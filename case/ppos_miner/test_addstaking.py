# -*- coding: utf-8 -*-
"""
@Author: wuyiqin
@Date: 2019/8/16 11:45
@Description:主要是增持和修改节点信息用例
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
from utils.platon_lib.ppos_tool import get_block_number
from client_sdk_python.eth import Eth




class TestAddstaking():
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
    genesis_dict = LoadFile(genesis_path).get_data()
    chainid = int(genesis_dict["config"]["chainId"])

    config_json_path = conf.PLATON_CONFIG_PATH
    config_dict = LoadFile(config_json_path).get_data()
    amount_delegate = Web3.fromWei(
        int(config_dict['EconomicModel']['Staking']['MinimumThreshold']), 'ether')
    amount = Web3.fromWei(
        int(config_dict['EconomicModel']['Staking']['StakeThreshold']), 'ether')


    def setup_class(self):
        # self.auto = AutoDeployPlaton()
        # self.auto.start_all_node(self.node_yml_path)
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


    @allure.title("增加质押分别为{amount}")
    @pytest.mark.parametrize('amount', [100, 10000000, 1000000])
    def test_add_staking(self, amount):
        """
        用例id 72 账户余额足够，增加质押成功
        用例id 74 验证人在质押锁定期内增持的质押数量不限制
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        nodeId = self.nodeid_list2[0]
        log.info("钱包1做一笔质押")
        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], nodeId, self.externalId,
                                              self.nodeName, self.website, self.details, self.amount,
                                              self.programVersion)
        log.info("分别验证增持{}".format(amount))
        msg = self.ppos_noconsensus_1.addStaking(nodeId, typ=0, amount=amount)
        print(msg)
        assert msg.get("Status") == True, "返回状态错误"
        assert msg.get("ErrMsg") == 'ok', "返回消息错误"

        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        nodeid = msg["Data"]["NodeId"]
        assert nodeid == self.nodeid_list2[0]
        if amount == 100:
            assert Web3.fromWei(msg["Data"]["Shares"],'ether') == self.amount+100
        if amount == 10000000:
            assert Web3.fromWei(msg["Data"]["Shares"],'ether') == self.amount+100+10000000
        if amount == 1000000:
            assert Web3.fromWei(msg["Data"]["Shares"],'ether') == self.amount+100+10000000+1000000


    @allure.title("非验证人增持质押")
    def test_not_illegal_addstaking(self):
        """
        用例id 78 非验证人增持质押
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        nodeId = conf.illegal_nodeID
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg['Data']== "":
            log.info("节点1成为验证人")
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0],
                                                        self.nodeid_list2[0], self.externalId, self.nodeName, self.website,
                                                        self.details,
                                                        self.amount, self.programVersion)
        msg = self.ppos_noconsensus_1.addStaking(nodeId=nodeId, typ=0, amount=100)
        assert msg.get("Status") == False ,"返回状态错误"
        assert msg.get("ErrMsg") == 'This candidate is not exist',"非验证人增持质押异常"


    @allure.title("编辑验证人信息-未成为验证人的nodeID")
    def test_editCandidate_nodeid(self):
        """
        验证修改未成为验证人的nodeID
        """
        externalId = "88888888"
        nodeName = "wuyiqin"
        website = "www://baidu.com"
        details = "node_1"
        account = self.account_list[0]
        nodeid = conf.illegal_nodeID

        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        log.info("转账到钱包2")
        nodeId = self.nodeid_list2[1]
        msg = self.ppos_noconsensus_2.getCandidateInfo(nodeId)
        if msg['Data'] == "":
            log.info("节点2成为验证人")
            msg = self.ppos_noconsensus_2.createStaking(0, self.account_list[1],
                                                        nodeId, self.externalId, self.nodeName, self.website, self.details,
                                                        self.amount, self.programVersion)
            assert msg.get("Status") == True, "返回状态错误"
            assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("节点2修改节点信息")
        msg = self.ppos_noconsensus_2.updateStakingInfo(account, nodeid,
                                                        externalId, nodeName, website, details)
        log.info(msg)
        assert msg.get("Status") == False, "返回状态错误"


    @allure.title("编辑验证人信息-参数有效性验证")
    def test_editCandidate(self):
        """
        用例id 70 编辑验证人信息-参数有效性验证
        """
        externalId = "88888888"
        nodeName = "wuyiqin"
        website = "www://baidu.com"
        details = "node_1"
        account = self.account_list[0]

        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        log.info("转账到钱包2")
        nodeId = self.nodeid_list2[1]
        msg = self.ppos_noconsensus_2.getCandidateInfo(nodeId)
        if msg['Data'] == "":
            log.info("节点2成为验证人")
            msg = self.ppos_noconsensus_2.createStaking(0, self.account_list[1],
                                                        nodeId, self.externalId, self.nodeName, self.website, self.details,
                                                        self.amount, self.programVersion)
            assert msg.get("Status") == True, "返回状态错误"
            assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("节点2修改节点信息")
        msg = self.ppos_noconsensus_2.updateStakingInfo(account, self.nodeid_list2[1],
                                                        externalId, nodeName, website, details)
        assert msg.get("Status") == True, "返回状态错误"
        assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("查看节点2的信息")
        msg = self.ppos_noconsensus_2.getCandidateInfo(self.nodeid_list2[1])
        log.info(msg)
        assert msg["Data"]["ExternalId"] == externalId
        assert msg["Data"]["NodeName"] == nodeName
        assert msg["Data"]["Website"] == website
        assert msg["Data"]["Details"] == details
        assert msg["Data"]["benefitAddress"] == account



    @allure.title("修改钱包地址，更改后的地址收益正常")
    def test_alter_address(self):
        """
        修改钱包地址，更改后的地址收益正常
        """
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])
        externalId = "88888888"
        nodeName = "helloword"
        website = "www://dddddd.com"
        details = "node_2"
        ####没钱的钱包#####
        account = conf.no_money[0]
        balance_before = self.eth.getBalance(account)
        assert balance_before == 0
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[1])
        if msg['Data']== "":
            log.info("质押节点2成为验证节点")
            msg = self.ppos_noconsensus_2.createStaking(0, self.account_list[0],
                                                        self.nodeid_list2[1], self.externalId, self.nodeName, self.website,
                                                        self.details,
                                                        self.amount, self.programVersion)
            assert msg.get("Status") == True, "返回状态错误"
            assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("修改节点2的信息")
        msg = self.ppos_noconsensus_2.updateStakingInfo(account, self.nodeid_list2[1],
                                                        externalId, nodeName, website, details)
        assert msg.get("Status") == True, "返回状态错误"
        assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("进入第2个结算周期")
        get_block_number(self.w3_list[0])
        log.info("进入第3个结算周期")
        get_block_number(self.w3_list[0])
        balance_after = self.eth.getBalance(account)
        log.info(balance_after)
        assert balance_after > 0,"修改后的钱包余额没增加"
        assert balance_after> balance_before,"地址更改后未发现余额增加"


    @allure.title("增加质押为{x}")
    @pytest.mark.parametrize('x', [0, (amount_delegate-1)])
    def test_add_staking_zero(self,x):
        """测试增持金额为0,低于门槛"""

        log.info("转账到钱包3")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[2])
        log.info("质押节点3,成为验证人")
        nodeId = self.nodeid_list2[2]
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2],
                                                    nodeId, self.externalId, self.nodeName, self.website,
                                                    self.details,
                                                    self.amount, self.programVersion)
        log.info("节点3增持质押".format(x))
        msg = self.ppos_noconsensus_3.addStaking(nodeId, typ=0, amount=x)
        log.info(msg)
        assert msg.get("Status") == False, "返回状态错误"


    @allure.title("账户余额不足增加质押")
    def test_Insufficient_addStaking(self):
        """
        用例id 73 账户余额不足，增加质押失败
        """
        log.info("质押节点5成为验证人")
        nodeId = self.nodeid_list2[4]
        msg = self.ppos_noconsensus_5.createStaking(0, self.account_list[4], nodeId, self.externalId,
                                                    self.nodeName, self.website, self.details, self.amount,
                                                    self.programVersion)
        assert msg.get("Status") == True, "返回状态错误"
        amount = 100000000000000000000000000000000000
        msg = self.ppos_noconsensus_5.addStaking(nodeId=nodeId, typ=0, amount=amount)
        assert msg.get("Status") == False, "返回状态错误"
        msg_string = "The von of account is not enough"
        assert msg_string in msg.get("ErrMsg"), "余额不足发生质押异常"


    # @allure.title("验证人已申请退出中，申请增持质押")
    # def test_quit_and_addstaking(self):
    #     """
    #     用例id 77 验证人已申请退出中，申请增持质押
    #     """
    #     nodeId = self.nodeid_list2[0]
    #     msg = self.ppos_noconsensus_1.unStaking(nodeId)
    #     assert msg.get("Status") == True, "返回状态错误"
    #     assert msg.get("ErrMsg") == 'ok', "返回消错误"
    #     log.info("{}已经退出验证人.".format(nodeId))
    #     node_list = self.getCandidateList()
    #     log.info(self.nodeid_list2[0])
    #     log.info(node_list)
    #     assert self.nodeid_list2[0] not in node_list
    #     """验证人退出后，查询实时验证人列表返回的是空，可能是bug"""
    #     msg = self.ppos_noconsensus_1.addStaking(nodeId, typ=0, amount=100)
    #     assert msg.get("Status") == True, "返回状态错误"
    #     assert msg.get("ErrMsg") == 'This candidate is not exist'


    @allure.title("验证人已申请退出中，申请增持质押")
    def test_quit_and_addstaking(self):
        """
        用例id 77 验证人已申请退出中，申请增持质押
        """
        log.info("转账到钱包4")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[3])

        nodeId = self.nodeid_list2[3]
        log.info("节点4发起质押")
        msg = self.ppos_noconsensus_4.createStaking(0, self.account_list[3], nodeId, self.externalId,
                                                    self.nodeName, self.website, self.details, self.amount,
                                                    self.programVersion)
        assert msg.get("Status") == True, "质押失败"
        log.info("节点4退出质押")
        msg = self.ppos_noconsensus_4.unStaking(nodeId)
        # print(msg)
        assert msg.get("Status") == True, "返回状态错误"
        assert msg.get("ErrMsg") == 'ok', "返回消息错误"
        log.info("{}已经退出验证人.".format(nodeId))
        node_list = self.getCandidateList()
        # print(nodeId)
        # print(node_list)
        assert nodeId not in node_list
        msg = self.ppos_noconsensus_1.getCandidateInfo(nodeId)
        assert msg['Data'] == ""
        msg = self.ppos_noconsensus_4.addStaking(nodeId, typ=0, amount=100)
        assert msg.get("Status") == False, "返回状态错误"
        assert msg.get("ErrMsg") == 'This candidate is not exist'