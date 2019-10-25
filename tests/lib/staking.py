from environment.env import TestEnvironment
from environment.node import Node
from .config import StakingConfig
from .economic import Economic


class Staking:
    def __init__(self, env: TestEnvironment, node: Node, cfg: StakingConfig):
        self.cfg = cfg
        self.node = node
        self.economic = Economic(env)

    @property
    def ppos(self):
        return self.node.ppos

    def create_staking(self, typ, benifit_address, from_address, node_id=None, amount=None, program_version=None,
                       program_version_sign=None, bls_pubkey=None, bls_proof=None, transaction_cfg=None):
        """
        创建质押
        :param typ: 
        :param benifit_address: 
        :param from_address: 
        :param node_id: 
        :param amount: 
        :param program_version: 
        :param program_version_sign: 
        :param bls_pubkey: 
        :param bls_proof: 
        :param transaction_cfg: 
        :return: 
        """
        if node_id is None:
            node_id = self.node.node_id
        if amount is None:
            amount = self.economic.create_staking_limit
        if program_version is None:
            program_version = self.node.program_version
        if program_version_sign is None:
            program_version_sign = self.node.program_version_sign
        if bls_pubkey is None:
            bls_pubkey = self.node.blspubkey
        if bls_proof is None:
            bls_proof = self.node.schnorr_NIZK_prove
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.createStaking(typ, benifit_address, node_id, self.cfg.external_id, self.cfg.node_name,
                                       self.cfg.website, self.cfg.details, amount, program_version, program_version_sign,
                                       bls_pubkey, bls_proof, pri_key, transaction_cfg=transaction_cfg)

    def edit_candidate(self, from_address, benifit_address, node_id=None, transaction_cfg=None):
        """
        编辑
        """
        if node_id is None:
            node_id = self.node.node_id
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.editCandidate(benifit_address, node_id, self.cfg.external_id, self.cfg.node_name, self.cfg.website, self.cfg.details,
                                       pri_key, transaction_cfg=transaction_cfg)

    def increase_staking(self, typ, from_address, node_id=None, amount=None, transaction_cfg=None):
        """
        增持
        """
        if node_id is None:
            node_id = self.node.node_id
        if amount is None:
            amount = self.economic.add_staking_limit
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.increaseStaking(typ, node_id, amount, pri_key, transaction_cfg=transaction_cfg)

    def withdrew_staking(self, from_address, node_id=None, transaction_cfg=None):
        """
        解除质押
        transaction_cfg: 交易配置 
         type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        """
        if node_id is None:
            node_id = self.node.node_id
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.withdrewStaking(node_id, pri_key, transaction_cfg=transaction_cfg)

    def get_staking_address(self):
        """
        获取质押钱包地址
        :return:
        """
        result = self.ppos.getCandidateInfo(self.node.node_id)
        candidate_info = result.get('Data')
        address = candidate_info.get('StakingAddress')
        return self.node.web3.toChecksumAddress(address)

    def get_candidate_list_not_verifier(self):
        """
        获取当前结算周期非验证人的候选人列表
        :return:
        """
        candidate_list = self.ppos.getCandidateList().get('Data')
        verifier_list = self.ppos.getVerifierList().get('Data')
        candidate_no_verify_list = []
        verifier_node_list = [node_info.get("NodeId") for node_info in verifier_list]
        for node_info in candidate_list:
            node_id = node_info.get("NodeId")
            if node_id not in verifier_node_list:
                candidate_no_verify_list.append(node_id)
        return candidate_no_verify_list

    def get_staking_amount(self, node=None, flag=0):
        """
        根据节点获取质押金额
        :param node:
        :param flag:
        :return:
        """
        if node is None:
            node = self.node
        flag = int(flag)
        stakinginfo = node.ppos.getCandidateInfo(node.node_id)
        staking_data = stakinginfo.get('Data')
        shares = int(staking_data.get('Shares'))
        released = int(staking_data.get('Released'))
        restrictingplan = int(staking_data.get('RestrictingPlan'))
        return [shares, released, restrictingplan][flag]
