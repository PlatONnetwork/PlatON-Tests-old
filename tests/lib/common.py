from environment.env import TestEnvironment
from environment.node import Node
from .config import StakingConfig, PipConfig
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
        if node_id is None:
            node_id = self.node.node_id
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.editCandidate(benifit_address, node_id, self.cfg.external_id, self.cfg.node_name, self.cfg.website, self.cfg.details,
                                       pri_key, transaction_cfg=transaction_cfg)

    def increase_staking(self, typ, from_address, node_id=None, amount=None, transaction_cfg=None):
        if node_id is None:
            node_id = self.node.node_id
        if amount is None:
            amount = self.economic.add_staking_limit
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.increaseStaking(typ, node_id, amount, pri_key, transaction_cfg=transaction_cfg)

    def withdrew_staking(self, from_address, node_id=None, transaction_cfg=None):
        if node_id is None:
            node_id = self.node.node_id
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.withdrewStaking(node_id, pri_key, transaction_cfg=transaction_cfg)


class Delegate:
    def __init__(self, env: TestEnvironment, node: Node):
        self.node = node
        self.economic = Economic(env)

    @property
    def ppos(self):
        return self.node.ppos

    def delegate(self, typ, from_address, node_id=None, amount=None, tansaction_cfg=None):
        if node_id is None:
            node_id = self.node.node_id
        if amount is None:
            amount = self.economic.delegate_limit
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.delegate(typ, node_id, amount, pri_key, transaction_cfg=tansaction_cfg)

    def withdrew_delegate(self, staking_blocknum, from_address, node_id=None, amount=None, transaction_cfg=None):
        if node_id is None:
            node_id = self.node.node_id
        if amount is None:
            amount = self.economic.delegate_limit
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.withdrewDelegate(staking_blocknum, node_id, amount, pri_key, transaction_cfg)


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


class DuplicateSign:
    def __init__(self, env: TestEnvironment, node: Node):
        self.node = node
        self.economic = Economic(env)

    def reportDuplicateSign(self, typ, data, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.reportDuplicateSign(typ, data, pri_key, transaction_cfg)

    @property
    def ppos(self):
        return self.node.ppos


class Restricting:
    def __init__(self, env: TestEnvironment, node: Node):
        self.node = node
        self.economic = Economic(env)

    def createRestrictingPlan(self, account, plan, from_address, transaction_cfg=None):
        pri_key = self.economic.account.find_pri_key(from_address)
        return self.ppos.createRestrictingPlan(account, plan, pri_key, transaction_cfg)

    @property
    def ppos(self):
        return self.node.ppos
