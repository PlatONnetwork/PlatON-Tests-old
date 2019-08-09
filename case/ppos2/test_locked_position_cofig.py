# -*- coding: utf-8 -*-

import json
import math
import time
import random

import allure
import pytest
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common import log
import json
from utils.platon_lib.govern_util import *
from utils.platon_lib.ppos_common import CommonMethod
from deploy.deploy import AutoDeployPlaton



class TestLockeDpositionConfig:
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
    chainid = 101
    ConsensusSize = 150
    time_interval = 10
    initial_amount = {'FOUNDATION': 905000000000000000000000000,
                      'FOUNDATIONLOCKUP': 20000000000000000000000000,
                      'STAKING': 25000000000000000000000000,
                      'INCENTIVEPOOL': 45000000000000000000000000,
                      'DEVELOPERS': 5000000000000000000000000
                      }
    def start_init(self):
        #修改config参数
        CommonMethod.update_config(self,'EconomicModel','Common','ExpectedMinutes',3)
        CommonMethod.update_config(self,'EconomicModel','Common','PerRoundBlocks',5)
        CommonMethod.update_config(self,'EconomicModel','Common','ValidatorCount',10)
        CommonMethod.update_config(self,'EconomicModel','Staking','ElectionDistance',10)
        CommonMethod.update_config(self,'EconomicModel','Staking','StakeThreshold',1000)
        #启动节点
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)


    def test_unlock_Normal(self):
        '''
        只有一个锁仓期，到达解锁期返回解锁金额
        :param amount:
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            # 创建锁仓计划
            loukupbalace = Web3.toWei (50, 'ether')
            plan = [{'Epoch': 1, 'Amount': loukupbalace}]
            result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                        from_address=address1, gasPrice=self.base_gas_price,
                                                        gas=self.staking_gas)
            assert result['Status'] == True, "创建锁仓计划返回状态为:{} 有误".format (result['Status'])
            print(address2)
            balance = platon_ppos.eth.getBalance(address2)
            log.info ("锁仓之后账户余额：{}".format (balance))
            log.info("当前块高：{}".format(platon_ppos.eth.blockNumber))
            RestrictingInfo = platon_ppos.GetRestrictingInfo(address2)
            assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
            dict_Info = json.loads(RestrictingInfo['Data'])
            assert dict_Info['balance'] == loukupbalace,"锁仓金额：{}有误".format(dict_Info['balance'])

            #验证到达锁仓解锁期之后账户金额
            CommonMethod.get_block_number(self,self.ConsensusSize)
            balance2 = platon_ppos.eth.getBalance(address2)
            log.info ("解锁之后账户余额：{}".format (balance2))
            RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
            assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
            dict_Info = json.loads (RestrictingInfo['Data'])
            balance = platon_ppos.eth.getBalance(address2)
            assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
            assert balance2 == loukupbalace,"返回的释放锁仓金额：{} 有误".format(balance)

    def test_multiple_unlock_Normal(self):
        '''
        多个锁仓期，到达部分解锁期返回解锁金额
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            loukupbalace = Web3.toWei (50, 'ether')
            plan = [{'Epoch': 1, 'Amount': loukupbalace},{'Epoch': 2, 'Amount': loukupbalace}]
            result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                        from_address=address1, gasPrice=self.base_gas_price,
                                                        gas=self.staking_gas)
            assert result['Status'] == True, "创建锁仓计划返回状态为:{} 有误".format (result['Status'])
            balance = platon_ppos.eth.getBalance (address2)
            log.info ("锁仓之后账户余额：{}".format (balance))
            log.info ("当前块高：{}".format (platon_ppos.eth.blockNumber))
            RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
            assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
            dict_Info = json.loads (RestrictingInfo['Data'])
            assert dict_Info['balance'] == loukupbalace*2, "锁仓金额：{}有误".format (dict_Info['balance'])

            # 验证到达锁仓解锁期之后账户金额
            CommonMethod.get_block_number (self, self.ConsensusSize)
            balance2 = platon_ppos.eth.getBalance (address2)
            log.info ("解锁之后账户余额：{}".format (balance2))
            RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
            assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
            dict_Info = json.loads (RestrictingInfo['Data'])
            balance = platon_ppos.eth.getBalance (address2)
            #log.info()dict_Info['Entry'][1]  ==
            assert dict_Info['balance'] == loukupbalace, "锁仓金额：{}有误".format (dict_Info['balance'])
            assert balance2 == loukupbalace, "返回的释放锁仓金额：{} 有误".format (balance)


    def test(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        log.info ("当前块高：{}".format (platon_ppos.eth.blockNumber))
        balance2 = platon_ppos.eth.getBalance ('0x1CAf947bC2fA1cb37C5da11588Fca30218581428')
        log.info ("解锁之后账户余额：{}".format (balance2))
        a = platon_ppos.GetRestrictingInfo ('0x1CAf947bC2fA1cb37C5da11588Fca30218581428')
        b = json.loads(a['Data'])
        print(b[''])







if __name__ == '__main__':
    a = TestLockeDpositionConfig()
    #a.start_init()
    #a.initial_unlock_Normal(1000)
    #a.test_initial_unlock_Normal()
    a.test()