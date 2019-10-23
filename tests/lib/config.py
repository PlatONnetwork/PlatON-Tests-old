import math
import time
import os
from conf.settings import BASE_DIR
from common.key import get_pub_key
from .utils import wait_block_number

class PposConfig:
    external_id = None
    node_name = None
    website = None
    details = None

    def __init__(self, external_id, node_name, website, details):
        self.external_id = external_id
        self.node_name = node_name
        self.website = website
        self.details = details


class PipConfig:
    PLATON_NEW_BIN = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/platon"))
    PLATON_NEW_BIN1 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version1/platon"))
    PLATON_NEW_BIN2 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version2/platon"))
    PLATON_NEW_BIN3 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version3/platon"))
    PLATON_NEW_BIN4 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version4/platon"))
    PLATON_NEW_BIN8 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version8/platon"))
    PLATON_NEW_BIN9 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version9/platon"))
    PLATON_NEW_BIN6 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version6/platon"))
    PLATON_NEW_BIN7 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version7/platon"))
    PLATON_NEW_BIN0 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/platon"))
    PLATON_NEW_BIN120 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/diffcodeversion/platon"))


class CommonConfig:
    RELEASE_ZERO = 62215742.48691650
    TOKEN_TOTAL = 10250000000000000000000000000
    FOUNDATION_ADDRESS = "0x493301712671ada506ba6ca7891f436d29185821"
    # 锁仓合约账户地址
    FOUNDATION_LOCKUP_ADDRESS = "0x1000000000000000000000000000000000000001"
    # 质押合约地址
    STAKING_ADDRESS = "0x1000000000000000000000000000000000000002"
    # platON激励池账户
    INCENTIVEPOOL_ADDRESS = "0x1000000000000000000000000000000000000003"
    # 剩余总账户
    REMAIN_ACCOUNT_ADDRESS = "0x2e95e3ce0a54951eb9a99152a6d5827872dfb4fd"
    # 开发者基金会账户
    DEVELOPER_FOUNDATAION_ADDRESS = '0x60ceca9c1290ee56b98d4e160ef0453f7c40d219'
    init_token_info = {FOUNDATION_LOCKUP_ADDRESS: 259096240418673500000000000,
                       STAKING_ADDRESS: 40000000000000000000000000,
                       INCENTIVEPOOL_ADDRESS: 262215742486916500000000000,
                       FOUNDATION_ADDRESS: 1638688017094410000000000000,
                       REMAIN_ACCOUNT_ADDRESS: 8000000000000000000000000000,
                       DEVELOPER_FOUNDATAION_ADDRESS: 50000000000000000000000000
                       }
    release_info = [{"blockNumber": 1600, "amount": 55965742486916500000000000},
                    {"blockNumber": 3200, "amount": 49559492486916500000000000},
                    {"blockNumber": 4800, "amount": 42993086236916500000000000},
                    {"blockNumber": 6400, "amount": 36262519830666600000000000},
                    {"blockNumber": 8000, "amount": 29363689264263300000000000},
                    {"blockNumber": 9600, "amount": 22292387933693900000000000},
                    {"blockNumber": 11200, "amount": 15044304069863300000000000},
                    {"blockNumber": 12800, "amount": 7615018109436900000000000}
                    ]

    def __init__(self, genesis_data):
        self.genesis_data = genesis_data
        self.additional_cycle_time = self.genesis_data['EconomicModel']['Common']['AdditionalCycleTime']
        self.expected_minutes = self.genesis_data['EconomicModel']['Common']['ExpectedMinutes']
        self.perround_blocks = self.genesis_data['config']['cbft']['amount']
        self.interval = int((self.genesis_data['config']['cbft']['period'] / self.perround_blocks) / 1000)
        self.validator_count = self.genesis_data['EconomicModel']['Common']['ValidatorCount']
        self.consensus_wheel = (self.expected_minutes * 60) // (self.interval * self.perround_blocks * self.validator_count)
        self.settlement_size = self.consensus_wheel * (self.interval * self.perround_blocks * self.validator_count)
        self.consensussize = self.interval * self.perround_blocks * self.validator_count
        self.create_staking_limit = self.genesis_data["EconomicModel"]["Staking"]["StakeThreshold"]
        self.add_staking_limit = self.genesis_data["EconomicModel"]["Staking"]["MinimumThreshold"]
        self.delegate_limit = self.add_staking_limit
        self.consensus_block = self.interval * self.perround_blocks * self.validator_count

    def get_block_count_number(self, node, roundnum=1):
        """
        获取验证节点出块数
        """
        current_block = node.eth.blockNumber
        block_namber = self.consensussize * roundnum
        count = 0
        for i in range(block_namber - 1):
            node_id = get_pub_key(node.url, current_block)
            current_block = current_block - 1
            if node_id == node.node_id:
                count = count + 1
        return count

    def get_current_year_reward(self, node):
        """
        获取首年奖励
        :return:
        """
        annualcycle, annual_size, current_end_block = self.get_annual_switchpoint(node.web3)
        verifier_list = node.ppos.getVerifierList()
        count = len(verifier_list['Data'])
        block_reward = node.web3.fromWei(self.init_token_info[self.INCENTIVEPOOL_ADDRESS], 'ether') / 2 / annual_size
        block_reward = node.web3.toWei(block_reward, 'ether')
        staking_reward = node.web3.fromWei(self.init_token_info[self.INCENTIVEPOOL_ADDRESS], 'ether') / 2 / annualcycle / count
        staking_reward = node.web3.toWei(staking_reward, 'ether')
        return block_reward, staking_reward

    def get_settlement_switchpoint(self, node, number=0):
        """
        获取当前结算周期最后一块高
        :param node: w3链接
        :param number: 结算周期数
        :return:
        """
        block_namber = self.settlement_size * number
        tmp_current_block = node.eth.blockNumber
        current_end_block = math.ceil(tmp_current_block / self.settlement_size) * self.settlement_size + block_namber
        return current_end_block

    def get_front_settlement_switchpoint(self, node, number=0):
        """
        获取当前结算周期前一个块高
        :param node: w3链接
        :param number: 结算周期数
        :return:
        """
        block_num = self.settlement_size * (number + 1)
        current_end_block = self.get_settlement_switchpoint(node)
        history_block = current_end_block - block_num
        return history_block

    def wait_settlement_blocknum(self, node, number=0):
        """
        等待当个结算周期结算
        :param node:
        :param number: 结算周期数
        :return:
        """
        end_block = self.get_settlement_switchpoint(node, number)
        wait_block_number(node, end_block, self.interval)

    def get_annual_switchpoint(self, node):
        """
        获取年度结算周期数
        :return:
        """
        annual_cycle = (self.additional_cycle_time * 60) // (self.settlement_size * self.interval)
        annualsize = annual_cycle * self.settlement_size
        current_block = node.eth.blockNumber
        current_end_block = math.ceil(current_block / annualsize) * annualsize
        return annual_cycle, annualsize, current_end_block

    def wait_annual_blocknum(self, node):
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

    def wait_consensus_blocknum(self, node, number=0):
        """
        等待当个共识轮块高结束
        :param node:
        :param number:
        :return:
        """
        end_block = self.get_consensus_switchpoint(node, number)
        wait_block_number(node, end_block, self.interval)

    def get_consensus_switchpoint(self, node, number=0):
        """
        获取指定共识轮块高
        :param node:
        :param number:
        :return:
        """
        block_namber = self.consensussize * number
        current_block = node.eth.blockNumber
        current_end_block = math.ceil(current_block / self.consensussize) * self.consensussize + block_namber
        return current_end_block
