# -*- coding: utf-8 -*-

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
from utils.platon_lib.ppos_tool import get_block_number,getVerifierList


"""
主要是锁定期的用例
"""
class TestLockup():
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
    chainid = 101



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
        self.w3_list = [connect_web3(url) for url in self.rpc_list]
        """用新的钱包地址和未质押过的节点id封装对象"""
        self.ppos_noconsensus_1 = Ppos(self.rpc_list[0], self.account_list[0],self.chainid,privatekey=self.privatekey_list[0])
        self.ppos_noconsensus_2 = Ppos(self.rpc_list[0], self.account_list[1],self.chainid,privatekey=self.privatekey_list[1])
        self.ppos_noconsensus_3 = Ppos(self.rpc_list[0], self.account_list[2],self.chainid,privatekey=self.privatekey_list[2])
        self.ppos_noconsensus_4 = Ppos(self.rpc_list[0], self.account_list[3],self.chainid,privatekey=self.privatekey_list[3])
        self.ppos_noconsensus_5 = Ppos(self.rpc_list[0], self.account_list[4],self.chainid,privatekey=self.privatekey_list[4])
        self.ppos_noconsensus_6 = Ppos(self.rpc_list[0], self.account_list[5],self.chainid,privatekey=self.privatekey_list[5])
        self.eth = Eth(self.w3_list[0])


    def transaction(self,w3, from_address, to_address=None,value=100000000000000000000000000000000,
                    gas=91000000, gasPrice=9000000000,pwd=conf.PASSWORD):
        """"
        转账公共方法,转账1000w eth
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



    @allure.title("验证人退回质押金（未到达可解锁期）")
    def test_back_unstaking(self):
        """
        验证人退回质押金（未到达可解锁期）
        质押成为下个周期验证人，退出后，下一个结算周期退出
        """
        log.info("转账每个钱包")
        for to_account in self.account_list:
            self.transaction(self.w3_list[0],self.address,to_address=to_account)
        log.info("节点1质押金额{} eth".format(self.amount))
        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        account_1 = self.eth.getBalance(self.account_list[0])
        log.info(account_1)
        get_block_number(self.w3_list[0])
        log.info("查询第2个结算周期的验证人")
        node_list = getVerifierList()
        log.info(node_list)
        assert self.nodeid_list2[0] in node_list

        log.info("节点1在第2结算周期，锁定期申请退回")
        self.ppos_noconsensus_1.unStaking(nodeId=self.nodeid_list2[0])
        """发起退回消耗一定gas"""
        account_2 = self.eth.getBalance(self.account_list[0])
        log.info(account_2)
        assert account_1 > account_2, "发起退回的交易钱包异常"

        log.info("进入第3个结算周期")
        get_block_number(w3=self.w3_list[0])
        account_3 = self.eth.getBalance(self.account_list[0])
        log.info(account_3)
        assert  account_3> account_2
        assert  account_3 -account_2 < Web3.toWei(self.amount, "ether")
        log.info(account_3 -account_2)

        node_list = getVerifierList()
        log.info(node_list)
        assert self.nodeid_list2[0] not in node_list

        log.info("进入第4个结算周期")
        get_block_number(w3=self.w3_list[0])
        account_4 = self.eth.getBalance(self.account_list[0])
        log.info(account_4)
        """ 第3个结算周期结束后质押金额已退 """
        log.info(account_4 - account_3)
        assert account_4 -account_3 > Web3.toWei(self.amount, "ether")
        assert account_4 -account_2 > Web3.toWei(self.amount, "ether")


    @allure.title("锁定期增加质押与委托")
    def test_lockup_addstaking(self):
        """
        用例id74 锁定期增加质押
        用例id 112 锁定期委托人进行委托
        """
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        if msg["Data"] == "":
            log.info("节点1质押金额{} eth".format(self.amount))
            self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
        log.info("进入锁定期")
        get_block_number(self.w3_list[0])
        value = 100
        msg = self.ppos_noconsensus_1.addStaking(self.nodeid_list2[0],0,value)
        assert msg.get("Status") == True
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        log.info(msg)
        nodeid = msg["Data"]["NodeId"]
        log.info("增持后验证质押金额")
        assert  msg["Data"]["Shares"] == 1000100000000000000000000
        assert  msg["Data"]["Released"] == 1000000000000000000000000
        assert msg["Data"]["ReleasedHes"] == 100000000000000000000
        assert nodeid == self.nodeid_list2[0]
        self.ppos_noconsensus_2.delegate(0,self.nodeid_list2[0],10)
        msg = self.ppos_noconsensus_2.getCandidateInfo(self.nodeid_list2[0])
        log.info(msg)
        assert msg["Data"]["Shares"] == 1000110000000000000000000
        # assert msg["Data"]["Released"] == 1000000000000000000000000
        # assert msg["Data"]["ReleasedHes"] == 10000000000000000000


    @allure.title("验证根据质押金额排名")
    def test_taking_cycle_ranking(self):
        """
        验证根据质押金额排名
        """
        log.info("质押节点2")
        self.ppos_noconsensus_2.createStaking(0, self.account_list[1], self.nodeid_list2[1],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("质押节点3")
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount+100, self.programVersion)
        log.info("进入到下个结算周期")
        get_block_number(w3=self.w3_list[0])
        node_list = getVerifierList()
        log.info(node_list)
        log.info(self.nodeid_list2[2])
        log.info(self.nodeid_list2[1])

        msg = self.ppos_noconsensus_2.getCandidateInfo(self.nodeid_list2[1])
        log.info(msg)
        msg = self.ppos_noconsensus_2.getCandidateInfo(self.nodeid_list2[2])
        log.info(msg)

        assert self.nodeid_list2[2] in node_list
        assert self.nodeid_list2[1] in node_list
        assert node_list[0] == self.nodeid_list2[2]


    @allure.title("验证根据增持+委托金额排名")
    def test_delegate_cycle_ranking(self):
        log.info("钱包4委托节点2 50eth")
        msg = self.ppos_noconsensus_4.delegate(0,nodeId=self.nodeid_list2[1],amount=50)
        print(msg)
        log.info("节点2增加质押61 eth")
        msg = self.ppos_noconsensus_2.addStaking(self.nodeid_list2[1],0,amount=61)
        print(msg)
        log.info("进入下一个结算周期")
        get_block_number(self.w3_list[0])

        node_list = getVerifierList()
        log.info(node_list)
        log.info(self.nodeid_list2[1])
        log.info(self.nodeid_list2[2])

        """预期节点2排在节点3之前"""
        msg = self.ppos_noconsensus_2.getCandidateInfo(self.nodeid_list2[1])
        log.info(msg)

        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        log.info(msg)

        assert node_list[0] == self.nodeid_list2[1]
        assert node_list[1] == self.nodeid_list2[2]


    # @allure.title("版本号低排名约低")
    # def test_version_cycle_ranking(self):
    #     pass


    @allure.title("质押相等的金额，按照时间先早排序")
    def test_same_amount_cycle(self):
        """
        质押相等的金额，按照时间先早排序
        """
        log.info("质押节点4金额200eth")
        self.ppos_noconsensus_4.createStaking(0, self.account_list[3], self.nodeid_list2[3],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount+200, self.programVersion)
        log.info("质押节点5金额20eth")
        self.ppos_noconsensus_5.createStaking(0, self.account_list[4], self.nodeid_list2[4],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount+200, self.programVersion)
        log.info("进入到下个结算周期")
        get_block_number(self.w3_list[0])

        node_list = getVerifierList()
        log.info(node_list)
        log.info(self.nodeid_list2[3])
        log.info(self.nodeid_list2[4])
        assert node_list[0] == self.nodeid_list2[3]
        assert node_list[1] == self.nodeid_list2[4]


    # @allure.title("验证人申请退回所有质押金（包含初始质押金和当前结算期内质押金）")
    # def test_(self):
    #     self.ppos_noconsensus_6.createStaking(0, self.account_list[5], self.nodeid_list2[5],
    #                                           self.externalId, self.nodeName, self.website, self.details,
    #                                           self.amount, self.programVersion)
    #     log.info("进入下一个结算周期")
    #     get_block_number(self.w3_list[0])
    #     log.info("节点6增持金额")
    #     self.ppos_noconsensus_6.addStaking(self.nodeid_list2[5],0,self.amount+100)
    #     get_block_number(self.w3_list[0])
    #     log.info("进入下一个结算周期")
    #     self.ppos_noconsensus_6.unStaking(nodeId=self.nodeid_list2[5])
    #     log.info("进入锁定期")
    #     get_block_number(self.w3_list[0])
    #     """查不到"""
    #     get_block_number(self.w3_list[0])
    #     """查到全部"""






































