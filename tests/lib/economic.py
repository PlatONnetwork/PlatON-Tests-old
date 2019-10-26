from decimal import Decimal

from dacite import from_dict
from .utils import wait_block_number
from environment.node import Node
from .genesis import Genesis
from common.key import get_pub_key
import math
from .config import DefaultEconomicConfig
from environment.env import TestEnvironment


class Economic:
    cfg = DefaultEconomicConfig

    def __init__(self, env: TestEnvironment):
        self.env = env

        self.genesis = from_dict(data_class=Genesis, data=self.env.genesis_config)

        # 出块速率参数
        self.per_round_blocks = self.genesis.config.cbft.amount
        self.interval = int((self.genesis.config.cbft.period / self.per_round_blocks) / 1000)

        # 增发周期时长
        self.additional_cycle_time = self.genesis.EconomicModel.Common.AdditionalCycleTime

        # 验证人数
        self.validator_count = self.genesis.EconomicModel.Common.ValidatorCount

        # 结算相关
        # 结算周期
        self.expected_minutes = self.genesis.EconomicModel.Common.ExpectedMinutes
        # 共识轮数
        self.consensus_wheel = (self.expected_minutes * 60) // (self.interval * self.per_round_blocks * self.validator_count)
        # 结算周期块数
        self.settlement_size = self.consensus_wheel * (self.interval * self.per_round_blocks * self.validator_count)
        # 共识轮块数
        self.consensus_size = self.interval * self.per_round_blocks * self.validator_count

        # 最低金额限制
        # 最低质押金额
        self.create_staking_limit = self.genesis.EconomicModel.Staking.StakeThreshold
        # 最低增持金额
        self.add_staking_limit = self.genesis.EconomicModel.Staking.MinimumThreshold
        # 最低委托金额
        self.delegate_limit = self.add_staking_limit

    @property
    def account(self):
        return self.env.account

    def get_block_count_number(self, node: Node, roundnum=1):
        """
        获取验证节点出块数
        """
        current_block = node.eth.blockNumber
        block_namber = self.consensus_size * roundnum
        count = 0
        for i in range(block_namber - 1):
            node_id = get_pub_key(node.url, current_block)
            current_block = current_block - 1
            if node_id == node.node_id:
                count = count + 1
        return count

    def get_current_year_reward(self, node: Node, verifier_num=None):
        """
        获取首年出块奖励，质押奖励
        :return:
        """
        new_block_rate = self.genesis.EconomicModel.Reward.NewBlockRate
        annualcycle, annual_size, current_end_block = self.get_annual_switchpoint(node)
        if verifier_num is None:
            verifier_list = node.ppos.getVerifierList()
            verifier_num = len(verifier_list['Data'])
        amount = node.eth.getBalance(self.cfg.INCENTIVEPOOL_ADDRESS, 0)
        block_proportion = str(new_block_rate / 100)
        staking_proportion = str(1 - new_block_rate / 100)
        block_reward = int(Decimal(str(amount)) * Decimal(str(block_proportion)) / Decimal(str(annualcycle)))
        staking_reward = int(
            Decimal(str(amount)) * Decimal(str(staking_proportion)) / Decimal(str(annualcycle)) / Decimal(str(verifier_num)))
        return block_reward, staking_reward

    def get_settlement_switchpoint(self, node: Node, number=0):
        """
        获取当前结算周期最后一块高
        :param node: 节点对象
        :param number: 结算周期数
        :return:
        """
        block_number = self.settlement_size * number
        tmp_current_block = node.eth.blockNumber
        current_end_block = math.ceil(tmp_current_block / self.settlement_size) * self.settlement_size + block_number
        return current_end_block

    def get_front_settlement_switchpoint(self, node: Node, number=0):
        """
        获取当前结算周期前一个块高
        :param node: 节点对象
        :param number: 结算周期数
        :return:
        """
        block_num = self.settlement_size * (number + 1)
        current_end_block = self.get_settlement_switchpoint(node)
        history_block = current_end_block - block_num
        return history_block

    def wait_settlement_blocknum(self, node: Node, number=0):
        """
        等待当个结算周期结算
        :param node:
        :param number: 结算周期数
        :return:
        """
        end_block = self.get_settlement_switchpoint(node, number)
        wait_block_number(node, end_block, self.interval)

    def get_annual_switchpoint(self, node: Node):
        """
        获取年度结算周期数
        :return:
        """
        annual_cycle = (self.additional_cycle_time * 60) // (self.settlement_size * self.interval)
        annualsize = annual_cycle * self.settlement_size
        current_block = node.eth.blockNumber
        current_end_block = math.ceil(current_block / annualsize) * annualsize
        return annual_cycle, annualsize, current_end_block

    def wait_annual_blocknum(self, node: Node):
        """
        等待当个年度块高结束
        :param node:
        :return:
        """
        annualcycle, annualsize, current_end_block = self.get_annual_switchpoint(node)
        current_block = node.eth.blockNumber
        differ_block = annualsize - (current_block % annualsize)
        annual_end_block = current_block + differ_block
        wait_block_number(node, annual_end_block, self.interval)

    def wait_consensus_blocknum(self, node: Node, number=0):
        """
        等待当个共识轮块高结束
        :param node:
        :param number:
        :return:
        """
        end_block = self.get_consensus_switchpoint(node, number)
        wait_block_number(node, end_block, self.interval)

    def get_consensus_switchpoint(self, node: Node, number=0):
        """
        获取指定共识轮块高
        :param node:
        :param number:
        :return:
        """
        block_number = self.consensus_size * number
        current_block = node.eth.blockNumber
        current_end_block = math.ceil(current_block / self.consensus_size) * self.consensus_size + block_number
        return current_end_block
