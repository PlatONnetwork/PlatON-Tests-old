# -*- coding: utf-8 -*-
"""
@Author: wuyiqin
@Date: 2019/8/16 11:45
@Description:主要是ppos委托的用例
"""
import json
import math
import time
import allure
import pytest
from client_sdk_python import Web3
from common.connect import connect_web3
from utils.platon_lib.ppos_wyq import Ppos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info
from common import log
from deploy.deploy import AutoDeployPlaton
from client_sdk_python.personal import (
    Personal,
)
from hexbytes import HexBytes
from client_sdk_python.eth import Eth
from utils.platon_lib.ppos_tool import get_config_data


class TestDelegate():
    node_yml_path = conf.NODE_YML
    node_info = get_node_info(node_yml_path)
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get(
        'collusion')
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get(
        'nocollusion')

    address = Web3.toChecksumAddress(conf.ADDRESS)
    privatekey = conf.PRIVATE_KEY
    account_list = conf.account_list
    privatekey_list = conf.privatekey_list
    externalId = "1111111111"
    nodeName = "platon"
    website = "https://www.test.network"
    details = "supper node"
    programVersion = 1792
    illegal_nodeID = conf.illegal_nodeID
    genesis_path = conf.GENESIS_TMP


    """替换config.json"""
    get_config_data()
    config_json_path = conf.PLATON_CONFIG_PATH
    config_dict = LoadFile(config_json_path).get_data()
    amount_delegate = Web3.fromWei(
        int(config_dict['EconomicModel']['Staking']['MinimumThreshold']), 'ether')
    amount = Web3.fromWei(
        int(config_dict['EconomicModel']['Staking']['StakeThreshold']), 'ether')


    def setup_class(self):
        self.auto = AutoDeployPlaton()
        self.auto.start_all_node(self.node_yml_path)
        self.genesis_dict = LoadFile(self.genesis_path).get_data()
        self.chainid = int(self.genesis_dict["config"]["chainId"])
        self.ppos_link = Ppos(
            self.rpc_list[0],self.address,self.chainid)
        self.w3_list = [connect_web3(url) for url in self.rpc_list]
        """用新的钱包地址和未质押过的节点id封装对象"""
        self.ppos_noconsensus_1 = Ppos(self.rpc_list[0], self.account_list[0],self.chainid,privatekey=self.privatekey_list[0])
        self.ppos_noconsensus_2 = Ppos(self.rpc_list[0], self.account_list[1],self.chainid,privatekey=self.privatekey_list[1])
        self.ppos_noconsensus_3 = Ppos(self.rpc_list[0], self.account_list[2],self.chainid,privatekey=self.privatekey_list[2])
        self.ppos_noconsensus_4 = Ppos(self.rpc_list[0], self.account_list[3],self.chainid,privatekey=self.privatekey_list[3])
        self.ppos_noconsensus_5 = Ppos(self.rpc_list[0], self.account_list[4],self.chainid,privatekey=self.privatekey_list[4])
        self.ppos_noconsensus_6 = Ppos(self.rpc_list[0], self.account_list[5],self.chainid,privatekey=self.privatekey_list[5])
        self.eth = Eth(self.w3_list[0])


    def transaction(self,w3, from_address, to_address=None,value=1000000000000000000000000000000000,
                    gas=91000000, gasPrice=9000000000,pwd=conf.PASSWORD):
        """"
        转账公共方法
        """
        personal = Personal(w3)
        personal.unlockAccount(from_address, pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': gas,
            'gasPrice': gasPrice,
            'value': value
        }
        tx_hash = w3.eth.sendTransaction(params)
        result = w3.eth.waitForTransactionReceipt(HexBytes(tx_hash).hex())
        return result


    def getCandidateList(self):
        """
        获取实时验证人的nodeID list
        """
        msg = self.ppos_noconsensus_1.getCandidateList()
        recive_list = msg.get("Data")
        nodeid_list = []
        if recive_list is None:
            return recive_list
        else:
            for node_info in recive_list:
                nodeid_list.append(node_info.get("NodeId"))
        return nodeid_list


    @allure.title("委托金额分别为{amount}")
    @pytest.mark.parametrize('amount', [amount_delegate-1, 0])
    def test_illege_delegate(self,amount):
        """
        用例id 委托金额小于门槛
        """
        log.info("转账每个钱包")
        for to_account in self.account_list:
            self.transaction(self.w3_list[0],self.address,to_address=to_account)
        log.info("质押节点1：{}成为验证人".format(self.nodeid_list2[0]))

        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("钱包2委托金额".format(amount))
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
        log.info(msg)
        assert msg.get("Status") == False,"委托金额异常"


    @allure.title("质押过的钱包委托失败")
    def test_delegate_verifier(self):
        """
        测试质押过的钱包不能去委托
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        amount = self.amount_delegate
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg['Data']!= "":
            log.info("质押过的钱包1不能再去质押")
            msg = self.ppos_noconsensus_1.delegate(0, self.nodeid_list2[0], amount)
            # print(msg)
            assert msg.get("Status") == False
            msg_string = "is not allowed to be used for delegating"
            assert msg_string in msg["ErrMsg"], "质押过的钱包不能进行质押出现异常"
        else:
            log.info("质押节点1：{}成为验证人".format(self.nodeid_list2[0]))
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
            log.info("质押过的钱包1不能再去质押")
            msg = self.ppos_noconsensus_1.delegate(0, self.nodeid_list2[0], amount)
            assert msg.get("Status") == False
            log.info(msg)
            msg_string = "is not allowed to be used for delegating"
            assert msg_string in msg["ErrMsg"], "质押过的钱包不能进行质押出现异常"


    @allure.title("发起委托成功")
    def test_delegate(self):
        """
        用例id 95 委托成功，查询节点信息，金额
        用例id 98 委托人与验证人验证，验证人存在
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        amount = self.amount_delegate
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg['Data']!= "":
            log.info("钱包2委托节点1")
            msg = self.ppos_noconsensus_2.delegate(0,self.nodeid_list2[0],amount)
            assert msg.get("Status") == True
            assert msg.get("ErrMsg") == 'ok'
        else:
            log.info("质押节点1：{}成为验证人".format(self.nodeid_list2[0]))
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
            msg = self.ppos_noconsensus_2.delegate(0,self.nodeid_list2[0],amount)
            assert msg.get("Status") == True
            assert msg.get("ErrMsg") == 'ok'


    @allure.title("查询当前单个委托信息")
    def test_getDelegateInfo(self):
        """
        用例id 94 查询当前单个委托信息
        """

        log.info("转账到钱包5")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[4])
        log.info("转账到钱包6")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[5])

        log.info("质押节点5成为验证人")
        self.ppos_noconsensus_5.createStaking(0, self.account_list[4], self.nodeid_list2[4],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        msg = self.ppos_noconsensus_6.delegate(0, self.nodeid_list2[4], self.amount_delegate)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'
        log.info("查询质押节点5信息")
        msg = self.ppos_noconsensus_5.getCandidateInfo(self.nodeid_list2[4])
        assert msg["Data"]["NodeId"] == self.nodeid_list2[4]
        log.info("查询质押+委托的金额正确")
        assert Web3.fromWei(msg["Data"]["Shares"], 'ether') == self.amount + self.amount_delegate
        assert Web3.fromWei(msg["Data"]["ReleasedHes"], 'ether') == self.amount
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("质押的块高{}".format(stakingBlockNum))
        msg = self.ppos_noconsensus_6.getDelegateInfo(stakingBlockNum, self.account_list[5], self.nodeid_list2[4])
        data = msg["Data"]
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[5]
        assert data["NodeId"] == self.nodeid_list2[4]
        assert Web3.fromWei(data["ReleasedHes"], 'ether') == self.amount_delegate


    @allure.title("余额不足委托失败")
    def test_insufficient_delegate(self):
        """
        用例96 余额不足委托失败
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        amount = 1000000000000000000000000000000
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg['Data']!= "":
            msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
            # print(msg)
            assert msg.get("Status") == False
            assert msg.get("ErrMsg") == 'Delegate failed: The von of account is not enough'
        else:
            log.info("质押节点1：{}成为验证人".format(self.nodeid_list2[0]))
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
            msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
            # print(msg)
            assert msg.get("Status") == False
            assert msg.get("ErrMsg") == 'Delegate failed: The von of account is not enough'


    @allure.title("验证人不存在进行委托")
    def test_not_nodeId_delegate(self):
        """
        用例72 验证人不存在进行委托
        """
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        value = self.amount_delegate
        nodeid = conf.illegal_nodeID
        msg = self.ppos_noconsensus_2.delegate(0, nodeid, value)
        print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'This candidate is not exist'


    @allure.title("验证人退出后，委托人信息还存在")
    def test_back_unStaking_commissioned(self):
        """
        用例id 82 验证人申请退回质押金，委托金额还生效
        用例id 83 验证人退出后，委托人信息还存在
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg['Data']== "":
            log.info("节点1再次成为验证人")
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
            log.info("钱包2进行委托100")
            self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], 100)
            log.info("节点1退出验证人")
            self.ppos_noconsensus_1.unStaking(self.nodeid_list2[0])
            msg = self.ppos_noconsensus_2.getDelegateListByAddr(self.account_list[1])
            log.info(msg)
            StakingBlockNum = msg["Data"][0]["StakingBlockNum"]
            msg = self.ppos_noconsensus_2.getDelegateInfo(StakingBlockNum,self.account_list[1],self.nodeid_list2[0])
            log.info(msg)
            data = msg["Data"]
            data = json.loads(data)
            log.info(data)
            assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[1]
            assert data["NodeId"] == self.nodeid_list2[0]
        else:
            log.info("钱包2进行委托100")
            self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], 100)
            log.info("节点1退出验证人")
            self.ppos_noconsensus_1.unStaking(self.nodeid_list2[0])
            msg = self.ppos_noconsensus_2.getDelegateListByAddr(self.account_list[1])
            log.info(msg)
            StakingBlockNum = msg["Data"][0]["StakingBlockNum"]
            msg = self.ppos_noconsensus_2.getDelegateInfo(StakingBlockNum,self.account_list[1],self.nodeid_list2[0])
            log.info(msg)
            data = msg["Data"]
            data = json.loads(data)
            log.info(data)
            assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[1]
            assert data["NodeId"] == self.nodeid_list2[0]



    @allure.title("验证节点退出后，再成为验证节点,钱包委托信息有2个")
    def test_identifier_quit_delegate(self):
        """
        委托验证节点，验证节点退出后，再成为验证节点，再去委托：预期有2个委托消息
        """
        log.info("转账到钱包3")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[2])
        log.info("转账到钱包4")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[3])

        log.info("质押节点3：{}成为验证节点".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("钱包4:{}进行委托".format(self.account_list[3]))
        self.ppos_noconsensus_4.delegate(0,self.nodeid_list2[2],50)
        log.info("质押节点3退出验证人{}".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.unStaking(self.nodeid_list2[2])
        log.info("{}再次成为验证人".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2],self.nodeid_list2[2],self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        log.info("钱包4:{}再次进行委托".format(self.account_list[3]))
        msg = self.ppos_noconsensus_4.delegate(0,self.nodeid_list2[2],100)
        print(msg)
        log.info("查询钱包的委托情况")
        msg = self.ppos_noconsensus_4.getDelegateListByAddr(self.account_list[3])
        log.info(msg)
        log.info(msg["Data"])
        print(len(msg["Data"]))
        assert len(msg["Data"]) == 2
        for i in msg["Data"]:
            assert Web3.toChecksumAddress(i["Addr"]) == self.account_list[3]
            assert i["NodeId"] == self.nodeid_list2[2]



    @allure.title("使用锁仓账户中的Token进行创建验证人申请退回质押金")
    def test_restrictingPlan_unStaking(self):
        """
        用例id 83 使用锁仓账户中的Token进行创建验证人申请退回质押金
        """
        pass



    def test_restrictingPlan_delegate(self):
        """
        用例id 101 委托人使用锁仓Token进行委托
        """
        pass



    def test_restrictingPlan_insufficient_delegate(self):
        """
        用例id 103委托人使用锁仓Token（余额不足）进行委托
        """
        pass








