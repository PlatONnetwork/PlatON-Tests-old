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
    gasPrice = Web3.toWei(0.000000000000000001,'ether')
    gas = 21000
    transfer_gasPrice = Web3.toWei(1,'ether')
    transfer_gas = 210000000
    value = 1000
    chainid = 101
    ConsensusSize = 250
    time_interval = 10
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

        url = CommonMethod.link_list(self)
        platon_ppos = Ppos(url,self.address,self.chainid)
        FOUNDATION = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONADDRESS))
        FOUNDATIONLOCKUP = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONLOCKUPADDRESS))
        STAKING = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.STAKINGADDRESS))
        INCENTIVEPOOL = platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
        log.info("奖励池初始金额:{}".format(INCENTIVEPOOL))
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
        address1,private_key1 = CommonMethod.read_private_key_list()
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.transfer_gasPrice, self.gas, self.value,
                                          conf.PRIVATE_KEY)
        return_info= platon_ppos.eth.waitForTransactionReceipt(result)
        if return_info is not None:
            Balance = platon_ppos.eth.getBalance(address1)
            log.info("转账金额{}",Balance)
            assert Web3.toWei(self.value,'ether') == Balance,"转账金额:{}失败".format(Balance)
        else:
            status = 1
            assert status == 0, "转账金额:{}失败".format(self.value)


    # def test_transfer_notsufficientfunds(self):
    #     '''
    #     账户余额不足的情况下进行转账
    #     :return:
    #     '''
    #     platon_ppos = CommonMethod.ppos_link (self)
    #     #账户1
    #     address1,private_key1 = CommonMethod.read_private_key_list()
    #     #账户2
    #     address2,private_key2 = CommonMethod.read_private_key_list()
    #     balance = platon_ppos.eth.getBalance(address1)
    #     result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (address1),
    #                                       Web3.toChecksumAddress (address2), self.transfer_gasPrice, self.gas, self.value,
    #                                       private_key1)
    #     print('报错',result)

    def test_transfer_funds(self):
        '''
        验证初始化之后普通账户转账内置账户
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        lockup_balancebe_before = platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
        log.info("转账前激励池余额：".format(lockup_balancebe_before))
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS), self.transfer_gasPrice, self.gas,                                                          self.value,conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            lockup_balancebe_after = platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
            log.info ("转账后激励池余额：".format (lockup_balancebe_before))
            assert lockup_balancebe_before + Web3.toWei (self.value, 'ether') == lockup_balancebe_after,"转账金额:{}失败".format(                                                             self.value)
        else:
            status = 1
            assert status == 0, "转账激励池账户金额:{}失败".format (self.value)



    def test_fee_income(self):
        '''
        验证初始内置账户没有基金会Staking奖励和出块奖励只有手续费收益
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        incentive_pool_balance_befor = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
        log.info('交易前激励池查询余额：{}'.format(incentive_pool_balance_befor))
        # 签名转账
        address1,private_key1 = CommonMethod.read_private_key_list()
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                          Web3.toChecksumAddress (address1), self.transfer_gasPrice, self.gas, self.value,
                                          self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
            log.info('交易后激励池查询余额：{}'.format(incentive_pool_balance_after))
            difference = incentive_pool_balance_after - incentive_pool_balance_befor
            log.info('手续费的金额：{}'.format(difference))
            assert difference == (self.gas * self.transfer_gasPrice),"手续费{}有误".format(difference)
        else:
            status = 1
            assert status == 0, "转账{}金额错误".format(Web3.toWei (self.value, 'ether'))


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
        node_info = get_node_list (self.node_yml_path)
        node_info_length = len (node_info) - 1
        index = random.randint (0, node_info_length)
        node_data = node_info[0][index]

        #获取节点质押金额
        punishment_CandidateInfo = platon_ppos.getCandidateInfo (node_data['id'])
        assert punishment_CandidateInfo['Status'] == True, "查询锁仓信息失败"
        punishment_amount = punishment_CandidateInfo['Data']['Released'] * (20 / 100)
        print(punishment_amount)

        #停止其中一个正在出块的节点信息
        self.auto = AutoDeployPlaton ()
        self.auto.kill(node_data)
        platon_ppos1 = connect_web3(node_data['url'])

        if not platon_ppos1.isConnected():

            url = CommonMethod.link_list (self)
            platon_ppos = Ppos (url, self.address, self.chainid)
            CommonMethod.get_block_number(self)

            incentive_pool_balance_after = platon_ppos.eth.getBalance (conf.INCENTIVEPOOLADDRESS)
            log.info ('处罚之后激励池查询余额：{}'.format (incentive_pool_balance_after))

            assert incentive_pool_balance_after == incentive_pool_balance_befor + punishment_amount

        else:
            status = 1
            assert status == 0, '停止节点:{}失败'.format (node_data['host'])



    def test_Staking_reward(self):
        pass

    def test_packaging_reward(self):
        pass

    def test_poundage_reward(self):
        pass






if __name__ == "__main__":
    a = TestDposinit()
    a.test()
    #a.test_init_token()
    #a.test_punishment_income()