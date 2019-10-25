from environment.env import TestEnvironment
from environment.node import Node
from .economic import Economic


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