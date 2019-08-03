# -*- coding: utf-8 -*-

import time
import random

import allure
import pytest
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common.load_file import get_node_list
from common import log
from deploy.deploy import AutoDeployPlaton
from utils.platon_lib.ppos_common import CommonMethod


class TestDposinit:
    address = conf.ADDRESS
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_TEST_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    gasPrice = Web3.toWei(0.000000000000000001,'ether')
    gas = 21000
    transfer_gasPrice = Web3.toWei(1,'ether')
    transfer_gas = 210000000
    value = 1000
    initial_amount = {'FOUNDATION': 905000000000000000000000000,
                      'FOUNDATIONLOCKUP': 20000000000000000000000000,
                      'STAKING': 25000000000000000000000000,
                      'INCENTIVEPOOL': 45000000000000000000000000,
                      'DEVELOPERS': 5000000000000000000000000
                      }

    def test(self):
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)
        #print(self.nodeid_list)

    def test_init_token(self):
        '''
        验证链初始化后token各内置账户初始值
        :return:
        '''

        platon_ppos = CommonMethod.ppos_link()
        FOUNDATION = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONADDRESS))
        FOUNDATIONLOCKUP = self.platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONLOCKUPADDRESS))
        STAKING = self.platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.STAKINGADDRESS))
        INCENTIVEPOOL = self.platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
        DEVELOPERS = self.platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.DEVELOPERSADDRESS))
        token_init_total = conf.TOKENTOTAL
        if self.initial_amount['FOUNDATION'] != FOUNDATION:
            log.info("基金会初始金额:{}有误",format(FOUNDATION))
        elif self.initial_amount['FOUNDATIONLOCKUP'] == FOUNDATIONLOCKUP:
            log.info("基金会锁仓初始金额:{}".format(FOUNDATIONLOCKUP))
        elif self.initial_amount['STAKING'] == STAKING:
            log.info("质押账户初始金额:{}".format(STAKING))
        elif self.initial_amount['INCENTIVEPOOL'] == INCENTIVEPOOL:
            log.info("奖励池初始金额:{}".format(INCENTIVEPOOL))
        elif self.initial_amount['DEVELOPERS'] == DEVELOPERS:
            log.info("预留账户初始金额:{}".format(DEVELOPERS))
        assert token_init_total == (FOUNDATION + FOUNDATIONLOCKUP + STAKING + INCENTIVEPOOL + DEVELOPERS)

    def test_transfer_normal(self):
        '''
        验证初始化之后账户之间转账
        :return:
        '''
        platon_ppos = self.ppos_link ()
        address1,private_key1 = CommonMethod.read_private_key_list()

        try:
            platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                              Web3.toChecksumAddress (address1), self.gasPrice, self.gas, self.value,
                                              conf.PRIVATE_KEY)
            Balance1 = platon_ppos.eth.getBalance('address1')
            assert Web3.toWei(self.value,'ether') == Balance1
        except:
            status = 1
            assert status == 0, '账号余额不足，无法发起转账'

    def test_transfer_notsufficientfunds(self):
        '''
        账户余额不足的情况下进行转账
        :return:
        '''
        platon_ppos = self.ppos_link ()
        #账户1
        address1,private_key1 = CommonMethod.read_private_key_list()
        #账户2
        address2,private_key2 = CommonMethod.read_private_key_list()
        balance = platon_ppos.eth.getBalance(address1)
        if balance == 0:
            try:
                platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (address1),
                                                  Web3.toChecksumAddress (address2), self.gasPrice, self.gas, self.value,
                                                  private_key1)
            except:
                status = 1
                assert status == 0, '账号余额不足，无法发起转账'
        else:
            log.info('账号:{}已转账,请切换账号再试'.format(address1))

    def test_transfer_funds(self):
        '''
        验证初始化之后普通账户转账内置账户
        :return:
        '''
        platon_ppos = self.ppos_link ()
        lockup_balancebe_before = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        # 签名转账
        try:
            platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                              Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS), self.gasPrice, self.gas,                                                          self.value,conf.PRIVATE_KEY)
            lockup_balancebe_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
            assert lockup_balancebe_before + Web3.toWei(self.value,'ether') == lockup_balancebe_after
        except:
            status = 1
            assert status == 0, '无法发起转账'

    def test_Incentive_pool(self):
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                                                    privatekey=conf.PRIVATE_KEY)
        #platon_ppos = self.ppos_link ()
        lockupbalance = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info('激励池查询余额：{}'.format(lockupbalance))
        INCENTIVEPOOL = self.initial_amount['INCENTIVEPOOL']
        assert lockupbalance == INCENTIVEPOOL

    def test_fee_income(self):
        '''
        验证初始内置账户没有基金会Staking奖励和出块奖励只有手续费收益
        :return:
        '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        #platon_ppos = self.ppos_link ()
        incentive_pool_balance_befor = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info('交易前激励池查询余额：{}'.format(incentive_pool_balance_befor))
        # 签名转账
        address1,private_key1 = CommonMethod.read_private_key_list()

        try:
            platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                              Web3.toChecksumAddress (address1), self.gasPrice, self.gas, self.value,
                                              conf.PRIVATE_KEY)
            balance = platon_ppos.eth.getBalance (address1)
            if balance  == Web3.toWei (self.value, 'ether'):
                incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
                log.info('交易前激励池查询余额：{}'.format(incentive_pool_balance_after))
                difference = incentive_pool_balance_after - incentive_pool_balance_befor
                log.info('手续费的金额：{}'.format(difference))
                assert difference == self.gas
            else:
                log.info("转账{}金额错误".format(Web3.toWei (self.value, 'ether')))
        except:
            status = 1
            assert status == 0, '转账失败'

    def test_punishment_income(self):
        '''
        验证低出块率验证节点的处罚金自动转账到激励池
        :return:
        '''
        #随机获取其中一个正在出块的节点信息
        node_info = get_node_list (conf.TWENTY_FIVENODE_YML)
        node_info_length = len (node_info) - 1
        index = random.randint (0, node_info_length)
        node_data = node_info[0][index]
        print(node_data)
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()

        incentive_pool_balance_befor = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info ('处罚之前激励池查询余额：{}'.format (incentive_pool_balance_befor))
        #停止其中一个正在出块的节点信息
        try:
            self.auto = AutoDeployPlaton (cbft=self.cbft_json_path)
            self.auto.kill(node_data)
            platon_ppos = self.ppos_link (node_data['url'])
            if not platon_ppos.web3.isConnected():
                platon_ppos = self.ppos_link()
                current_block = platon_ppos.eth.blockNumber()
                waiting_time = 250 - (current_block % 250)
                time.sleep(waiting_time + 1)
                incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
                log.info ('处罚之后激励池查询余额：{}'.format (incentive_pool_balance_after))
                punishment_CandidateInfo=platon_ppos.getCandidateInfo(node_data['id'])
                if punishment_CandidateInfo['Status'] == 'True' :
                    punishment_amount = punishment_CandidateInfo['Data']['Shares'] * (20/100)
                    assert incentive_pool_balance_after == incentive_pool_balance_befor + punishment_amount
                else:
                    log.info("查询处罚节点:{}质押信息失败".format(node_data['host']))
            else:
                log.info("当前质押节点:{}链接正常".format(node_data['host']))
        except:
            status = 1
            assert status == 0, '停止节点:{}失败'.format(node_data['host'])

    def test_Staking_reward(self):
        pass

    def test_packaging_reward(self):
        pass

    def test_poundage_reward(self):
        pass






if __name__ == "__main__":
    a = TestDposinit()
    # a.test_token_loukup()
    #a.test_transfer_normal()
    #a.test_punishment_income()
    a.test()
    #a.ppos_link()
    #a.test_morelockup_pledge(1)