# -*- coding: utf-8 -*-

import json
import math
import time
import allure
import pytest
from client_sdk_python import Web3
from common.connect import connect_web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info
from common import log
from deploy.deploy import AutoDeployPlaton
from client_sdk_python.personal import (
    Personal,
)
from client_sdk_python.eth import Eth

"""每轮230个块确认验证人"""
def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number + 20
    else:
        return total_time - number + i + 20


class TestPledge():
    node_yml_path = conf.PPOS_NODE_YML
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
    amount = 1000000
    programVersion = 1792
    illegal_nodeID = conf.illegal_nodeID



    def setup_class(self):
        self.ppos_link = Ppos(
            self.rpc_list[0], self.address)
        self.w3_list = [connect_web3(url) for url in self.rpc_list]
        """用新的钱包地址和未质押过的节点id封装对象"""
        self.ppos_noconsensus_1 = Ppos(self.rpc_list[0], self.account_list[0], privatekey= self.privatekey_list[0])
        self.ppos_noconsensus_2 = Ppos(self.rpc_list[0], self.account_list[1], privatekey=self.privatekey_list[1])
        self.ppos_noconsensus_3 = Ppos(self.rpc_list[0], self.account_list[2], privatekey=self.privatekey_list[2])
        self.ppos_noconsensus_4 = Ppos(self.rpc_list[0], self.account_list[3], privatekey=self.privatekey_list[3])
        for to_account in self.account_list:
            self.transaction(self.w3_list[0],self.address,to_account)
        self.eth = Eth(self.w3_list[0])

    def transaction(self,w3, from_address, to_address=None, value=1000000000000000000000000000000000,
                    gas=91000000, gasPrice=9000000000):
        personal = Personal(self.w3_list[0])
        personal.unlockAccount(self.address, self.pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': gas,
            'gasPrice': gasPrice,
            'value': value
        }
        tx_hash = w3.eth.sendTransaction(params)
        return tx_hash

    def getCandidateList(self):
        msg = self.ppos_noconsensus_1.getCandidateList()
        # print(msg)
        recive_list = msg.get("Data")
        nodeid_list = []
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
        return nodeid_list

##############################初始验证人############################################

    def test_initial_identifier(self):
        """
        用例id 54,55
        测试验证人参数有效性验证
        """
        recive = self.ppos_link.getVerifierList()
        recive_list = recive.get("Data")
        nodeid_list=[]
        # 查看查询当前结算周期的验证人队列
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
            StakingAddress = node_info.get("StakingAddress")
            StakingAddress = ( Web3.toChecksumAddress(StakingAddress))
            assert StakingAddress == self.address,"内置钱包地址错误{}".format(StakingAddress)
        # print(recive)
        # print(nodeid_list)
        assert nodeid_list == nodeid_list, "正常的nodeID列表{},异常的nodeID列表{}".format(nodeid_list,recive_list)

    def test_initial_cannot_entrust(self):
        """
        用例id 56 初始验证人不能接受委托
        """
        msg = self.ppos_link.delegate(typ = 1,nodeId=self.nodeid_list[0],amount=50)
        assert msg.get("Status") == False ,"返回状态错误"
        assert msg.get("ErrMsg") == 'This candidate is not allow to delegate',"返回提示语错误"

    def test_initial_add_pledge(self):
        """
        用例id 57 初始验证人增持质押
        """
        msg = self.ppos_link.addStaking(nodeId=self.nodeid_list[0],typ=0,amount=1000)
        print(msg)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'

    def test_initial_quit(self):
        """
        用例id 58 初始验证人退出
        """
        msg = self.ppos_link.unStaking(self.nodeid_list[0])
        print(msg)
        print(self.nodeid_list[0])
        assert msg.get("Status") ==True
        assert msg.get("ErrMsg") == 'ok'
        """暂时没配置参数所以还要调整"""
        time.sleep(2)
        node_list = self.getCandidateList()
        assert self.nodeid_list[0] not in node_list


###########################质押于增持################################################

    def test_iff_staking(self):
        """
        用例 64 非初始验证人做质押,质押金额小于最低门槛
        """
        benifitAddress = self.account_list[1]
        nodeId = self.nodeid_list2[0]
        """非共识节点做一笔质押"""
        amount = 100000
        msg = self.ppos_noconsensus_1.createStaking(0, benifitAddress,
                                           nodeId,self.externalId,self.nodeName, self.website, self.details,amount,self.programVersion)
        print(msg)
        assert msg.get("Status") ==False
        assert msg.get("ErrMsg") == "Staking deposit too low"

    def test_staking(self):
        """
        用例 62 非初始验证人做质押1000000
        """
        nodeId = self.nodeid_list2[0]
        """非共识节点做一笔质押"""
        msg = self.ppos_noconsensus_1.createStaking(0, self.account_list[1],
                                           nodeId,self.externalId,self.nodeName, self.website,self.details,
                                                    self.amount,self.programVersion)
        print(msg)
        assert msg.get("Status") ==True
        assert msg.get("ErrMsg") == 'ok'
        """暂时没配置参数所以还要调整"""
        ##查看实时验证人信息
        time.sleep(5)
        recive = self.ppos_noconsensus_1.getCandidateList()
        recive_list = recive.get("Data")
        nodeid_list = []
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
        assert self.nodeid_list2[0] in nodeid_list,"非初始验证人质押失败"

    def test_not_illegal_addstaking(self):
        """
        用例id 78 非验证人增持质押
        """
        nodeId = conf.illegal_nodeID
        msg = self.ppos_noconsensus_1.addStaking(nodeId=nodeId, typ=0, amount=100)
        # print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'This candidate is not exist'

    def test_illegal_pledge(self):
        """
        用例id 63 非链上的nodeID去质押
        """
        benifitAddress = self.account_list[1]
        log.info("不存在链上的nodeID去质押")
        msg = self.ppos_noconsensus_2.createStaking(0, benifitAddress,self.illegal_nodeID,self.externalId,
                                           self.nodeName, self.website, self.details,self.amount,self.programVersion)
        print(msg)
        assert msg.get("Status") ==True
        assert msg.get("ErrMsg") == 'ok'

    @pytest.mark.parametrize('amount', [(100),(10000000),(1000000)])
    def test_add_staking(self,amount):
        """
        用例id 72 账户余额足够，增加质押成功
        用例id 74 验证人在质押锁定期内增持的质押数量不限制
        """
        nodeId = self.nodeid_list2[0]
        log.info("分别验证增持100，10000000，1000000")
        msg = self.ppos_noconsensus_1.addStaking(nodeId,typ=0,amount=amount)
        print(msg)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'

    def test_getCandidateInfo(self):
        """
        用例69 查询验证人信息,调用质押节点信息
        """
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        nodeid = msg["Data"]["NodeId"]
        print(msg["Data"]["Shares"])
        log.info("增持后验证质押金额")
        assert  msg["Data"]["Shares"] == 12000100000000000000000000
        assert nodeid == self.nodeid_list2[0]
        msg = self.ppos_link.getCandidateInfo(self.nodeid_list[0])
        nodeid = msg["Data"]["NodeId"]
        assert nodeid == self.nodeid_list[0]

    # @pytest.mark.parametrize("externalId,nodeName,website,details",[("88888888","jay_wu","https://baidu.com,node_1"),
    #                                                                       ("","","","")])
    # def test_editCandidate(self,externalId,nodeName,website,details):
    #     """
    #     用例id 70 编辑验证人信息-参数有效性验证
    #     """
    #     msg = self.ppos_noconsensus_1.updateStakingInfo(self.account_list[0], self.nodeid_list2[0],
    #                                                     externalId, nodeName, website, details)
    #     print(msg)
    #     msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
    #     print(msg)

    def test_editCandidate(self):
        """
        用例id 70 编辑验证人信息-参数有效性验证
        """
        externalId = "88888888"
        nodeName = "jay_wu"
        website = "www://baidu.com"
        details = "node_1"
        msg = self.ppos_noconsensus_1.updateStakingInfo(self.account_list[0], self.nodeid_list2[0],
                                                        externalId, nodeName, website, details)
        assert msg.get("Status") ==True
        assert msg.get("ErrMsg") == 'ok'
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        print(msg)
        assert msg["Data"]["ExternalId"] == externalId
        assert msg["Data"]["nodeName"] == nodeName
        assert msg["Data"]["website"] == website
        assert msg["Data"]["details"] == details

    def test_add_staking_zero(self):
        """测试增持金额为0"""
        nodeId = self.nodeid_list2[0]
        msg = self.ppos_noconsensus_1.addStaking(nodeId,typ=0,amount=0)
        assert msg.get("Status") == False

    def test_Insufficient_delegate(self):
        """
        用例id 73 账户余额不足，增加质押失败
        """
        amount = 100000000000000000000000000000000000
        nodeId = self.nodeid_list2[0]
        msg = self.ppos_noconsensus_1.addStaking(nodeId=nodeId,typ=0,amount=amount)
        # print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'The von of account is not enough'

    def test_quit_and_addstaking(self):
        """
        用例id 77 验证人已申请退出中，申请增持质押
        """
        nodeId = self.nodeid_list2[0]
        msg  = self.ppos_noconsensus_1.unStaking(nodeId)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'
        log.info("{}已经退出验证人.".format(nodeId))
        time.sleep(2)
        node_list = self.getCandidateList()
        assert self.nodeid_list2[0] not in node_list
        msg = self.ppos_noconsensus_1.addStaking(nodeId,typ=0,amount=100)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'This candidate is not exist'

#######################################委托############################################################

    def test_illege_delegate(self):
        """
        用例id 首次委托金额必须大于10 eth
        """
        amount = 9
        msg = self.ppos_noconsensus_3.delegate(0,self.illegal_nodeID,amount)
        print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == "Delegate deposit too low"
        amount = 0
        msg = self.ppos_noconsensus_3.delegate(0, self.illegal_nodeID, amount)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == "This amount is illege"

    def test_delegate_verifier(self):
        """
        测试质押过的钱包不能去委托
        """
        amount = 1000
        msg = self.ppos_noconsensus_2.delegate(0,self.illegal_nodeID,amount)
        print(msg)
        assert msg.get("Status") == False

    def test_delegate(self):
        """
        用例95 委托成功，查询节点信息，金额
        用例id 98 委托人与验证人验证，验证人存在
        """
        amount = 1000
        msg = self.ppos_noconsensus_3.delegate(0,self.illegal_nodeID,amount)
        print(msg)
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'

    def test_getDelegateInfo(self):
        """
        用例id 94 查询委托参数验证
        """
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.illegal_nodeID)
        print(msg)
        assert msg["Data"]["NodeId"] == self.illegal_nodeID
        """查询当前候选人总共质押加被委托的von数目"""
        assert msg["Data"]["Shares"] == 1001000000000000000000000
        assert msg["Data"]["ReleasedHes"] == 1000000000000000000000000
        """通过查询"""
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        # print(stakingBlockNum)
        msg = self.ppos_noconsensus_3.getDelegateInfo(stakingBlockNum,self.account_list[2],self.illegal_nodeID)
        # print(msg)
        data = msg["Data"]
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[2]
        assert data["NodeId"] == self.illegal_nodeID
        assert data["ReleasedHes"] == 1000000000000000000000

    def test_insufficient_delegate(self):
        """
        用例96 余额不足委托失败
        """
        amount = 100000000000000000000000000
        msg = self.ppos_noconsensus_3.delegate(0,self.illegal_nodeID,amount)
        # print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'Delegate failed: The von of account is not enough'

    def test_not_nodeId_delegate(self):
        """
        用例72 验证人不存在进行委托
        """
        amount = 1000
        msg = self.ppos_noconsensus_3.delegate(0,self.nodeid_list2[2],amount)
        print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'This candidate is not exist'

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

    def test_back_unStaking(self):
        """
        用例id 81 验证人申请退回质押金（未有委托用户委托的情况）
        """
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2],self.nodeid_list2[2],
                                                    self.externalId, self.nodeName, self.website, self.details,
                      self.amount,self.programVersion)
        account_before = self.eth.getBalance(self.account_list[2])
        print(self.nodeid_list2[2])
        print(account_before)
        self.ppos_noconsensus_3.unStaking(self.nodeid_list2[2])
        time.sleep(2)
        account_after = self.eth.getBalance(self.account_list[2])
        assert account_after > account_before
        log.info("因为质押消耗的gas值大于撤销质押的gas值")
        assert 900000000000000000000000 <account_after -account_before< 1000000000000000000000000
        node_list = self.getCandidateList()
        print(node_list)
        assert self.nodeid_list2[2] not in node_list,"验证节点退出异常"
        log.info("{}已经退出验证人".format(self.nodeid_list2[2]))

    def test_back_unStaking_commissioned(self):
        """
        用例id 82 验证人申请退回质押金（有委托用户委托的情况)
        """
        log.info("{}成为验证人".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2],self.nodeid_list2[2],
                                                    self.externalId, self.nodeName, self.website, self.details,
                      self.amount,self.programVersion)
        log.info("{}进行委托".format(self.account_list[3]))
        self.ppos_noconsensus_4.delegate(0,self.nodeid_list2[2],100)
        account_before = self.eth.getBalance(self.account_list[2])
        print(account_before)
        self.ppos_noconsensus_3.unStaking(self.nodeid_list2[2])
        log.info("{}退出验证人".format(self.nodeid_list2[2]))
        time.sleep(2)
        account_after = self.eth.getBalance(self.account_list[2])
        print(account_after)
        print(account_after-account_before)
        assert account_after > account_before
        assert 900000000000000000000000 < account_after - account_before < 1000000000000000000000000
        node_list = self.getCandidateList()
        print(node_list)
        assert self.nodeid_list2[2] not in node_list, "验证节点退出异常"

    def test_back_delegate_account(self):
        """
        验证验证节点退出后，验证金额不会退。需要手工退
        """
        log.info("{}成为验证人".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2],self.nodeid_list2[2],
                                                    self.externalId, self.nodeName, self.website, self.details,
                      self.amount,self.programVersion)
        log.info("{}进行委托".format(self.account_list[3]))
        self.ppos_noconsensus_4.delegate(0,self.nodeid_list2[2],100)
        account_before = self.eth.getBalance(self.account_list[3])
        print(account_before)
        self.ppos_noconsensus_3.unStaking(self.nodeid_list2[2])
        account_after = self.eth.getBalance(self.account_list[3])
        print(account_after)
        # assert account_after > account_before
        log.info("{}退出验证人".format(self.nodeid_list2[2]))
        """暂时不清楚退出质押后，委托人的钱怎么退"""

    def test_restrictingPlan_unStaking(self):
        """
        用例id 83 使用锁仓账户中的Token进行创建验证人申请退回质押金
        """

    def test_quitReleased_(self):
        """
         测试验证节点退出后，还能查询到钱包的委托信息
         测试节点退出后，查看委托的钱包委托金额不变
        """
        log.info("质押节点{}".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("钱包{}委托到{}".format(self.account_list[3],self.account_list[2]))
        msg = self.ppos_noconsensus_4.delegate(0, self.nodeid_list2[2], 100)
        assert msg["Status"] == True
        assert msg["ErrMsg"] == "ok"
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("{}退出验证人".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.unStaking(self.nodeid_list2[2])
        log.info("查询委托信息{}".format(self.account_list[3]))
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = msg["Data"]
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[3]
        assert data["NodeId"] == self.nodeid_list2[2]
        assert data["ReleasedHes"] == 100000000000000000000

##############################赎回####################################################

    def test_unDelegate_part(self):
        """
         用例id 106 申请赎回委托
         用例id 111 委托人未达到锁定期申请赎回
         申请部分赎回
        """
        log.info("质押节点{}".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("委托验证人节点{}100".format(self.nodeid_list2[3]))
        log.info("钱包{}委托到{}".format(self.account_list[3],self.account_list[2]))
        self.ppos_noconsensus_4.delegate(0, self.nodeid_list2[2], 100)
        log.info("查询当前节点质押信息")
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        print(msg)
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        """传人参数为委托人钱包，验证人的节点id"""
        log.info("查询钱包{}的委托信息".format(self.account_list[3]))
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum,self.account_list[3],self.nodeid_list2[2])
        print(msg)
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[3]
        assert data["NodeId"] == self.nodeid_list2[2]
        print(data["ReleasedHes"])
        assert data["ReleasedHes"] == 80000000000000000000

    def test_unDelegate_iff_and_all(self):
        """
        用例id 104 余额不足赎回
        用例id xxx 大于委托金额赎回
        """
        msg = self.ppos_noconsensus_3.getDelegateListByAddr(self.account_list[2])
        print(self.nodeid_list2[2])
        iff_account = conf.no_money[0]


















































































































































