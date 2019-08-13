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
        CommonMethod.get_block_number (self, self.ConsensusSize)
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
        CommonMethod.get_block_number (self, self.ConsensusSize)
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
        #balance = platon_ppos.eth.getBalance (address1)
        #log.info ("发起锁仓账户余额:{}".format (balance))
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 1, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address2, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])

        #给锁仓账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   self.privatekey)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None,"转账：{}失败".format(self.value)
        print(address2)
        balance1 = platon_ppos.eth.getBalance (address2)
        log.info ("锁仓账户余额：{}".format (balance1))
        assert balance1 == Web3.toWei(self.value,'ether'),"锁仓账户余额：{}".format (balance1)

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 800
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        balance2 = platon_ppos.eth.getBalance (address2)
        log.info ("质押完锁仓账户余额：{}".format (balance2))

        # 到达解锁期之后锁仓账号余额
        CommonMethod.get_block_number (self, self.ConsensusSize)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期后账户余额：{}".format (balance3))
        assert balance3 == balance2 + Web3.toWei(lockupamoutn - amount,'ether'),"锁仓账户金额：{} 有误".format(balance3)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True,"锁仓的状态：{} 有误".format(dict_Info['symbol'])
        assert dict_Info['debt'] == Web3.toWei(amount,'ether'),"欠释放锁仓金额：{} 有误".format(dict_Info['debt'])

        # 申请退回质押金
        result = platon_ppos.unStaking (nodeId, privatekey=private_key2, from_address=address2,
                                        gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押退回质押金返回的状态：{},用例失败".format (result['Status'])

        # 等待两个结算周期后查询锁仓账号情况
        balance4 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期申请退回质押金后账户余额：{}".format (balance4))
        CommonMethod.get_block_number (self, self.ConsensusSize * 2 + 10)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        balance5 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期退回质押金后账户余额：{}".format (balance5))
        log.info ("预期锁仓账户金额：{}".format (balance4 + Web3.toWei (lockupamoutn, 'ether')))
        assert balance5 == balance4 + Web3.toWei (lockupamoutn, 'ether'), "锁仓账户金额：{} 有误".format (balance4)
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
        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 100
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (0, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])

        # 创建锁仓计划
        # balance = platon_ppos.eth.getBalance (address1)
        # log.info ("发起锁仓账户余额:{}".format (balance))
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
        #assert dict_Info['debt'] == Web3.toWei (amount, 'ether'), "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])

        # 给锁仓账号转手续费
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (self.address),
                                                   Web3.toChecksumAddress (address2),
                                                   self.base_gas_price, self.base_gas, self.value,
                                                   conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        assert return_info is not None, "转账锁仓账号手续费：{}失败".format (self.value)
        balance1 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期后账户余额：{}".format (balance1))
        # 申请委托验证人节点
        amount = 100
        result = platon_ppos.delegate (1, nodeId, amount, privatekey=private_key2, from_address=address2,
                                              gasPrice=self.base_gas_price, gas=self.staking_gas)
        log.info ("申请委托地址：{}".format (address2))
        assert result['Status'] == True, "申请委托返回的状态：{},用例失败".format (result['Status'])
        balance2 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期后账户余额：{}".format (balance2))

        # 到达解锁期之后锁仓账号余额
        CommonMethod.get_block_number (self, self.ConsensusSize)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期后账户余额：{}".format (balance3))
        assert balance3 == balance2, "锁仓账户金额：{} 有误".format (balance3)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        #assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
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
        balance4 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期发起赎回部分委托后账户余额：{}".format (balance4))
        CommonMethod.get_block_number (self, self.ConsensusSize)
        balance5 = platon_ppos.eth.getBalance (address2)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        log.info ("赎回部分委托金后锁仓账户余额：{}".format (balance5))
        assert balance5 == balance4 + Web3.toWei (partamount, 'ether'),"到达解锁期赎回部分委托后账户余额：{}".format (balance5)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == loukupbalace - Web3.toWei (partamount, 'ether'), "欠释放锁仓金额：{} 有误".format (dict_Info[                                                                                         'debt'])
        #申请赎回全部委托金
        msg = platon_ppos.getCandidateInfo (nodeId)
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        delegate_info = platon_ppos.unDelegate (stakingBlockNum, nodeId, lockupamoutn - partamount, privatekey=private_key2,
                                                from_address=address2, gasPrice=self.base_gas_price,
                                                gas=self.staking_gas)
        assert delegate_info['Status'] == True, "申请赎回委托返回的状态：{},用例失败".format (result['Status'])
        balance6 = platon_ppos.eth.getBalance (address2)
        log.info ("赎回全部委托金后锁仓账户余额：{}".format (balance6))
        CommonMethod.get_block_number (self, self.ConsensusSize)
        balance7 = platon_ppos.eth.getBalance (address2)
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        log.info ("赎回全部委托金后预期锁仓账户余额：{}".format (balance6 + Web3.toWei (lockupamoutn, 'ether')))
        log.info ("赎回全部委托金后最终锁仓账户余额：{}".format (balance7))
        assert balance7 == balance6 + loukupbalace - Web3.toWei (partamount, 'ether'), "到达解锁期赎回委托后账户余额：{}".format                                                                                               (balance7)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == False, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == 0, "欠释放锁仓金额：{} 有误".format (
            dict_Info['debt'])

    def test_unlock_point_pledge_punish_amount(self):
        '''
        到达解锁期后处罚节点后锁仓账户的余额情况
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
        assert return_info is not None, "转账：{}失败".format (self.value)
        # 创建锁仓计划
        # balance = platon_ppos.eth.getBalance (address1)
        # log.info ("发起锁仓账户余额:{}".format (balance))
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 2, 'Amount': loukupbalace}]
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
        print (address2)
        balance1 = platon_ppos.eth.getBalance (address2)
        log.info ("锁仓账户余额：{}".format (balance1))
        assert balance1 == Web3.toWei (self.value, 'ether'), "锁仓账户余额：{}".format (balance1)

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 900
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        balance2 = platon_ppos.eth.getBalance (address2)
        log.info ("质押完锁仓账户余额：{}".format (balance2))
        platon_ppos.GetRestrictingInfo(address2)
        result = platon_ppos.getCandidateInfo(nodeId)
        log.info("质押信息:{}".format(result))
        assert result['Status'] == True, "获取质押节点返回状态为:{} 有误".format (result['Status'])
        RestrictingPlan = result['Data']['RestrictingPlanHes']
        assert RestrictingPlan == Web3.toWei (amount, 'ether'),'质押金额：{} 有误'.format(RestrictingPlan)

        # 获取节点内置质押节点信息
        con_node, no_node = get_node_list (self.node_yml_path)
        nodes = con_node + no_node
        for node in nodes:
            if nodeId in node.values ():
                node_data = node

        #停止其中一个正在出块的节点信息
        self.auto = AutoDeployPlaton ()
        self.auto.kill (node_data)
        platon_ppos1 = connect_web3 (node_data['url'])
        assert not platon_ppos1.isConnected(),"节点：{} 连接异常".format(node_data['host'])

        # 到达解锁期之后锁仓账号余额
        CommonMethod.get_block_number (self, self.ConsensusSize*2)
        Candidateinfo = platon_ppos.getCandidateList()
        log.info("查询所有实时的候选人信息：{}".format(Candidateinfo))
        platon_ppos.GetRestrictingInfo(address2)
        result = platon_ppos.getCandidateInfo(nodeId)
        log.info("质押节点信息:{}".format(result))
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        balance3 = platon_ppos.eth.getBalance (address2)
        log.info ("到达解锁期后账户余额：{}".format (balance3))
        assert balance3 == balance2 + Web3.toWei (amount * 0.2, 'ether'), "锁仓账户金额：{} 有误".format (balance3)
        assert RestrictingInfo['Status'] == True, "获取锁仓计划返回状态为:{} 有误".format (result['Status'])
        dict_Info = json.loads (RestrictingInfo['Data'])
        assert dict_Info['balance'] == 0, "锁仓金额：{}有误".format (dict_Info['balance'])
        assert dict_Info['symbol'] == True, "锁仓的状态：{} 有误".format (dict_Info['symbol'])
        assert dict_Info['debt'] == 0, "欠释放锁仓金额：{} 有误".format (dict_Info['debt'])


    def test_eliminated_verifier_create_lockup(self):
        '''
        验证人违规被剔除验证人列表，创建锁仓计划
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
        assert return_info is not None, "转账：{}失败".format (self.value)
        # 创建锁仓计划
        # balance = platon_ppos.eth.getBalance (address1)
        # log.info ("发起锁仓账户余额:{}".format (balance))
        lockupamoutn = 500
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 2, 'Amount': loukupbalace}]
        result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey=private_key1,
                                                    from_address=address1, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
        assert result['Status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['Status'])
        RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
        assert RestrictingInfo['Status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['Status'])

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 500
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])

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

        # 节点被剔除验证人列表之后
        while 1:
            #CommonMethod.get_block_number (self, 100)
            result = platon_ppos.getCandidateInfo (nodeId)
            if result['Status'] == True:
                time.sleep(10)
            else:
                break

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 500
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key1, from_address=address1,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == False, "申请质押返回的状态：{},用例失败".format (result['Status'])

    def test_owe_amountstack_lock_plan(self):
        '''
        到达解锁时间点，如果账户锁仓不足再新增新的锁仓计划
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
        assert return_info is not None, "转账：{}失败".format (self.value)
        # 创建锁仓计划
        # balance = platon_ppos.eth.getBalance (address1)
        # log.info ("发起锁仓账户余额:{}".format (balance))
        lockupamoutn = 900
        loukupbalace = Web3.toWei (lockupamoutn, 'ether')
        plan = [{'Epoch': 2, 'Amount': loukupbalace}]
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
        print (address2)
        balance1 = platon_ppos.eth.getBalance (address2)
        log.info ("锁仓账户余额：{}".format (balance1))
        assert balance1 == Web3.toWei (self.value, 'ether'), "锁仓账户余额：{}".format (balance1)

        # 申请质押节点
        version = get_version (platon_ppos)
        amount = 900
        nodeId = CommonMethod.read_out_nodeId (self, 'nocollusion')
        result = platon_ppos.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                            amount, version, privatekey=private_key2, from_address=address2,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)
        assert result['Status'] == True, "申请质押返回的状态：{},{},用例失败".format (result['Status'], result['ErrMsg'])
        balance2 = platon_ppos.eth.getBalance (address2)
        log.info ("质押完锁仓账户余额：{}".format (balance2))
        platon_ppos.GetRestrictingInfo (address2)
        result = platon_ppos.getCandidateInfo (nodeId)
        log.info ("质押信息:{}".format (result))
        assert result['Status'] == True, "获取质押节点返回状态为:{} 有误".format (result['Status'])
        RestrictingPlan = result['Data']['RestrictingPlanHes']
        assert RestrictingPlan == Web3.toWei (amount, 'ether'), '质押金额：{} 有误'.format (RestrictingPlan)








    def test(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        # platon_ppos1 = connect_web3 ('http://192.168.10.226:6789')        # 停止其中一个正在出块的节点信息
        # a = platon_ppos1.isConnected ()
        # print(a)
        # self.auto = AutoDeployPlaton ()
        # self.auto.kill (node_data)
        # platon_ppos1 = connect_web3 (node_data['url'])

        # while 1:
        #     log.info ("当前块高：{}".format (platon_ppos.eth.blockNumber))
        #     time.sleep(5)
        # Candidateinfo = platon_ppos.getCandidateList ()
        # log.info ("查询所有实时的候选人信息：{}".format (Candidateinfo))
        # balance2 = platon_ppos.eth.getBalance (Web3.toChecksumAddress(0x2061B05df81F4336feA36173F029a7CC88A98301))
        # log.info ("解锁之后账户余额：{}".format (balance2))
        # platon_ppos.GetRestrictingInfo ('0x2061B05df81F4336feA36173F029a7CC88A98301')
        result = platon_ppos.getCandidateInfo ('4e7f7efc4a36f8b05def1fc99225533a3d792f9e4535822a8abd6a1107d68a9f2e9c233484b4ce84771913fa9aec0cee0e8d0109eef5c55dec0e1b34ae939df1')
        log.info ("质押节点信息:{}".format (result))
        # b = json.loads(a['Data'])
        # print(b['Entry'][0]['amount'])








if __name__ == '__main__':
    a = TestLockeDpositionConfig()
    #a.start_init()
    #a.initial_unlock_Normal(1000)
    #a.test_unlock_Normal()
    #a.test_multiple_unlock_Normal()
    a.test()
    #a.test_unlock_point_pledge_amount()
    #a.test_unlock_point_delegtion_notbalance()
    #a.test_unlock_point_pledge_punish_amount()