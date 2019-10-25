from environment.env import TestEnvironment
from environment.node import Node
from .economic import Economic


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