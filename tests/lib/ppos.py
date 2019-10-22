from environment.env import TestEnvironment
from environment.node import Node
from environment.account import Account
from .config import PposConfig


class Ppos(Account):
    def __init__(self, env: TestEnvironment, cfg: PposConfig, node: Node):
        super().__init__(accountFile=env.cfg.account_file, chainId=env.chain_id)
        self.env = env
        self.cfg = cfg
        self.node = node
        self.accounts = env.account.accounts

    @property
    def ppos(self):
        return ""

    def create_staking(self, typ, benifit_address, from_address, amount=None, program_version=None,
                       program_version_sign=None, bls_pubkey=None, bls_proof=None, transaction_cfg=None):
        pass

    def edit_candidate(self, from_address, benifit_address=None, node_id=None, external_id=None,
                       node_name=None, website=None, details=None, transaction_cfg=None):
        pass

    def increase_staking(self, typ, from_address, node_id=None, amount=None, transaction_cfg=None):
        pass

    def withdrew_staking(self, from_address, node_id=None, transaction_cfg=None):
        pass