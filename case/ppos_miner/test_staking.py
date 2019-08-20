# -*- coding: utf-8 -*-
"""
@Author: wuyiqin
@Date: 2019/8/16 11:45
@Description:主要是ppos初始验证人和质押用例
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
from utils.platon_lib.ppos_tool import get_block_number,get_config_data


class TestStaking():
    node_yml_path = conf.NODE_YML
    node_info = get_node_info(node_yml_path)
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get(
        'collusion')
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get(
        'nocollusion')

    address = Web3.toChecksumAddress(conf.ADDRESS)
    pwd = conf.PASSWORD
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
        self.ppos_link1 = Ppos(
            self.rpc_list[1],self.address,self.chainid)
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
                    gas=91000000, gasPrice=9000000000,pwd ="88888888"):
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

#############################初始验证人############################################

    @allure.title("校验初始验证人信息")
    def test_initial_identifier(self):
        """
        用例id 54,55
        测试验证人参数有效性验证
        """
        recive = self.ppos_link.getVerifierList()
        nodeid_list = []
        for node_info in recive.get("Data"):
            nodeid_list.append(node_info.get("NodeId"))
            StakingAddress = node_info.get("StakingAddress")
            StakingAddress = ( Web3.toChecksumAddress(StakingAddress))
            assert StakingAddress == self.address,"内置钱包地址错误{}".format(StakingAddress)
        assert self.nodeid_list == nodeid_list, "正常的nodeID列表{},异常的nodeID列表{}".format(self.nodeid_list,nodeid_list)


    @allure.title("验证人不能接受委托")
    def test_initial_cannot_entrust(self):
        """
        用例id 56 初始验证人不能接受委托
        """
        msg = self.ppos_link.delegate(typ = 0,nodeId=self.nodeid_list[0],amount=50)
        assert msg.get("Status") == False ,"返回状态错误"
        msg_string = "Delegate failed: Account of Candidate(Validator)  is not allowed to be used for delegating"
        assert msg.get("ErrMsg") == msg_string,"返回提示语错误"


    @allure.title("验证人增持质押")
    def test_initial_add_pledge(self):
        """
        用例id 57 初始验证人增持质押
        """
        value = 1000
        print(self.nodeid_list[0])
        msg = self.ppos_link.addStaking(nodeId=self.nodeid_list[0],typ=0,amount=value)
        assert msg.get("Status") == True ,"初始验证人增持质押失败"
        assert msg.get("ErrMsg") == 'ok',"返回消息错误"
        msg = self.ppos_link.getCandidateInfo(self.nodeid_list[0])
        assert  msg["Data"]["NodeId"] == self.nodeid_list[0]
        assert self.amount+value == Web3.fromWei(msg["Data"]["Shares"], 'ether'),"增持+质押金额异常"
        assert self.amount == Web3.fromWei(msg["Data"]["Released"], 'ether'),"锁定期质押金额异常"
        assert value == Web3.fromWei(msg["Data"]["ReleasedHes"], 'ether'),"犹豫期质押金额异常"
        assert msg.get("Status") == True ,"返回状态错误"
        assert msg.get("ErrMsg") == 'ok',"返回消息错误"


    @allure.title("初始验证人退出与重新质押")
    def test_initial_quit(self):
        """
        用例id 58 初始验证人退出
        初始验证人退出验证节点后，不能在锁定期内再质押
        初始验证人结束锁定期后，重新质押
        """
        msg = self.ppos_link.unStaking(self.nodeid_list[0])
        assert msg.get("Status") ==True ,"返回状态错误"
        assert msg.get("ErrMsg") == 'ok',"返回消息错误"
        print(self.nodeid_list[0])
        """需要等到锁定期的下一个结算周期结束后才没看到验证人消息"""
        node_list = self.getCandidateList()
        assert self.nodeid_list[0] not in node_list,"初始验证人还没退出"
        log.info("查询节点的质押情况")
        msg = self.ppos_link.getCandidateInfo(self.nodeid_list[0])
        assert msg.get("Status") == True, "返回状态错误"
        assert msg["Data"]["NodeId"] == self.nodeid_list[0],"验证人信息异常不存在了"

        msg = self.ppos_link.createStaking(0, self.address,self.nodeid_list[0],self.externalId,self.nodeName,
                                           self.website, self.details,self.amount,self.programVersion)
        assert msg.get("Status") == False, "返回状态错误"
        log.info("进入下个结算周期")
        get_block_number(self.w3_list[0])
        msg = self.ppos_link.createStaking(0, self.address,self.nodeid_list[0],self.externalId,self.nodeName,
                                           self.website, self.details,self.amount,self.programVersion)
        assert msg.get("Status") == False,"在退回需要再锁一个周期，但没生效"
        log.info("进入下个结算周期")
        get_block_number(self.w3_list[0])
        msg = self.ppos_link.createStaking(0, self.address,self.nodeid_list[0],self.externalId,self.nodeName,
                                           self.website, self.details,self.amount,self.programVersion)
        log.info(msg)
        assert msg.get("Status") == True, "返回状态错误"



############################质押#######################################################

    # @allure.title("钱包余额为0做质押")
    # def test_not_sufficient_funds_staking(self):
    #     benifitAddress = conf.no_money[1]
    #     nodeId = self.nodeid_list2[0]
    #     status = 0
    #     try:
    #         self.ppos_noconsensus_1.createStaking(0, benifitAddress,
    #                                                 nodeId, self.externalId, self.nodeName, self.website, self.details,
    #                                                 self.amount, self.programVersion)
    #     except:
    #         status = 1
    #     assert status == 1, '钱包余额为0发起质押预期是异常，实际成功'


    @allure.title("质押{x}小于最低门槛")
    @pytest.mark.parametrize('x', [0, amount-1])
    def test_iff_staking(self,x):
        """
        用例 64 非初始验证人做质押,质押金额小于最低门槛
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        benifitAddress = self.account_list[0]
        nodeId = self.nodeid_list2[0]
        msg = self.ppos_noconsensus_1.createStaking(0, benifitAddress,
                                           nodeId,self.externalId,self.nodeName, self.website, self.details,x,self.programVersion)
        log.info(msg)
        if x == self.amount-1:
            assert msg.get("Status") == False, "返回状态错误"
            assert msg.get("ErrMsg") == "Staking deposit too low"
        if x == 0:
            assert msg.get("Status") == False, "返回状态错误"


    @allure.title("非初始验证人做质押")
    def test_staking(self):
        """
        用例 62 非初始验证人质押刚到门槛
        """
        self.transaction(self.w3_list[0],self.address,to_address=self.account_list[0])
        log.info("转账到钱包1")
        nodeId = self.nodeid_list2[0]
        log.info("节点1成为验证人")
        account_before = self.eth.getBalance(self.account_list[0])
        msg = self.ppos_noconsensus_1.createStaking(0, self.account_list[0],
                                           nodeId,self.externalId,self.nodeName, self.website,self.details,
                                                    self.amount,self.programVersion)
        assert msg.get("Status") == True, "返回状态错误"
        assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        account_after = self.eth.getBalance(self.account_list[0])
        assert account_before > account_after + Web3.toWei(self.amount, "ether")
        msg = self.ppos_noconsensus_1.getCandidateInfo(nodeId=nodeId)
        assert Web3.fromWei(msg["Data"]["Shares"], 'ether') == self.amount
        nodeid_list = self.getCandidateList()
        assert nodeId in nodeid_list,"非初始验证人质押失败"


    @allure.title("非链上的nodeID去质押")
    def test_illegal_pledge(self):
        """
        用例id 63 非链上的nodeID去质押
        """
        benifitAddress = self.account_list[1]
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=benifitAddress)
        log.info("不存在链上的nodeID去质押")
        msg = self.ppos_noconsensus_2.createStaking(0, benifitAddress,self.illegal_nodeID,self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        # print(msg)
        assert msg.get("Status") ==True ,"返回状态错误"
        assert msg.get("ErrMsg") == 'ok',"返回消息错误"
        msg = self.ppos_noconsensus_2.getCandidateInfo(nodeId=self.illegal_nodeID)
        assert Web3.fromWei(msg["Data"]["Shares"], 'ether') == self.amount


    @allure.title("质押过的钱包二次质押")
    def test_account_staking_twice(self):
        """
        质押过的钱包二次质押
        """
        log.info("转账到钱包3")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[2])
        log.info("节点3去成为验证人")
        msg = self.ppos_noconsensus_3.createStaking(0, self.account_list[2],self.nodeid_list2[2],self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        assert msg.get("Status") ==True ,"返回状态错误"

        log.info("用质押过的钱包和未质押的节点id做一笔质押")
        log.info("钱包3质押给节点6")
        nodeId = self.nodeid_list2[5]
        log.info("用质押过的钱包3，质押节点6成为验证人")
        msg = self.ppos_noconsensus_3.createStaking(0, self.account_list[2],
                                           nodeId,self.externalId,self.nodeName, self.website,self.details,
                                                    self.amount,self.programVersion)
        assert msg.get("Status") ==True ,"返回状态错误"
        assert msg.get("ErrMsg") == 'ok',"质押过的钱包二次质押失败"
        nodeID_list = self.getCandidateList()
        log.info(nodeID_list)
        log.info(self.nodeid_list2[5])
        assert self.nodeid_list2[5] in nodeID_list,"nodeID不在列表中"


    @allure.title("质押过的节点再次质押")
    def test_nodeID_staking_twice(self):
        """
        质押过的节点再次质押
        """
        log.info("转账到钱包4")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[3])
        log.info("节点4去成为验证人")
        nodeId = self.nodeid_list2[3]
        msg = self.ppos_noconsensus_4.createStaking(0, self.account_list[3],nodeId,self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        assert msg.get("Status") == True, "返回状态错误"
        self.transaction(self.w3_list[0],self.address,to_address=self.account_list[5])
        log.info("转账到钱包6,用钱包6质押节点4")
        msg = self.ppos_noconsensus_6.createStaking(0, self.account_list[5],nodeId,self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        assert msg.get("Status") ==False ,"返回状态错误"
        assert msg.get("ErrMsg") == "This candidate is already exists"
        msg = self.ppos_noconsensus_4.getCandidateInfo(nodeId=self.nodeid_list2[3])
        assert Web3.fromWei(msg["Data"]["Shares"], 'ether')== self.amount


    @allure.title("验证人申请退回质押金")
    def test_back_unStaking(self):
        """
        用例id 81 验证人申请退回质押金
        """
        log.info("转账到钱包5")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[4])
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[4])
        if msg['Data']== "":
            log.info("质押节点5成为验证人")
            self.ppos_noconsensus_5.createStaking(0, self.account_list[4], self.nodeid_list2[4],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
        account_before = self.eth.getBalance(self.account_list[4])
        log.info("节点5对应的钱包余额{}".format(account_before))
        log.info("节点5退出质押{}".format(self.nodeid_list2[4]))
        msg = self.ppos_noconsensus_5.unStaking(self.nodeid_list2[4])
        log.info(msg)
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[4])
        if msg['Data'] != "":
            log.info("进入到锁定期")
            get_block_number(self.w3_list[0])
            log.info("进入解锁期")
            get_block_number(self.w3_list[0])
        account_after = self.eth.getBalance(self.account_list[4])
        log.info("节点5退出质押后钱包余额{}".format(account_after))
        assert account_after > account_before,"退出质押后，钱包余额未增加"
        log.info("因为质押消耗的gas值大于撤销质押的gas值")
        assert 900000000000000000000000 < account_after - account_before < 1000000000000000000000000
        node_list = self.getCandidateList()
        assert self.nodeid_list2[4] not in node_list, "验证节点退出异常"
        log.info("{}已经退出验证人".format(self.nodeid_list2[4]))



    # @allure.title("质押和增持后的余额正常")
    # def test_balance_by_staking_addstaking(self):
    #     """
    #     测试质押和增持后的余额正常
    #     """
    #     self.auto = AutoDeployPlaton()
    #     self.auto.start_all_node(self.node_yml_path)
    #     log.info("转账每个钱包")
    #     for to_account in self.account_list:
    #         self.transaction(self.w3_list[0],self.address,to_address=to_account,value=10000000000000000000000000)
    #     value_before = self.eth.getBalance(self.account_list[5])
    #     log.info(value_before)
    #     self.ppos_noconsensus_6.createStaking(0, self.account_list[5], self.nodeid_list2[5],
    #                                           self.externalId, self.nodeName, self.website, self.details,
    #                                           self.amount, self.programVersion)
    #     staking_after = self.eth.getBalance(self.account_list[5])
    #     assert value_before - staking_after > Web3.toWei(self.amount,"ether")
    #     value = self.amount + 1000
    #     self.ppos_noconsensus_6.addStaking(self.nodeid_list2[5], 0, value)
    #     addstaking_after = self.eth.getBalance(self.account_list[5])
    #     assert staking_after - addstaking_after > Web3.toWei(value,"ether")


    # def test_(self):
    #     """
    #     测试成为验证人异常退出，验证重启后是否被惩罚，验证人身份是否存在
    #     :return:
    #     """
    #     pass















































































































































