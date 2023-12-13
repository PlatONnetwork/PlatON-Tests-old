from tests.lib.utils import *
import rlp
import pytest
from client_sdk_python.packages.platon_account.internal.transactions import bech32_address_bytes


@pytest.mark.P3
def test_staking_gas(client_new_node):
    client_new_node.ppos.need_quota_gas = False
    external_id = "external_id"
    node_name = "node_name"
    website = "website"
    details = "details"
    node = client_new_node.node
    economic = client_new_node.economic
    benifit_address1, pri_key = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    balance1 = node.eth.getBalance(benifit_address1)
    log.info(balance1)
    if node.program_version_sign[:2] == '0x':
        program_version_sign = node.program_version_sign[2:]

    # program_version_sign_ = node.program_version_sign[2:]
    benifit_address = bech32_address_bytes(benifit_address1)

    data = HexBytes(rlp.encode([rlp.encode(int(1000)), rlp.encode(0), rlp.encode(benifit_address),
                                rlp.encode(bytes.fromhex(node.node_id)), rlp.encode(external_id), rlp.encode(node_name),
                                rlp.encode(website), rlp.encode(details),
                                rlp.encode(economic.create_staking_limit), rlp.encode(600), rlp.encode(node.program_version),
                                rlp.encode(bytes.fromhex(program_version_sign)), rlp.encode(bytes.fromhex(node.blspubkey)),
                                rlp.encode(bytes.fromhex(node.schnorr_NIZK_prove))]))
    esgas = node.eth.estimateGas({"from": benifit_address1, "to": node.ppos.stakingAddress, "data": data})
    print('esgas', esgas)
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 32000
    log.info('gas: {}'.format(gas))

    result = client_new_node.ppos.createStaking(0, benifit_address1, node.node_id, external_id,
                                                node_name, website,
                                                details, economic.create_staking_limit,
                                                node.program_version, node.program_version_sign, node.blspubkey,
                                                node.schnorr_NIZK_prove,
                                                pri_key, reward_per=600)

    assert_code(result, 0)
    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    result = client_new_node.ppos.createStaking(0, benifit_address1, node.node_id, external_id,
                                                node_name, website,
                                                details, economic.create_staking_limit,
                                                node.program_version, node.program_version_sign, node.blspubkey,
                                                node.schnorr_NIZK_prove,
                                                pri_key, reward_per = 600)
    assert_code(result, 0)
    time.sleep(2)
    balance2 = node.eth.getBalance(benifit_address1)
    log.info(balance2)
    assert esgas == gas
    assert (balance1 - economic.create_staking_limit) - gas * gasPrice == balance2


@pytest.mark.P3
def test_delegate_gas(client_new_node):
    client = client_new_node
    node = client.node
    economic = client.economic
    staking_address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    address, pri_key = economic.account.generate_account(node.web3, economic.delegate_limit * 10)

    result = client.staking.create_staking(0, staking_address, staking_address)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(address)
    log.info(balance1)
    result = client.delegate.delegate(0, address)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(address)
    log.info(balance2)
    data = rlp.encode([rlp.encode(int(1004)), rlp.encode(0), rlp.encode(bytes.fromhex(node.node_id)),
                       rlp.encode(economic.delegate_limit)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 16000
    log.info(gas)
    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    assert balance1 - economic.delegate_limit - gas * gasPrice == balance2


@pytest.mark.P3
def test_withdrewDelegate_gas(client_new_node):
    client = client_new_node
    node = client.node
    economic = client.economic
    staking_address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    address, pri_key = economic.account.generate_account(node.web3, economic.delegate_limit * 10)

    result = client.staking.create_staking(0, staking_address, staking_address)
    assert_code(result, 0)
    result = client.delegate.delegate(0, address)
    assert_code(result, 0)
    msg = client.ppos.getCandidateInfo(client_new_node.node.node_id)
    staking_blocknum = msg["Ret"]["StakingBlockNum"]
    balance1 = node.eth.getBalance(address)
    log.info(balance1)
    result = client.delegate.withdrew_delegate(staking_blocknum, address)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(address)
    log.info(balance2)

    data = rlp.encode(
        [rlp.encode(int(1005)), rlp.encode(staking_blocknum), rlp.encode(bytes.fromhex(node.node_id)),
         rlp.encode(economic.delegate_limit)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 8000
    log.info(gas)
    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    assert balance1 - gas * gasPrice == balance2 - economic.delegate_limit


@pytest.mark.P3
def test_increase_staking_gas(client_new_node):
    client = client_new_node
    node = client.node
    economic = client.economic
    staking_address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)

    result = client.staking.create_staking(0, staking_address, staking_address)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(staking_address)
    log.info(balance1)
    result = client.staking.increase_staking(0, staking_address)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(staking_address)
    log.info(balance2)
    data = rlp.encode(
        [rlp.encode(int(1002)), rlp.encode(bytes.fromhex(node.node_id)), rlp.encode(0),
         rlp.encode(economic.add_staking_limit)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 20000
    log.info(gas)
    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    assert balance1 - economic.delegate_limit - gas * gasPrice == balance2


@pytest.mark.P3
def test_edit_candidate_gas(client_new_node):
    external_id = "external_id"
    node_name = "node_name"
    website = "website"
    details = "details"
    reward_per = 0
    client = client_new_node
    node = client.node
    economic = client.economic
    client.ppos.need_quota_gas = False
    benifit_address, pri_key = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    result = client.staking.create_staking(0, benifit_address, benifit_address)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(benifit_address)
    log.info(balance1)
    result = client.ppos.editCandidate(benifit_address, node.node_id, external_id, node_name, website, details,
                                       pri_key, reward_per=reward_per)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(benifit_address)
    log.info(balance2)
    rlp_benifit_address = rlp.encode(bech32_address_bytes(benifit_address)) #if benifit_address else b''
    rlp_external_id = rlp.encode(external_id) #if external_id else b''
    rlp_node_name = rlp.encode(node_name) #if node_name else b''
    rlp_website = rlp.encode(website) #if website else b''
    rlp_details = rlp.encode(details) #if details else b''
    rlp_reward_per = rlp.encode(reward_per) if reward_per else b''
    data = HexBytes(rlp.encode([rlp.encode(int(1001)), rlp_benifit_address, rlp.encode(bytes.fromhex(node.node_id)), rlp_reward_per, rlp_external_id,
                                rlp_node_name, rlp_website, rlp_details]))
    estimated_gas = node.eth.estimateGas({"from": benifit_address, "to": node.ppos.stakingAddress, "data": data})
    print(estimated_gas)
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 12000
    log.info(gas)

    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    assert balance1 - gas * gasPrice == balance2


@pytest.mark.P3
def test_withdrew_staking_gas(client_new_node):
    client = client_new_node
    node = client.node
    economic = client.economic
    staking_address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)

    result = client.staking.create_staking(0, staking_address, staking_address)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(staking_address)
    log.info(balance1)
    result = client.staking.withdrew_staking(staking_address)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(staking_address)
    log.info(balance2)
    data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node.node_id))])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 20000
    log.info(gas)
    gasPrice = node.eth.gasPrice
    log.info(gasPrice)
    assert balance1 - gas * gasPrice == balance2 - economic.create_staking_limit
