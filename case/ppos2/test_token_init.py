# -*- coding: utf-8 -*-

import time
import random

import allure
import pytest
import threading
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common.load_file import get_node_list
from common import log
from deploy.deploy import AutoDeployPlaton
from common.connect import connect_web3
from utils.platon_lib.ppos_common import CommonMethod


class TestDposinit:
    address = conf.ADDRESS
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_TEST_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    base_gas_price = 60000000000000
    base_gas = 21000
    staking_gas = base_gas + 32000 + 6000 + 100000
    transfer_gasPrice = Web3.toWei (1, 'ether')
    transfer_gas = 210000000
    value = 1000
    chainid = 120
    ConsensusSize = 150
    time_interval = 10
    initial_amount = {'FOUNDATION': 905000000000000000000000000,
                      'FOUNDATIONLOCKUP': 20000000000000000000000000,
                      'STAKING': 25000000000000000000000000,
                      'INCENTIVEPOOL': 45000000000000000000000000,
                      'DEVELOPERS': 5000000000000000000000000
                      }

    def start_init(self):
        # 修改config参数
        CommonMethod.update_config (self, 'EconomicModel', 'Common', 'ExpectedMinutes', 3)
        CommonMethod.update_config (self, 'EconomicModel', 'Common', 'PerRoundBlocks', 5)
        CommonMethod.update_config (self, 'EconomicModel', 'Common', 'ValidatorCount', 10)
        CommonMethod.update_config (self, 'EconomicModel', 'Staking', 'ElectionDistance', 10)
        CommonMethod.update_config (self, 'EconomicModel', 'Staking', 'StakeThreshold', 1000)
        # 启动节点
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)

    def test_init_token(self):
        '''
        验证链初始化后token各内置账户初始值
        :return:
        '''
        url = CommonMethod.link_list(self)
        platon_ppos = Ppos(url,self.address,self.chainid)
        FOUNDATION = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONADDRESS))
        FOUNDATIONLOCKUP = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONLOCKUPADDRESS))
        STAKING = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.STAKINGADDRESS))
        INCENTIVEPOOL = platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
        DEVELOPERS = platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.DEVELOPERSADDRESS))
        token_init_total = conf.TOKENTOTAL
        if self.initial_amount['FOUNDATION'] != FOUNDATION:
            log.info("基金会初始金额:{}有误".format(FOUNDATION))
        elif self.initial_amount['FOUNDATIONLOCKUP'] != FOUNDATIONLOCKUP:
            log.info("基金会锁仓初始金额:{}有误".format(FOUNDATIONLOCKUP))
        elif self.initial_amount['STAKING'] != STAKING:
            log.info("质押账户初始金额:{}有误".format(STAKING))
        elif self.initial_amount['INCENTIVEPOOL'] != INCENTIVEPOOL:
            log.info("奖励池初始金额:{}有误".format(INCENTIVEPOOL))
        elif self.initial_amount['DEVELOPERS'] != DEVELOPERS:
            log.info("预留账户初始金额:{}有误".format(DEVELOPERS))
        reality_total = FOUNDATION + FOUNDATIONLOCKUP + STAKING + INCENTIVEPOOL + DEVELOPERS
        assert token_init_total == (reality_total),"初始化发行值{}有误".format(reality_total)

    def test_transfer_normal(self):
        '''
        验证初始化之后账户之间转账
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)
        balance = platon_ppos.eth.getBalance(address1)
        log.info("转账金额{}".format(balance))
        assert Web3.toWei(self.value,'ether') == balance,"转账金额:{}失败".format(balance)


    def test_fee_income(self):
        '''
        1、验证初始化之后普通账户转账内置账户
        2、验证初始内置账户没有基金会Staking奖励和出块奖励只有手续费收益
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        incentive_pool_balance_befor = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info('交易前激励池查询余额：{}'.format(incentive_pool_balance_befor))
        address1, private_key1 = CommonMethod.read_private_key_list ()
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)
        incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info('交易后激励池查询余额：{}'.format(incentive_pool_balance_after))
        difference = incentive_pool_balance_after - incentive_pool_balance_befor
        log.info('手续费的金额：{}'.format(difference))
        assert difference == 1260000000000000000,"手续费{}有误".format(difference)


    def test_punishment_income(self):
        '''
        验证低出块率验证节点的处罚金自动转账到激励池
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        incentive_pool_balance_befor = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info ('处罚之前激励池查询余额：{}'.format (incentive_pool_balance_befor))

        #获取节点内置质押节点信息
        nodeId = CommonMethod.read_out_nodeId(self,'collusion')
        log.info("节点ID：{}".format(nodeId))
        con_node, no_node = get_node_list (self.node_yml_path)
        nodes = con_node + no_node
        for node in nodes:
            if nodeId in node.values ():
                node_data = node

        #获取节点质押金额
        punishment_CandidateInfo = platon_ppos.getCandidateInfo (nodeId)
        assert punishment_CandidateInfo['Status'] == True, "查询锁仓信息失败"
        pledge_amount1 = punishment_CandidateInfo['Data']['Released']
        log.info("质押节点质押金：{}".format(pledge_amount1))

        # 停止其中一个正在出块的节点信息
        self.auto = AutoDeployPlaton ()
        self.auto.kill (node_data)
        platon_ppos1 = connect_web3 (node_data['url'])
        assert not platon_ppos1.isConnected (), "节点：{} 连接异常".format (node_data['host'])
        CommonMethod.get_next_settlement_interval(self)
        punishment_CandidateInfo = platon_ppos.getCandidateInfo (nodeId)
        pledge_amount3 = punishment_CandidateInfo['Data']['Released']
        log.info ("节点低出块率后节点质押金：{}".format (pledge_amount3))
        incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info ('处罚之后激励池查询余额：{}'.format (incentive_pool_balance_after))
        assert incentive_pool_balance_after == incentive_pool_balance_befor + (pledge_amount1 - pledge_amount3)












if __name__ == "__main__":
    a = TestDposinit()
    a.start_init()
    #a.test_init_token()
    a.test_punishment_income()