from environment.env import TestEnvironment
from environment.node import Node
from .config import PipConfig
from .economic import Economic
from .utils import int_to_bytes, get_blockhash


class Pip:
    def __init__(self, env: TestEnvironment, node: Node, cfg: PipConfig):
        self.cfg = cfg
        self.node = node
        self.economic = Economic(env)

    def submitText(self, verifier, pip_id, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.pip.submitText(verifier, pip_id, pri_key, transaction_cfg)

    def submitVersion(self, verifier, pip_id, new_version, end_voting_rounds, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.pip.submitVersion(verifier, pip_id, new_version, end_voting_rounds, pri_key, transaction_cfg)

    def submitParam(self, verifier, url, end_voting_block, param_name, current_value, new_value, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.pip.submitParam(verifier, url, end_voting_block, param_name, current_value, new_value, pri_key, transaction_cfg)

    def submitCancel(self, verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.pip.submitCancel(verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, pri_key, transaction_cfg)

    def vote(self, verifier, proposal_id, option, from_address, program_version=None, version_sign=None, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        if program_version is None:
            program_version = self.node.program_version
        if version_sign is None:
            version_sign = self.node.program_version_sign
        return self.pip.vote(verifier, proposal_id, option, program_version, version_sign, pri_key, transaction_cfg)

    def declareVersion(self, active_node, from_address, program_version=None, version_sign=None, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        if program_version is None:
            program_version = self.node.program_version
        if version_sign is None:
            version_sign = self.node.program_version_sign
        return self.pip.declareVersion(active_node, program_version, version_sign, pri_key, transaction_cfg)

    @property
    def pip(self):
        return self.node.pip

    def get_status_of_proposal(self, proposal_id):
        """
        获取提案投票结果
        :param proposal_id: 
        :return: 
        """
        result = self.pip.getTallyResult(proposal_id)
        data = result.get('Data')
        if not data:
            raise Exception('根据给定的提案id查询提案结果失败')
        return data.get('status')

    def get_accu_verifiers_of_proposal(self, proposal_id):
        """
        获取在整个投票期内有投票资格的验证人总数
        :param proposal_id: 
        :return: 
        """
        result = self.pip.getTallyResult(proposal_id)
        resultinfo = result.get('Data')
        if not resultinfo:
            raise Exception('根据给定的提案id查询提案结果失败')
        return resultinfo.get('accuVerifiers')

    def get_yeas_of_proposal(self, proposal_id):
        """
        获取在整个投票期内有投赞成票人数
        :param proposal_id: 
        :return: 
        """
        result = self.pip.getTallyResult(proposal_id)
        data = result.get('Data')
        if not data:
            raise Exception('根据给定的提案id查询提案结果失败')
        return data.get('yeas')

    def get_nays_of_proposal(self, proposal_id):
        """
        获取在整个投票期内有投反对票人数
        :param proposal_id:
        :return:
        """
        result = self.pip.getTallyResult(proposal_id)
        data = result.get('Data')
        if not data:
            raise Exception('根据给定的提案id查询提案结果失败')
        return data.get('nays')

    def get_abstentions_of_proposal(self, proposal_id):
        """
        获取在整个投票期内有投弃权票人数
        :param proposal_id:
        :return:
        """
        result = self.pip.getTallyResult(proposal_id)
        data = result.get('Data')
        if not data:
            raise Exception('根据给定的提案id查询提案结果失败')
        return data.get('abstentions')

    @property
    def chain_version(self):
        """
        获取链上版本号
        :return:
        """
        result = self.pip.getActiveVersion()
        return result.get('Data')

    def get_version_small_version(self, flag=3):
        """
        判断传入版本号的小版本是否为0
        :param flag:
        :return:
        """
        flag = int(flag)
        if flag > 3 or flag < 1:
            raise Exception("传入参数有误")
        version = int(self.chain_version)
        version_byte = int_to_bytes(version)
        return version_byte[flag]

    def get_accuverifiers_count(self, proposal_id, blocknumber=None):
        """
        获取提案实时投票数
        :param proposal_id:
        :param blocknumber:
        :return:
        """
        if blocknumber is None:
            blocknumber = self.node.block_number
        blockhash = get_blockhash(self.node, blocknumber)
        result = self.pip.getAccuVerifiersCount(proposal_id, blockhash)
        voteinfo = result.get('Data')
        vote_result = eval(voteinfo)
        return vote_result

    def get_rate_of_voting(self, proposal_id):
        """
        计算升级提案投票率
        :param proposal_id:
        :return:
        """
        result = self.pip.getTallyResult(proposal_id).get('Data')
        if not result:
            raise Exception('根据给定的提案id查询提案结果失败')
        yeas = result.get('yeas')
        accu_verifiers = result.get('accuVerifiers')
        return yeas / accu_verifiers
