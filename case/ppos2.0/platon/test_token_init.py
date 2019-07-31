# -*- coding: utf-8 -*-

import json
import math
import time
import random

import allure
import pytest
from client_sdk_python import Web3
#from common.ppos import Ppos
from utils.platon_lib.ppos import Ppos
import inspect
from common.connect import connect_web3
from utils.platon_lib.dpos import PlatonDpos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info,get_node_list
from common import log
from deploy.deploy import AutoDeployPlaton
import json
from client_sdk_python.eth import Eth


class TestDposinit:
    address = Web3.toChecksumAddress(conf.ADDRESS)
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    gasPrice = Web3.toWei(0.000000000000000001,'ether')
    gas = 21000
    value = 1000
    initial_amount = {'FOUNDATION': 905000000000000000000000000,
                      'FOUNDATIONLOCKUP': 20000000000000000000000000,
                      'STAKING': 25000000000000000000000000,
                      'INCENTIVEPOOL': 45000000000000000000000000,
                      'DEVELOPERS': 5000000000000000000000000
                      }

    def ppos_link(self,url=None,address=conf.ADDRESS ,privatekey= conf.PRIVATE_KEY):
        if url is None:
            node_info = get_node_info (self.node_yml_path)
            self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
                'collusion')
            rpc_list_length = len (self.rpc_list) - 1
            index = random.randint (0, rpc_list_length)
            url = self.rpc_list[index]

        self.platon_ppos = Ppos (url, address=address, chainid=101,
                                 privatekey=privatekey)
        return self.platon_ppos

    def create_new_address(self,platon_ppos):
        self.new_address = platon_ppos.Web3.toChecksumAddress (
            self.ppos_link().web3.personal.newAccount (self.pwd))
        return self.new_address

    def read_private_key_list(self):
        with open (conf.PRIVATE_KEY_LIST, 'r') as f:
            private_key_list = f.read ().split ("\n")
            index = random.randrange (1, len (private_key_list) - 1)  # 生成随机行数
            address, private_key = private_key_list[index].split (',')
        return address, private_key

    # def update_config(self, file, key, data):
    #     with open(self.file, 'r', encoding='utf-8') as f:
    #         res = json.loads(f.read())

    def ppos_sendTransaction(self,to_address, from_address, gas, gasPrice, value):
        platon_ppos = self.ppos_link ()
        self.send_data = {
            "to": to_address,
            "from": from_address,
            "gas": gas,
            "gasPrice": gasPrice,
            "value": value,
        }
        a = platon_ppos.eth.estimateGas(self.send_data)
        tx_hash = platon_ppos.eth.sendTransaction (self.send_data)
        self.platon_ppos.eth.waitForTransactionReceipt (tx_hash)


    def setup_class(self):
        self.auto = AutoDeployPlaton (cbft=self.cbft_json_path)
        self.auto.start_all_node (self.node_yml_path)


    def test_init_token(self):
        '''
        验证链初始化后token各内置账户初始值
        :return:
        '''

        platon_ppos = self.ppos_link()
        FOUNDATION = platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONADDRESS))
        assert self.initial_amount['FOUNDATION'] == FOUNDATION
        FOUNDATIONLOCKUP = self.platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.FOUNDATIONLOCKUPADDRESS))
        assert self.initial_amount['FOUNDATIONLOCKUP'] == FOUNDATIONLOCKUP
        STAKING = self.platon_ppos.eth.getBalance(Web3.toChecksumAddress (conf.STAKINGADDRESS))
        assert self.initial_amount['STAKING'] == STAKING
        INCENTIVEPOOL = self.platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.INCENTIVEPOOLADDRESS))
        assert self.initial_amount['INCENTIVEPOOL'] == INCENTIVEPOOL
        DEVELOPERS = self.platon_ppos.eth.getBalance (Web3.toChecksumAddress (conf.DEVELOPERSADDRESS))
        assert self.initial_amount['DEVELOPERS'] == DEVELOPERS
        token_init_total = conf.TOKENTOTAL
        assert token_init_total == (FOUNDATION + FOUNDATIONLOCKUP + STAKING + INCENTIVEPOOL + DEVELOPERS)

    def test_transfer_normal(self):
        '''
        验证初始化之后账户之间转账
        :return:
        '''
        platon_ppos = self.ppos_link ()
        address1,private_key1 = self.read_private_key_list()

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
        address1 = '0x684b43Cf53C78aA567840174a55442d7a9282679'
        privatekey1 = 'a5ac52e828e2656309933339cf12d30755f918e368fffc7c265b55da718ff893'
        #账户2
        address2 = '0xc128fDBb500096974Db713b563dBeF597461C5dD'
        privatekey2 = 'c03975513e3de5b1c63fb4b31470111119d5ef1e580d14ebd23aee48f580ac13'
        balance = platon_ppos.eth.getBalance(address1)
        if balance == 0:
            try:
                platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (address1),
                                                  Web3.toChecksumAddress (address2), self.gasPrice, self.gas, self.value,
                                                  privatekey1)
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

    @allure.title ("查看初始化时锁仓余额和锁仓信息")
    def test_token_loukup(self):
        '''
        查询初始化链后基金会锁仓金额
        以及查询初始锁仓计划信息的有效性
        :return:
        '''
        #platon_ppos = self.ppos_link ()
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        lockupbalance = platon_ppos.eth.getBalance (conf.FOUNDATIONLOCKUPADDRESS)
        FOUNDATIONLOCKUP = self.initial_amount['FOUNDATIONLOCKUP']
        assert lockupbalance == FOUNDATIONLOCKUP
        result = platon_ppos.GetRestrictingInfo(conf.INCENTIVEPOOLADDRESS)
        if result['Status'] == 'True' :
            assert result['Date']['balance'] == self.initial_amount['FOUNDATIONLOCKUP']
        else:
            log.info("初始锁仓金额:{}，锁仓计划信息查询结果有误".format(lockupbalance))

    def test_loukupplan(self):
        '''
        验证正常锁仓功能
        参数输入：
        Epoch：1
        Amount：50 ether
        :return:
        '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                                 privatekey=conf.PRIVATE_KEY)
        #platon_ppos = self.ppos_link ()
        address1 = '0x472599739f398c24ad8Cdc03476b20D6469eAf46'
        privatekey1 = '61279a4b654aef7c3065c0cf550cdce460682875c218de893544a4799b57cc41'
        #非签名转账
        # platon_ppos.web3.personal.unlockAccount(conf.ADDRESS, conf.PASSWORD, 2222)
        # self.ppos_sendTransaction(address1,conf.ADDRESS,self.gas,self.gasPrice,Web3.toWei(10000,'ether'))
        #签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas,self.value,
                                          conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        log.info("发起锁仓账户的余额:{}",balance)
        if balance > 0:
            try:
                loukupbalace = Web3.toWei(50,'ether')
                plan = [{'Epoch': 1 ,'Amount':loukupbalace}]
                lockup_before = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                #创建锁仓计划
                result =platon_ppos.CreateRestrictingPlan(address1,plan,privatekey1,
                                                  from_address=address1, gasPrice=self.gasPrice )
                if result['status'] == 'True':
                    lockup_after = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                    assert lockup_after == lockup_before + loukupbalace
                else:
                    log.info("创建锁仓计划失败")
            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'
            #查看锁仓计划明细
            detail = RestrictingInfo = platon_ppos.GetRestrictingInfo(address1)
            if detail['status'] == 'True':
                assert RestrictingInfo['balance'] == loukupbalace
            else:
                log.info("查询锁仓计划信息返回状态为:{}".format(result['status']))



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
        address1 = '0x9148528b98a0065D185F01dbc59baB88CdbE7Ad2'
        private_key1 = '6ccbf153f7409af1e5df7a1ef77daaca4759f0a6b50ef73fe9ccd5738cc2fda1'
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        try:
            loukupbalace = Web3.toWei (amount, 'ether')
            plan = [{'Epoch': number, 'Amount': loukupbalace}]
            #当锁仓金额输入小于 1ether
            if number >= 1 and amount < 1:
                result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                            from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == 'false'
            #当锁仓解锁期输入非正整数倍
            elif number < 0 or type (number) == float:
                result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                            from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == 'false'
            #当锁仓解锁期大于36个结算期
            elif number > 36:
                result = platon_ppos.CreateRestrictingPlan (address1, plan, conf.PRIVATE_KEY,
                                                            from_address=conf.ADDRESS, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == 'false'

        except:
            status = 1
            assert status == 0, '创建锁仓计划失败'


    @allure.title ("锁仓金额大于账户余额")
    def test_loukupplan_amount(self):
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
        # 签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas,self.value,conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        if balance > 0 :
            try:
                loukupbalace = Web3.toWei (10000, 'ether')
                plan = [{'Epoch': 1, 'Amount': loukupbalace}]
                result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                            from_address=address1, gasPrice=self.gasPrice, gas=self.gas)
                assert result['status'] == 'false'
            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'
        else:
            log.info('error:转账失败')

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
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
        # 签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas,self.value,conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        if balance > 0 :
            try:
                loukupbalace1 = Web3.toWei (balace1, 'ether')
                loukupbalace2 = Web3.toWei (balace2, 'ether')
                if  (loukupbalace1 + loukupbalace2) < self.value:
                    plan = [{'Epoch': 1, 'Amount': loukupbalace1},{'Epoch': 2, 'Amount': loukupbalace2}]
                    result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                                from_address=address1, gasPrice=self.gasPrice, gas=self.gas)
                    assert result['status'] == 'True'
                elif self.value <= (loukupbalace1 + loukupbalace2) :
                    plan = [{'Epoch': 1, 'Amount': loukupbalace1}, {'Epoch': 2, 'Amount': loukupbalace2}]
                    result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                                from_address=address1, gasPrice=self.gasPrice,
                                                                gas=self.gas)
                    assert result['status'] == 'false'
                else:
                    log.info('锁仓输入的金额:{}出现异常'.format((loukupbalace1+loukupbalace2)))

            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'
        else:
            log.info('error:转账失败')

    @allure.title ("锁仓计划多个相同解锁期情况验证")
    @pytest.mark.parametrize ('code,', [(1),(2)])
    def test_loukupplan_sameperiod(self, code):
        '''
        验证一个锁仓计划里有多个相同解锁期
        code =1 :同个account在一个锁仓计划里有相同解锁期
        code =2 :同个account在不同锁仓计划里有相同解锁期
        :return:
        '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
        # 签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas, self.value,
                                          conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        if balance > 0:
            try:
                period1 = 1
                period2 = 2
                loukupbalace = Web3.toWei (100, 'ether')
                if code == 1:
                    plan = [{'Epoch': period1, 'Amount': loukupbalace}, {'Epoch': period1, 'Amount': loukupbalace}]
                    result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                                from_address=address1, gasPrice=self.gasPrice,
                                                                gas=self.gas)
                    assert result['status'] == 'True'
                    RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
                    json_data = json.loads(RestrictingInfo['Data'])
                    assert json_data['Entry'][0]['amount'] == (loukupbalace + loukupbalace)

                elif code == 2:
                    plan = [{'Epoch': period1, 'Amount': loukupbalace}, {'Epoch': period2, 'Amount': loukupbalace}]
                    result = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                                from_address=address1, gasPrice=self.gasPrice,
                                                                gas=self.gas)
                    assert result['status'] == 'True'
                    loukupbalace2 = Web3.toWei (200, 'ether')
                    plan = [{'Epoch': period1, 'Amount': loukupbalace2}, {'Epoch': period2, 'Amount': loukupbalace2}]
                    result1 = platon_ppos.CreateRestrictingPlan (address1, plan, privatekey1,
                                                                from_address=address1, gasPrice=self.gasPrice,
                                                                gas=self.gas)
                    assert result1['status'] == 'True'
                    RestrictingInfo = platon_ppos.GetRestrictingInfo (address1)
                    json_data = json.loads (RestrictingInfo['Data'])
                    assert json_data['Entry'][0]['amount'] == (loukupbalace + loukupbalace2)
                else:
                    log.info('输入的code:{}有误'.format(code))
            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'
        else:
            log.info('error:转账失败')

    @allure.title ("验证锁仓账户和释放到账账户为同一个时质押扣费验证")
    @pytest.mark.parametrize ('amount,', [(5000000), (9100000)])
    def test_lockup_pledge(self, amount):
        '''
        验证锁仓账户和释放到账账户为同一个时锁仓质押扣费情况
        amount：质押金额
        :return:
        '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
        # 签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas, 10000000,
                                          conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        log.info("发起锁仓账户余额:{}".format(balance))
        if balance == Web3.toWei (10000000, 'ether'):
            try:
                loukupbalace = Web3.toWei(9000000,'ether')
                plan = [{'Epoch': 1 ,'Amount':loukupbalace}]
                lockup_before = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                #创建锁仓计划
                result =platon_ppos.CreateRestrictingPlan(address1,plan,privatekey1,
                                                  from_address=address1, gasPrice=self.gasPrice )
                if result['status'] == 'True':
                    log.info ("发起锁仓账户余额:{}".format (balance))
                    lockup_after = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                    assert lockup_after == lockup_before + loukupbalace
                    staking_befor = platon_ppos.eth.getBalance(conf.STAKINGADDRESS)
                    if Web3.toWei(amount,'ether') < loukupbalace:
                        #发起质押
                        node_info = get_node_info (conf.TWENTY_FIVENODE_YML)
                        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get_node_info (
                            'nocollusion')
                        node_list_length = len (self.node_list)
                        index = random.randint (0, node_list_length - 1)
                        nodeId = self.node_list[index]
                        platon_ppos2 = self.ppos_link (None,address1,privatekey1)
                        result = platon_ppos2.createStaking(1, address1, nodeId,'externalId', 'nodeName', 'website', 'details',                                                              amount,1792,gasPrice=self.gasPrice)
                        if result['status'] == 'True':
                            #质押账户余额增加
                            staking_after = platon_ppos2.eth.getBalance(conf.STAKINGADDRESS)
                            assert staking_after == staking_befor + Web3.toWei (amount, 'ether')
                            #锁仓合约地址余额减少
                            lock_balance = platon_ppos2.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                            assert lock_balance == lockup_after - Web3.toWei (amount, 'ether')
                            #发起锁仓账户余额减少手续费
                            pledge_balance_after = platon_ppos2.eth.getBalance()
                            assert balance > pledge_balance_after
                            RestrictingInfo = platon_ppos2.GetRestrictingInfo(address1)
                            if RestrictingInfo['status'] == 'True':
                                #验证锁仓计划里的锁仓可用余额减少
                                assert loukupbalace == RestrictingInfo['Data']['balance'] + amount
                            else:
                                log.info("查询{}锁仓余额失败".format(address1))
                        else:
                            log.info("质押节点:{}失败".format(nodeId))
                    elif Web3.toWei(amount,'ether') >= loukupbalace:
                        # 发起质押
                        node_info = get_node_info (conf.TWENTY_FIVENODE_YML)
                        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
                            'nocollusion')
                        node_list_length = len (self.node_list)
                        index = random.randint (0, node_list_length - 1)
                        nodeId = self.node_list[index]
                        platon_ppos2 = self.ppos_link (None, address1, privatekey1)
                        result = platon_ppos2.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website',
                                                            'details', amount, 1792, gasPrice=self.gasPrice)
                        assert result['status'] == 'False'
                    else:
                        log.info("质押金额:{}有误".format(amount))
                else:
                    log.info("创建锁仓计划,状态为{}".format(result['status']))
            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'

    @allure.title ("验证锁仓账户和释放到账账户为不同时质押扣费验证")
    @pytest.mark.parametrize ('amount,', [(5000000), (9100000)])
    def test_morelockup_pledge(self):
        '''
                验证锁仓账户和释放到账账户为同一个时锁仓质押扣费情况
                amount：质押金额
                :return:
                '''
        platon_ppos = Ppos ('http://10.10.8.157:6789', self.address, chainid=102,
                            privatekey=conf.PRIVATE_KEY)
        # platon_ppos = self.ppos_link ()
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
        # 签名转账
        platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                          Web3.toChecksumAddress (address1), self.gasPrice, self.gas, 10000000,
                                          conf.PRIVATE_KEY)
        balance = platon_ppos.eth.getBalance (address1)
        log.info ("发起锁仓账户余额:{}".format (balance))
        if balance == Web3.toWei (10000000, 'ether'):
            try:
                loukupbalace = Web3.toWei(9000000,'ether')
                plan = [{'Epoch': 1 ,'Amount':loukupbalace}]
                lockup_before = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                #创建锁仓计划
                result =platon_ppos.CreateRestrictingPlan(address1,plan,privatekey1,
                                                  from_address=address1, gasPrice=self.gasPrice )
                if result['status'] == 'True':
                    log.info ("发起锁仓账户余额:{}".format (balance))
                    lockup_after = platon_ppos.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
                    assert lockup_after == lockup_before + loukupbalace
            except:
                status = 1
                assert status == 0, '创建锁仓计划失败'


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
        address1 = '0x51a9A03153a5c3c203F6D16233e3B7244844A457'
        privatekey1 = '25f9fdf3249bb47f239df0c59d23781c271e8b7e9a94e9e694c15717c1941502'
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
    a.test_transfer_normal()
    #a.test_punishment_income()