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
from common.load_file import get_node_list
from common import log
import json
from common.connect import connect_web3
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
        #修改config参数
        CommonMethod.update_config(self,'EconomicModel','Common','ExpectedMinutes',3)
        CommonMethod.update_config(self,'EconomicModel','Common','PerRoundBlocks',10)
        CommonMethod.update_config(self,'EconomicModel','Common','ValidatorCount',5)
        CommonMethod.update_config(self,'EconomicModel','Staking','ElectionDistance',20)
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
        assert return_info is not None,"转账：{}失败".format(self.value)
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
        CommonMethod.get_next_settlement_interval(self)
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
        assert return_info is not None,"转账：{}失败".format(self.value)
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

        # 验证到达锁仓第一个解锁期之后账户金额
        CommonMethod.get_next_settlement_interval (self)
        balance2 = platon_ppos.eth.getBalance (address2)
        log.info ("到达第一个解锁期后账户余额：{}".format (balance2))
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        balance = platon_ppos.eth.getBalance (address2)
        assert dict_Info['balance'] == loukupbalace, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['Entry'][0]['amount'] == loukupbalace,"第二个解锁期待释放金额：{}".format(dict_Info['Entry'][0]['amount'])
        assert balance2 == loukupbalace, "返回的释放锁仓金额：{} 有误".format (balance)

        #验证到达锁仓第二个解锁期之后账户金额
        CommonMethod.get_next_settlement_interval (self)
        balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("到达第二个解锁期后账户余额：{}".format (balance2))
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        balance = platon_ppos.eth.getBalance (address2)
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert balance3 == loukupbalace*2, "返回的释放锁仓金额：{} 有误".format (balance)

    def test_unlock_point_pledge_amount(self):
        '''
        到达解锁时间点，锁仓金额质押后在解锁期之后再申请退回质押金
        :return:
        '''
        nodeId = CommonMethod.get_no_candidate_list (self)
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None,"转账：{}失败".format(self.value)

        # 给锁仓账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)
        Balance = platon_ppos.eth.getBalance(address1)
        log.info("{}发起锁仓账户余额：{}".format(address1,Balance))
        Balance1 = platon_ppos.eth.getBalance (address1)
        log.info ("{}发起质押账号余额：{}".format (address2, Balance1))

        # 创建锁仓计划
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 1, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])
        info = json.loads(RestrictingInfo['Data'])
        assert info['balance'] == loukupbalace,"锁仓计划可用余额：{},有误".format(info['balance'])
        balance2 = platon_ppos.eth.getBalance (address1)
        log.info ("{}创建锁仓后余额：{}".format (address1,balance2))

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 800
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("{}质押完账户余额：{}".format (address2,balance3))
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == Web3.toWei(lockupamoutn - amount,'ether'), "锁仓金额：{}有误".format (dict_Info['balance'])

        # 到达解锁期之后锁仓账号余额
        CommonMethod.get_next_settlement_interval (self)
        balance4 = platon_ppos.eth.getBalance (address2)
        log.info("到达解锁期后预期账户余额：{}".format(balance3 + Web3.toWei(lockupamoutn - amount,'ether')))
        log.info("到达解锁期后实际账户余额：{}".format (balance4))
        assert balance4 == balance3 + Web3.toWei(lockupamoutn - amount,'ether'),"锁仓账户金额：{} 有误".format(balance4)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True,"锁仓的状态：{} 有误".format(dict_Info['symbol'])
        assert dict_Info['debt'] == Web3.toWei(amount,'ether'),"欠释放锁仓金额：{} 有误".format(dict_Info['debt'])

        # 申请退回质押金
        result = platon_ppos.unStaking (nodeId, privatekey=private_key2, from_address=address2,
                                        gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押退回质押金返回的状态：{},用例失败".format (result['Status'])
        balance5 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期申请退回质押金后账户余额：{}".format (balance5))

        # 等待两个结算周期后查询锁仓账号情况
        CommonMethod.get_next_settlement_interval (self,3)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        balance6 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期退回质押金后预期账户金额：{}".format (balance5 + loukupbalace))
        log.info ("到达解锁期退回质押金后实际账户余额：{}".format (balance6))
        assert balance6 == balance5 + loukupbalace, "锁仓账户金额：{} 有误".format (balance6)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == False, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == 0, "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])



    def test_unlock_point_delegtion_notbalance(self):
        '''
        1、到达解锁时间点用锁仓金额去委托节点，到达解锁期账户锁仓不足
        2、到达解锁期账户申请部分赎回委托
        3、全部赎回委托
        :return:
        '''
        nodeId = CommonMethod.get_no_candidate_list (self)
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账质押账号手续费：{}失败".format (self.value)

        # 给锁仓账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账锁仓账号手续费：{}失败".format (self.value)
        Balance = platon_ppos.eth.getBalance (address1)
        log.info ("{}发起锁仓账户余额：{}".format (address1, Balance))
        Balance1 = platon_ppos.eth.getBalance (address1)
        log.info ("{}发起质押账号余额：{}".format (address2, Balance1))

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 100
        result = platon_ppos.createStaking (0, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        Balance2 = platon_ppos.eth.getBalance (address1)
        log.info ("{}申请质押节点后账户余额：{}".format (address1, Balance2))

        # 创建锁仓计划
        lockupamoutn = 100
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 1, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == loukupbalace, "锁仓计划金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == False, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == 0, "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])
        Balance3 = platon_ppos.eth.getBalance (address1)
        log.info ("{}创建锁仓计划后账户余额：{}".format (address1, Balance3))

        # 申请委托验证人节点
        amount = 100
        result = platon_ppos.delegate (1, nodeId, amount, privatekey=private_key2, from_address=address2,
                                              gasPrice=self.base_gas_price, gas=self.staking_gas)
        log.info ("申请委托地址：{}".format (address2))
        assert result['Status'] == True, "申请委托返回的状态：{},用例失败".format (result['Status'])
        balance4 = platon_ppos.eth.getBalance (address2)
        log.info ("{}申请委托验证人节点后账户余额：{}".format (address2,balance4))

        # 到达解锁期之后锁仓账号余额
        CommonMethod.get_next_settlement_interval (self)
        balance5 = platon_ppos.eth.getBalance (address2)
        log.info ("{}到达解锁期后实际账户余额：{}".format (address2,balance5))
        assert balance5 == balance4, "锁仓账户金额：{} 有误".format (balance5)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == loukupbalace, "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])

        #申请赎回部分委托金
        partamount = 50
        msg = platon_ppos.getCandidateInfo (nodeId)
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        delegate_info = platon_ppos.unDelegate (stakingBlockNum, nodeId, partamount, privatekey=private_key2,
                                                from_address=address2, gasPrice=self.base_gas_price,
                                                gas=self.staking_gas)
        assert delegate_info['Status'] == True, "申请赎回委托返回的状态：{},用例失败".format (result['Status'])
        balance6 = platon_ppos.eth.getBalance (address2)
        log.info ("{}到达解锁期发起赎回部分委托后账户余额：{}".format (address2,balance6))

        #到达下个解锁期释放部分委托金
        CommonMethod.get_next_settlement_interval (self)
        balance7 = platon_ppos.eth.getBalance (address2)
        log.info ("赎回部分委托金后锁仓账户余额：{}".format (balance7))
        assert balance7 == balance6 + Web3.toWei (partamount, 'ether'),"到达解锁期赎回部分委托后账户余额：{}".format (balance7)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == loukupbalace - Web3.toWei (partamount, 'ether'), "欠释放锁仓金额：{} 有误".format (dict_Info[                                                                                         'debt'])
        #申请赎回全部委托金
        delegate_info = platon_ppos.unDelegate (stakingBlockNum, nodeId, lockupamoutn - partamount, privatekey=private_key2,
                                                from_address=address2, gasPrice=self.base_gas_price,
                                                gas=self.staking_gas)
        assert delegate_info['Status'] == True, "申请赎回委托返回的状态：{},用例失败".format (result['Status'])
        balance8 = platon_ppos.eth.getBalance (address2)
        log.info ("{}赎回全部委托金后锁仓账户余额：{}".format (address2,balance8))

        #到达下个解锁期释放全部委托金
        CommonMethod.get_next_settlement_interval (self)
        balance9 = platon_ppos.eth.getBalance (address2)
        log.info ("{}赎回全部委托金后实际账户余额：{}".format (address2,balance9))
        log.info ("{}赎回全部委托金后预期账户余额：{}".format (address2,balance8 + Web3.toWei (lockupamoutn - partamount, 'ether')))
        assert balance9 == balance8 + loukupbalace - Web3.toWei (partamount, 'ether'), "到达解锁期赎回委托后账户余额：{}".format                                                                                             (balance9)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == False, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == 0, "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])

    def test_unlock_point_pledge_punish_amount(self):
        '''
        到达解锁期后处罚节点后锁仓账户的余额情况
        :return:
        '''
        nodeId = CommonMethod.get_no_candidate_list (self)
        log.info("质押节点ID：{}".format(nodeId))
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 给发起锁仓账户转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)

        # 给发起质押账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)

        Balance = platon_ppos.eth.getBalance (address1)
        log.info ("{}账户余额：{}".format (address1, Balance))
        Balance1 = platon_ppos.eth.getBalance (address1)
        log.info ("{}账号余额：{}".format (address2, Balance1))

        # 创建锁仓计划
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 3, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])
        Balance2 = platon_ppos.eth.getBalance (address1)
        log.info ("{}发起锁仓后账户余额：{}".format (address1, Balance2))

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 900
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        platon_ppos.GetRestrictingInfo(address2)
        result = platon_ppos.getCandidateInfo(nodeId)
        assert result['Status'] == True, "获取质押节点返回状态为:{} 有误".format (result['Status'])
        RestrictingPlan = result['Data']['RestrictingPlanHes']
        assert RestrictingPlan == Web3.toWei (amount, 'ether'),'质押金额：{} 有误'.format(RestrictingPlan)
        Balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("{}质押完锁仓账户余额：{}".format (address2,Balance3))

        #等待验证人加入共识出块节点
        CommonMethod.get_next_settlement_interval (self,1)
        Balance4 = platon_ppos.eth.getBalance (address2)
        log.info ("{}加入共识验证人后账户余额：{}".format (address2, Balance4))

        # 获取节点内置质押节点信息
        con_node, no_node = get_node_list (self.node_yml_path)
        nodes = con_node + no_node
        for node in nodes:
            if nodeId in node.values ():
                node_data = node
        log.info("{}质押节点信息：{}".format(address2,node_data))

        #停止质押节点
        self.auto = AutoDeployPlaton ()
        self.auto.kill (node_data)
        platon_ppos1 = connect_web3 (node_data['url'])
        assert not platon_ppos1.isConnected(),"节点：{} 连接异常".format(node_data['host'])

        # 到达解锁期后处罚节点后锁仓账户
        CommonMethod.get_next_settlement_interval (self,1)
        Balance5 = platon_ppos.eth.getBalance (address2)
        log.info ("{}到达解锁期后处罚节点后预期账户余额：{}".format (address2,Balance4 + Web3.toWei (amount-(amount * 0.2), 'ether')))
        log.info ("{}到达解锁期后处罚节点后实际账户余额：{}".format (address2,Balance5))
        result = platon_ppos.getCandidateInfo(nodeId)
        assert Balance5 == Balance4 + Web3.toWei (amount-(amount * 0.2), 'ether'), "锁仓账户金额：{} 有误".format (Balance4)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓计划可用金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "欠释放状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == Web3.toWei (amount-(amount * 0.2), 'ether'), "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])


    def test_eliminated_verifier_create_lockup(self):
        '''
        验证人违规被剔除验证人列表，申请质押节点
        :return:
        '''
        nodeId = CommonMethod.get_no_candidate_list (self)
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)

        balance = platon_ppos.eth.getBalance (address1)
        log.info ("{}发起锁仓账户余额:{}".format (address1,balance))

        # 创建锁仓计划
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 5, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 200
        result = platon_ppos.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        result = platon_ppos.getCandidateInfo(nodeId)
        log.info("质押节点信息：{}".format(result))

        # 等待成为共识验证人
        CommonMethod.get_next_settlement_interval (self)
        CandidateInfo = platon_ppos.getCandidateInfo(nodeId)
        log.info("验证人信息{}".format(CandidateInfo))
        VerifierList = platon_ppos.getVerifierList ()
        log.info ("当前验证人列表：{}".format (VerifierList))
        ValidatorList = platon_ppos.getValidatorList()
        log.info("当前共识验证人列表：{}".format(ValidatorList))



        # for dictinfo in CandidateInfo['Data']:
        #     if nodeId == dictinfo['NodeId']:
        #         log.info("节点id：{}已成为共识验证人".format(nodeId))
        #         break
        #     else:
        #         log.info("节点id：{}未成为共识验证人".format(nodeId))
        #         status=0
        #         assert status == 1

        # 获取节点内置质押节点信息
        con_node, no_node = get_node_list (self.node_yml_path)
        nodes = con_node + no_node
        for node in nodes:
            if nodeId in node.values ():
                node_data = node

        # 停止其中一个正在出块的节点信息
        self.auto = AutoDeployPlaton ()
        self.auto.kill (node_data)
        platon_ppos1 = connect_web3 (node_data['url'])
        assert not platon_ppos1.isConnected (), "节点：{} 连接异常".format (node_data['host'])

        # 等待节点被剔除验证人列表
        CommonMethod.get_next_consensus_wheel (self,2)

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 200
        result = platon_ppos.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == False, "申请质押返回的状态：{},用例失败".format (result['Status'])

    def test_owe_amountstack_lock_plan(self):
        '''
        到达解锁时间点，如果账户锁仓不足再新增新的锁仓计划
        :return:
        '''
        nodeId = CommonMethod.get_no_candidate_list (self)
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address1),
                                                   self.base_gas_price, self.base_gas, self.value, self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)

        # 创建锁仓计划
        lockupamoutn = 500
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 1, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])

        # 给锁仓账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账：{}失败".format (self.value)
        balance = platon_ppos.eth.getBalance(address2)
        log.info("锁仓账户余额：{}".format(balance))

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 500
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])

        #到达解锁期释放锁仓金额
        CommonMethod.get_next_settlement_interval (self)
        platon_ppos.GetRestrictingInfo(address2)
        balance = platon_ppos.eth.getBalance(address2)
        log.info("到达解锁期释放锁仓余额：{}".format(balance))

        # 创建锁仓计划
        lockupamoutn = 100
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 1, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == Web3.toWei (100, 'ether'), "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == Web3.toWei (500, 'ether'), "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])



    def testss(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        while 1:
            block = platon_ppos.eth.blockNumber
            print(block)
        # Balance = platon_ppos.eth.getBalance('0x8E6b51f6D28A9e92726186Fb3D1720A31b098694')
        # print(Balance)
        # platon_ppos1 = connect_web3 ('http://192.168.10.225:6789')
        # result = platon_ppos1.isConnected()
        # print(result)
        # result1 = platon_ppos.getCandidateInfo ('2c34d6cd119e3b77b43aecdcfd653cacbd6b3b3c387a0d227e4d71b36a6a71b6111ecc953e329015fb1bc06961819609ffd5f73b63a179f27893e9e2da1e8ca1')
        # print("验证人信息：",result1)
        # result2= platon_ppos.getVerifierList()
        # result = platon_ppos.getValidatorList()
        # print("当前验证人列表",result2)
        # print("当前共识列表",result)





if __name__ == '__main__':
    a = TestLockeDpositionConfig()
    #a.start_init()
    #a.initial_unlock_Normal(1000)
    #a.test_unlock_Normal()
    #a.test_multiple_unlock_Normal()
    a.testss()
    #a.test_unlock_point_pledge_amount()
    #a.test_eliminated_verifier_create_lockup()
