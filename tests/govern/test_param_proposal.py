import time
import pytest
from typing import List
from tests.ppos.slashing.test_general_punishment import verify_low_block_rate_penalty, get_out_block_penalty_parameters
from common.log import log
from tests.lib import check_node_in_list, wait_block_number, assert_code
from tests.lib.client import Client
from tests.lib.config import PipConfig


@pytest.fixture()
def verifiers(clients_consensus, new_genesis_env):
    yield clients_consensus


def get_pips(clients: List[Client]):
    return [c.pip for c in clients]


def version_proposal(pip, to_version, voting_rounds):
    result = pip.submitVersion(pip.node.node_id, str(time.time()), to_version, voting_rounds,
                               pip.node.staking_address,
                               transaction_cfg=pip.cfg.transaction_cfg)
    log.info('submit version proposal result : {}'.format(result))
    return result
    # return get_proposal_result(pip, pip.cfg.version_proposal, result)


def param_proposal(pip, module, name, value):
    result = pip.submitParam(pip.node.node_id, str(time.time()), module, name, value, pip.node.staking_address,
                             transaction_cfg=pip.cfg.transaction_cfg)
    log.info('submit param proposal result : {}'.format(result))
    return result
    # return get_proposal_result(pip, pip.cfg.param_proposal, result)


def text_proposal(pip):
    result = pip.submitText(pip.node.node_id, str(time.time()), pip.node.staking_address,
                            transaction_cfg=pip.cfg.transaction_cfg)
    log.info('submit text proposal result:'.format(result))
    return result
    # return get_proposal_result(pip, pip.cfg.text_proposal, result)


def cancel_proposal(pip, pip_id, voting_rounds):
    result = pip.submitCancel(pip.node.node_id, str(time.time()), voting_rounds, pip_id,
                              pip.node.staking_address, transaction_cfg=pip.cfg.transaction_cfg)
    log.info('submit cancel proposal result : {}'.format(result))
    return result
    # return get_proposal_result(pip, pip.cfg.cancel_proposal, result)


def get_proposal_id(pip, proposal_type):
    pip_info = pip.get_effect_proposal_info_of_vote(proposal_type)
    log.info(f"proposal id is {pip_info['ProposalID']}")
    return pip_info['ProposalID']


def vote(pip, pip_id, vote_option=PipConfig.vote_option_yeas):
    result = pip.vote(pip.node.node_id, pip_id, vote_option,
                      pip.node.staking_address, transaction_cfg=pip.cfg.transaction_cfg)
    log.info(f'Node {pip.node.node_id} vote param proposal result {result}')
    return result.get('code')


def votes(pip_id, pips, vote_options):
    assert len(pips) == len(vote_options)
    for pip, vote_option in zip(pips, vote_options):
        assert vote(pip, pip_id, vote_option) == 0
    return True


def version_declare(pip):
    version = pip.node.program_version
    version_sign = pip.node.program_version_sign
    result = pip.declareVersion(pip.node.node_id, pip.node.staking_address, version, version_sign,
                                transaction_cfg=pip.cfg.transaction_cfg)
    log.info(f'Node {pip.node.node_id} declare version result {result}')
    return result


def wait_proposal_active(pip, pip_id):
    res = pip.pip.getProposal(pip_id)
    end_block = res['Ret']['EndVotingBlock']
    end_block = pip.economic.get_consensus_switchpoint(end_block)
    log.info(f'wait proposal active block : {end_block}')
    wait_block_number(pip.node, end_block)
    return


def make_0mb_slash(slash_client, check_client):
    """
    构造零出块处罚场景
    """
    slash_node = slash_client.node
    pledge_amount, block_reward, slash_blocks = get_out_block_penalty_parameters(slash_client, slash_node, 'Released')
    log.info(f'slashing param : pledge_amount ({pledge_amount}), block_reward ({block_reward}), slash_blocks ({slash_blocks})')
    log.info("make zero produce block")
    start_num, end_num = verify_low_block_rate_penalty(slash_client, check_client, block_reward, slash_blocks, pledge_amount, 'Released')
    log.info('check Verifier Lists')
    assert check_node_in_list(slash_node.node_id, check_client.ppos.getCandidateList) is False
    assert check_node_in_list(slash_node.node_id, check_client.ppos.getVerifierList) is False
    assert check_node_in_list(slash_node.node_id, check_client.ppos.getValidatorList) is False
    slash_client.node.start()
    return start_num, end_num


class TestParam:
    @pytest.mark.P0
    @pytest.mark.parametrize('value, code', [(501 * 10 ** 18, 0), (100000 * 10 ** 18, 0)])
    def test_param_of_minimumRelease(self, noproposal_pips, client_consensus, value, code):
        client = client_consensus
        pips = noproposal_pips
        pip = pips[0]
        # 提交提案并投票
        result = param_proposal(pip, 'restricting', 'minimumRelease', str(value))
        assert_code(result, code)
        pip_id = get_proposal_id(pip, pip.cfg.param_proposal)
        votes(pip_id, pips, [1, 1, 1, 1])
        # 验证参数生效
        wait_proposal_active(pip, pip_id)
        param_value = pip.pip.getGovernParamValue('restricting', 'minimumRelease')
        assert param_value.get('Code') == code
        assert param_value.get('Ret') == str(value)
        # 验证实际锁仓生效
        from_address, _ = client.economic.account.generate_account(client.node.web3, value + 1 * 10 ** 18)
        to_address = 'atx1c85wwztzpjefcvaev6wxpsrqp2gpfjyp6lmfqd'
        plan = [{'Epoch': 1, 'Amount': value}]
        result = client.restricting.createRestrictingPlan(to_address, plan, from_address)
        assert_code(result, 0)
        plan = [{'Epoch': 1, 'Amount': value - 1}]
        result = client.restricting.createRestrictingPlan(to_address, plan, from_address)
        assert_code(result, 304014)

    @pytest.mark.P0
    @pytest.mark.parametrize('value, code',
                             [(str(500 * 10 ** 18), 302034), (100 * 10 ** 18, 3), (str(99 * 10 ** 18), 3), (str(10000001 * 10 ** 18), 3),
                              (str(100001 * 10 ** 18), 0), (str(80 * 10 ** 18), 3), (str(81 * 10 ** 18), 3)])
    def test_invalid_param_of_minimumRelease(self, noproposal_pips, value, code):
        pips = noproposal_pips
        pip = pips[0]
        result = param_proposal(pip, 'restricting', 'minimumRelease', value)
        assert_code(result, code)

    @pytest.mark.P2
    @pytest.mark.skip
    def test_init_value_of_minimumRelease(self, noproposal_pips):
        pips = noproposal_pips
        pip = pips[0]
        result = pip.node.debug.economicConfig()
        assert result.get('restricting').get('minimumRelease') == str(80 * 10 ** 18)

    def test_govern_minimumRelease_after_restricted(self, client_consensus, noproposal_pips):
        client = client_consensus
        pips = noproposal_pips
        pip = pips[0]
        # 提案前创建锁仓
        from_address, _ = client.economic.account.generate_account(client.node.web3, pip.economic.create_staking_limit)
        to_address = 'atx1c85wwztzpjefcvaev6wxpsrqp2gpfjyp6lmfqd'
        plan = [{'Epoch': 1, 'Amount': pip.economic.delegate_limit * 80}, {'Epoch': 2, 'Amount': pip.economic.delegate_limit * 160},
                {'Epoch': 3, 'Amount': pip.economic.delegate_limit * 240}]
        result = client.restricting.createRestrictingPlan(to_address, plan, from_address)
        assert_code(result, 0)
        # 提案增加minimumRelease
        result = param_proposal(pip, 'restricting', 'minimumRelease', str(pip.economic.delegate_limit * 500))
        assert_code(result, 0)
        pip_id = get_proposal_id(pip, pip.cfg.param_proposal)
        # 提案后创建锁仓
        from_address, _ = client.economic.account.generate_account(client.node.web3, 241 * 10 ** 18)
        to_address = 'atx1gp3meyfrt7lp8tqtf7383n98ua3y7cqkxfphqr'
        plan = [{'Epoch': 1, 'Amount': 80 * 10 ** 18}, {'Epoch': 2, 'Amount': 160 * 10 ** 18}]
        result = client.restricting.createRestrictingPlan(to_address, plan, from_address)
        assert_code(result, 0)
        # 投票并等待提案生效
        votes(pip_id, pips, [1, 1, 1, 1])
        wait_proposal_active(pip, pip_id)
        param_value = pip.pip.getGovernParamValue('restricting', 'minimumRelease')
        assert param_value.get('Code') == 0
        assert param_value.get('Ret') == str(500 * 10 ** 18)
        # 验证锁仓释放金额是否正确
        pip.economic.wait_settlement(pip.node, 3)
        assert pip.node.eth.getBalance('atx1c85wwztzpjefcvaev6wxpsrqp2gpfjyp6lmfqd') == 480 * 10 ** 18
        assert pip.node.eth.getBalance('atx1gp3meyfrt7lp8tqtf7383n98ua3y7cqkxfphqr') == 240 * 10 ** 18
