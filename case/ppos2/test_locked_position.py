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
from utils.platon_lib.ppos_common import CommonMethod


class TestLockeDposition:
    address = conf.ADDRESS
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_TEST_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    gasPrice = 60000000000000
    gas = 21000
    transfer_gasPrice = Web3.toWei (1, 'ether')
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



    @allure.title ("查看初始化时锁仓余额和锁仓信息")
    def test_token_loukup(self):
        '''
        查询初始化链后基金会锁仓金额
        以及查询初始锁仓计划信息的有效性
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        lockupbalance = platon_ppos.eth.getBalance (conf.FOUNDATIONLOCKUPADDRESS)
        FOUNDATIONLOCKUP = self.initial_amount['FOUNDATIONLOCKUP']
        assert lockupbalance == FOUNDATIONLOCKUP
        result = platon_ppos.GetRestrictingInfo(conf.INCENTIVEPOOLADDRESS)
        assert result['Status']==True,"，锁仓计划信息查询状态为{}".format(result['Status'])
        dict_info = json.loads(result['Data'])
        assert dict_info['balance'] == self.initial_amount['FOUNDATIONLOCKUP'],'锁仓初始金额{}有误'.format(lockupbalance)


    def test_loukupplan(self):
        '''
        验证正常锁仓功能
        参数输入：
        Epoch：1
        Amount：50 ether
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1,private_key1 = CommonMethod.read_private_key_list()
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            #查询锁仓账户的余额
            lockup_before = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
            log.info ("发起锁仓账户的余额:{}".format(lockup_before))

            #创建锁仓计划
            loukupbalace = Web3.toWei(50,'ether')
            plan = [{'Epoch': 1 ,'Amount':loukupbalace}]
            url = CommonMethod.link_list (self)
            platon_ppos1 = Ppos (url, address1, self.chainid,private_key1)
            result =platon_ppos1.CreateRestrictingPlan(address1,plan,private_key1,
                                              from_address=address1, gasPrice=self.gasPrice )
            assert result['status'],"创建锁仓计划失败"
            lockup_after = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
            assert lockup_after == lockup_before + loukupbalace,"锁仓账户金额：{}有误".format(lockup_after)

            #查看锁仓计划明细
            detail = RestrictingInfo = platon_ppos.GetRestrictingInfo(address1)
            assert detail['status'] == True,"查询锁仓计划信息返回状态为:{}".format(result['status'])
            assert RestrictingInfo['balance'] == loukupbalace,"创建锁仓计划金额：{}有误".format(lockup_after)



    @allure.title ("根据不同参数创建锁仓计划")
    @pytest.mark.parametrize ('number,amount', [(1,0.1),(-1,3),(0.1,3),(37,3)])
    def test_loukupplan_abnormal(self,number,amount):
        '''
        创建锁仓计划时，参数有效性验证
        number : 锁仓解锁期
        amount : 锁仓金额
        :param number:
        :param amount:
        :return:
        '''

        address1,private_key1 = CommonMethod.read_private_key_list()
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        loukupbalace = Web3.toWei (amount, 'ether')
        plan = [{'Epoch': number, 'Amount': loukupbalace}]
        #当锁仓金额输入小于 1ether
        if number >= 1 and amount < 1:
            result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                        from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
            assert result['status'] == False,'创建锁仓状态为：{},用例失败'.format(result['status'])
        #当锁仓解锁期输入非正整数倍
        elif number < 0 or type (number) == float:
            result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                        from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
            assert result['status'] == False,'创建锁仓状态为：{},用例失败'.format(result['status'])
        #当锁仓解锁期大于36个结算期
        elif number > 36:
            result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                        from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
            assert result['status'] == False, '创建锁仓状态为：{},用例失败'.format (result['status'])



    @allure.title ("锁仓金额大于账户余额")
    def test_loukupplan_amount(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1,private_key1 = CommonMethod.read_private_key_list()
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
                loukupbalace = Web3.toWei (10000, 'ether')
                plan = [{'Epoch': 1, 'Amount': loukupbalace}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == False,'创建锁仓计划返回状态为{}，用例失败'.format(result['status'])
        else:
            status = 1
            assert status == 0, '转账失败'

    @allure.title ("多个锁仓期金额情况验证")
    @pytest.mark.parametrize ('balace1,balace2', [(300,300),(500,600)])
    def test_loukupplan_Moredeadline(self, balace1, balace2):
        '''
        验证一个锁仓计划里有多个解锁期
        amount : 锁仓
        balace1 : 第一个锁仓期的锁仓金额
        balace2 : 第二个锁仓期的锁仓金额
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1,private_key1 = CommonMethod.read_private_key_list()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            loukupbalace1 = Web3.toWei (balace1, 'ether')
            loukupbalace2 = Web3.toWei (balace2, 'ether')
            if  self.value > (loukupbalace1 + loukupbalace2) :
                plan = [{'Epoch': 1, 'Amount': loukupbalace1},{'Epoch': 2, 'Amount': loukupbalace2}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == True,"创建锁仓计划返回的状态：{},用例失败".format(result['status'])
            elif self.value <= (loukupbalace1 + loukupbalace2) :
                plan = [{'Epoch': 1, 'Amount': loukupbalace1}, {'Epoch': 2, 'Amount': loukupbalace2}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice,
                                                            gas=self.gas)
                assert result['status'] == True,"创建锁仓计划返回的状态：{},用例失败".format(result['status'])
            else:
                log.info('锁仓输入的金额:{}出现异常'.format((loukupbalace1+loukupbalace2)))
                status = 1
                assert status == 0, 'error:创建锁仓失败'
        else:
            status = 1
            assert status == 0, 'error:转账失败'


    @allure.title ("锁仓计划多个相同解锁期情况验证")
    @pytest.mark.parametrize ('status,', [(1),(2)])
    def test_loukupplan_sameperiod(self, status):
        '''
        验证一个锁仓计划里有多个相同解锁期
        code =1 :同个account在一个锁仓计划里有相同解锁期
        code =2 :同个account在不同锁仓计划里有相同解锁期
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)

        address1,private_key1 = CommonMethod.read_private_key_list()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            period1 = 1
            period2 = 2
            loukupbalace = Web3.toWei (100, 'ether')
            if status == 1:
                plan = [{'Epoch': period1, 'Amount': loukupbalace}, {'Epoch': period1, 'Amount': loukupbalace}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice,
                                                            gas=self.gas)
                assert result['status'] == True,"创建锁仓计划返回的状态：{},用例失败".format(result['status'])
                RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
                json_data = json.loads(RestrictingInfo['Data'])
                assert json_data['Entry'][0]['amount'] == (loukupbalace + loukupbalace),'锁仓金额{}有误'.format(json_data['Entry'][                                                                   0]['amount'])

            elif status == 2:
                plan = [{'Epoch': period1, 'Amount': loukupbalace}, {'Epoch': period2, 'Amount': loukupbalace}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice,
                                                            gas=self.gas)
                assert result['status'] == True,"创建锁仓计划返回的状态：{},用例失败".format(result['status'])
                loukupbalace2 = Web3.toWei (200, 'ether')
                plan = [{'Epoch': period1, 'Amount': loukupbalace2}, {'Epoch': period2, 'Amount': loukupbalace2}]
                result1 = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice,
                                                            gas=self.gas)
                assert result1['status'] == True,"创建锁仓计划返回的状态：{},用例失败".format(result['status'])
                RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
                json_data = json.loads (RestrictingInfo['Data'])
                assert json_data['Entry'][0]['amount'] == (loukupbalace + loukupbalace2),'锁仓金额{}有误'.format(json_data['Entry'][                                                                   0]['amount'])
            else:
                status = 1
                assert status == 0, '输入的status:{}有误'.format(status)
        else:
            status = 1
            assert status == 0, 'error:转账失败'

    @allure.title ("验证锁仓账户和释放到账账户为同一个时质押扣费验证")
    @pytest.mark.parametrize ('amount,', [(5000000), (9100000)])
    def test_lockup_pledge(self, amount):
        '''
        验证锁仓账户和释放到账账户为同一个时锁仓质押扣费情况
        amount：质押金额
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)

        address1, private_key1 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            loukupbalace = Web3.toWei(9000000,'ether')
            plan = [{'Epoch': 1 ,'Amount':loukupbalace}]
            balance = platon_ppos.eth.getBalance(address1)

            lockup_before = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)

            #创建锁仓计划
            result =platon_ppos.CreateRestrictingPlan(address1,plan,private_key1,
                                              from_address=address1, gasPrice=self.gasPrice )
            assert result['status'] == True, "创建锁仓计划返回的状态：{},用例失败".format (result['status'])
            lockup_after = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
            assert lockup_after == lockup_before + loukupbalace,"锁仓计划金额{}".format(lockup_after)
            staking_befor = platon_ppos.eth.getBalance(conf.STAKINGADDRESS)

            if Web3.toWei(amount,'ether') < loukupbalace:
                # 发起质押
                nodeId = CommonMethod.read_out_nodeId('nocollusion')
                platon_ppos2 = Ppos (url, address1, self.chainid,private_key1)
                result = platon_ppos2.createStaking(1, address1, nodeId,'externalId', 'nodeName', 'website',                                                                        'details', amount,1792,gasPrice=self.gasPrice)
                assert result['status'] == True, "申请质押返回的状态：{},用例失败".format (result['status'])

                #质押账户余额增加
                staking_after = platon_ppos2.eth.getBalance(conf.STAKINGADDRESS)
                assert staking_after == staking_befor + Web3.toWei (amount, 'ether'),"质押账户余额：{}有误".format(staking_after)

                #锁仓合约地址余额减少
                lock_balance = platon_ppos2.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                assert lock_balance == lockup_after - Web3.toWei (amount, 'ether'),"锁仓合约余额：{}有误".format(lock_balance)

                #发起锁仓账户余额减少手续费
                pledge_balance_after = platon_ppos2.eth.getBalance(address1)
                assert balance > pledge_balance_after,"发起锁仓账户余额减少{}手续费有误".format(address1)
                RestrictingInfo = platon_ppos2.GetRestrictingInfo(address1)
                assert result['status'] == True, "查询锁仓信息返回的状态：{},用例失败".format (result['status'])

                #验证锁仓计划里的锁仓可用余额减少
                RestrictingInfo = json.loads(RestrictingInfo)
                assert loukupbalace == RestrictingInfo['Data']['balance'] + amount,"查询{}锁仓余额失败".format(address1)

            elif Web3.toWei(amount,'ether') >= loukupbalace:
                # 发起质押
                nodeId = CommonMethod.read_out_nodeId('nocollusion')
                platon_ppos2 = Ppos (url, address1, self.chainid,private_key1)
                result = platon_ppos2.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website',
                                                    'details', amount, 1792, gasPrice=self.gasPrice)
                assert result['status'] == False, "创建锁仓信息返回的状态：{},用例失败".format (result['status'])
            else:
                status = 1
                assert status == 0, "质押金额:{}有误".format(amount)
        else:
            status = 1
            assert status == 0, '创建锁仓计划失败'


    @allure.title ("验证锁仓账户和释放到账账户为不同时质押扣费验证")
    @pytest.mark.parametrize ('status,', [(1), (2)])
    def test_morelockup_pledge(self,status):
        '''
        验证锁仓账户和释放到账账户为不同时锁仓质押扣费情况
        amount：质押金额
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)

        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()


        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)

        if return_info is not None:
            balance = platon_ppos.eth.getBalance (address1)
            log.info ("发起锁仓账户余额:{}".format (balance))
            loukupbalace = Web3.toWei(9000000,'ether')
            plan = [{'Epoch': 1 ,'Amount':loukupbalace}]

            #创建锁仓计划
            result =platon_ppos.CreateRestrictingPlan(address2,plan,private_key1,
                                              from_address=address1, gasPrice=self.gasPrice )
            assert result['status'] == True, "创建锁仓信息返回的状态：{},用例失败".format (result['status'])
            RestrictingInfo = platon_ppos.GetRestrictingInfo(address2)
            assert RestrictingInfo['status'] == True, "创建锁仓信息返回的状态：{},用例失败".format (result['status'])

            if status == 1:
                # 锁仓账号发起质押
                result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                           Web3.toChecksumAddress (address2),
                                                           self.transfer_gasPrice, self.gas, self.value,
                                                           conf.PRIVATE_KEY)
                return_info = platon_ppos.eth.waitForTransactionReceipt (result)
                assert return_info is not None ,"转账失败"
                nodeId = CommonMethod.read_out_nodeId ('nocollusion')
                platon_ppos2 = Ppos (url, self.address, self.chainid)
                result = platon_ppos2.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website',
                                                     'details', 5000000, 1792, gasPrice=self.gasPrice)
                assert result['status'] == True, "申请质押返回的状态：{},用例失败".format (result['status'])

            if status == 2:
                # 锁仓账号发起质押
                nodeId = CommonMethod.read_out_nodeId ('nocollusion')
                platon_ppos2 = Ppos (url, self.address, self.chainid)
                result = platon_ppos2.createStaking (1, address2, nodeId, 'externalId', 'nodeName', 'website',
                                                     'details', 5000000, 1792, gasPrice=self.gasPrice)
                print(result)
                #assert result['status'] == False, "申请质押返回的状态：{},用例失败".format (result['status'])
        else:
            status = 1
            assert status == 0, '转账失败，用例执行失败'

    @allure.title ("验证锁仓账户和释放到账账户为同一个时委托扣费")
    @pytest.mark.parametrize ('amount,', [(500), (910)])
    def test_lockup_entrust(self,amount):
        '''
        锁仓账户和释放到账账户为同一个时委托扣费验证
        :param amount:
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        address1, private_key1 = CommonMethod.read_private_key_list ()
        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)

        if return_info is not None:
            balance = platon_ppos.eth.getBalance (address1)
            log.info ("发起锁仓账户余额:{}".format (balance))
            loukupbalace = Web3.toWei (900, 'ether')
            plan = [{'Epoch': 1, 'Amount': loukupbalace}]

            # 创建锁仓计划
            result = platon_ppos.CreateRestrictingPlan (address1, plan, private_key1,
                                                        from_address=address1, gasPrice=self.gasPrice)
            assert result['status'] == False, "创建锁仓计划返回的状态：{},用例失败".format (result['status'])
            lockup_after = platon_ppos.eth.getBalance (conf.FOUNDATIONLOCKUPADDRESS)
            RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
            assert RestrictingInfo['status'] == False, "查询锁仓计划返回的状态：{},用例失败".format (result['status'])
            assert RestrictingInfo['Data']['balance'] == loukupbalace

            #委托金额小于锁仓金额发起委托
            staking_befor = platon_ppos.eth.getBalance (conf.STAKINGADDRESS)
            if Web3.toWei (amount, 'ether') < loukupbalace:
                platon_ppos1 = Ppos (url, self.address, self.chainid)
                nodeId = CommonMethod.read_out_nodeId ('collusion')
                delegate_info = platon_ppos1.delegate(1,nodeId,amount)
                assert delegate_info['status'] == True, "查询锁仓计划返回的状态：{},用例失败".format (result['status'])                                #质押账户余额增加
                staking_after = platon_ppos1.eth.getBalance(conf.STAKINGADDRESS)
                assert staking_after == staking_befor +Web3.toWei (amount, 'ether'),"质押账户余额：{}".format(staking_after)
                #锁仓合约地址余额减少
                lock_balance = platon_ppos1.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                assert lock_balance == lockup_after - Web3.toWei (amount, 'ether'),"锁仓合约余额：{}".format(lock_balance)
            #委托金额大于锁仓金额发起委托
            elif Web3.toWei (amount, 'ether') >= loukupbalace:
                platon_ppos1 = Ppos (url, self.address, self.chainid)
                nodeId = CommonMethod.read_out_nodeId ('collusion')
                delegate_info = platon_ppos1.delegate (1,nodeId, amount)
                assert delegate_info['status'] == 'False'

            else:
                log.info ("委托金额:{}输入有误".format (amount))
        except:
            status = 1
            assert status == 0, '用例执行失败'

    @pytest.mark.parametrize ('code,', [(1), (2)])
    def test_morelockup_entrust(self, code):
        '''
        验证锁仓账户和释放到账账户为不同时锁仓委托扣费情况
        code：1、锁仓账户有余额支付委托手续费。2、锁仓账户没有余额支付委托手续费
        :return:
        '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = CommonMethod.ppos_link ()
        address1, private_key1 = CommonMethod.read_private_key_list ()
        address2, private_key2 = CommonMethod.read_private_key_list ()
        # 非签名转账
        self.ppos_sendTransaction (address1, self.address, 1000)
        # 签名转账
        # self.ppos_Girokonto(address1,self.address,self.privatekey,10000000)
        # platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
        #                                   Web3.toChecksumAddress (address1), self.gasPrice, self.gas, 10000000,
        #                                   conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        log.info ("发起锁仓账户余额:{}".format (balance))
        if balance == Web3.toWei (1000, 'ether'):
            try:
                loukupbalace = Web3.toWei (900, 'ether')
                plan = [{'Epoch': 1, 'Amount': loukupbalace}]
                # 创建锁仓计划
                result = platon_ppos.CreateRestrictingPlan (address2, plan, private_key1,
                                                            from_address=address1, gasPrice=self.gasPrice)
                if result['status'] == 'True':
                    log.info ("发起锁仓账户余额:{}".format (balance))
                    RestrictingInfo = platon_ppos.GetRestrictingInfo (address2)
                    if RestrictingInfo['status'] == 'True':
                        assert RestrictingInfo['Data']['balance'] == loukupbalace
                if code == 1:
                    CommonMethod.ppos_Girokonto (address2, self.address, self.privatekey, 100)
                    # 锁仓账号发起质押
                    nodeId = CommonMethod.read_out_nodeId ('collusion')
                    platon_ppos1 = CommonMethod.ppos_link (None, address1, private_key1)
                    delegate_info = platon_ppos1.delegate (1, nodeId, 500)
                    assert delegate_info['status'] == 'True'

                if code == 2:
                    nodeId = CommonMethod.read_out_nodeId ('collusion')
                    platon_ppos1 = CommonMethod.ppos_link (None, address1, private_key1)
                    delegate_info = platon_ppos1.delegate (1, nodeId, 500)
                    assert delegate_info['status'] == 'False'
            except:
                status = 1
                assert status == 0, '用例执行失败'


    # def test_loukupplan_amount(self):
    #     '''
    #     账户余额为0的时候调用锁仓接口
    #     :return:
    #     '''
    #     platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
    #                         privatekey=conf.PRIVATE_KEY)
    #     # platon_ppos = self.ppos_link ()
    #     address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
    #     privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
    #     try:
    #         loukupbalace = Web3.toWei (100, 'ether')
    #         plan = [{'Epoch': 1, 'Amount': loukupbalace}]
    #         result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
    #                                                     from_address=address1, gasPrice=self.gasPrice, gas=self.gas)
    #         assert result['status'] == 'false'
    #     except:
    #         status = 1
    #         assert status == 0, '创建锁仓计划失败'

if __name__ == '__main__':
    a = TestLockeDposition()
    #(1, 0.1), (-1, 3), (0.1, 3), (37, 3)
    a.test_loukupplan_amount()

