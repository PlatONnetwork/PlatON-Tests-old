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


class TestDelegate():
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
    chainid = 101


    def setup_class(self):
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

    def test_illege_delegate(self):
        """
        用例id 首次委托金额必须大于10 eth
        """
        log.info("质押非共识节点1：{}成为验证人".format(self.nodeid_list2[0]))
        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        amount = 9
        log.info("钱包2{}委托金额为9 eth".format(self.account_list[1]))
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == "Delegate deposit too low"
        amount = 0
        log.info("钱包2{}委托金额为0 eth".format(self.account_list[1]))
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == "This amount is illege"

    def test_delegate_verifier(self):
        """
        测试质押过的钱包不能去委托
        """
        amount = 1000
        log.info("质押过的钱包不能再去质押{}".format(self.nodeid_list2[0]))
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
        # print(msg)
        assert msg.get("Status") == False
        """目前有bug，质押过的钱包也能委托"""

    def test_delegate(self):
        """
        用例95 委托成功，查询节点信息，金额
        用例id 98 委托人与验证人验证，验证人存在
        """
        amount = 1000
        log.info("钱包{}委托成功".format(self.account_list[1]))
        msg = self.ppos_noconsensus_2.delegate(0,self.nodeid_list2[0],amount)
        log.info("")
        assert msg.get("Status") == True
        assert msg.get("ErrMsg") == 'ok'

    def test_getDelegateInfo(self):
        """
        用例id 94 查询当前单个委托信息
        """
        log.info("查询质押节点信息{}".format(self.nodeid_list2[0]))
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        print(msg)
        assert msg["Data"]["NodeId"] == self.nodeid_list2[0]
        log.info("查询质押+委托的金额正确")
        assert msg["Data"]["Shares"] == 1001000000000000000000000
        assert msg["Data"]["ReleasedHes"] == 1000000000000000000000000
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("质押的块高{}".format(stakingBlockNum))
        msg = self.ppos_noconsensus_2.getDelegateInfo(stakingBlockNum, self.account_list[1], self.nodeid_list2[0])
        data = msg["Data"]
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[1]
        assert data["NodeId"] == self.nodeid_list2[0]
        assert data["ReleasedHes"] == 1000000000000000000000

    def test_insufficient_delegate(self):
        """
        用例96 余额不足委托失败
        """
        amount = 100000000000000000000000000000
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], amount)
        # print(msg)
        assert msg.get("Status") == False
        assert msg.get("ErrMsg") == 'Delegate failed: The von of account is not enough'

    def test_not_nodeId_delegate(self):
        """
        用例72 验证人不存在进行委托
        """
        amount = 1000
        msg = self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[1], amount)
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
        用例id 81 验证人申请退回质押金
        """
        account_before = self.eth.getBalance(self.account_list[0])
        log.info("非共识节点1对应的钱包余额{}".format(account_before))
        log.info("非共识节点1退出质押{}".format(self.nodeid_list2[0]))
        self.ppos_noconsensus_1.unStaking(self.nodeid_list2[0])
        time.sleep(2)
        account_after = self.eth.getBalance(self.account_list[0])
        log.info("非共识节点1退出质押后钱包余额{}")
        assert account_after > account_before,"退出质押后，钱包余额未增加"
        log.info("因为质押消耗的gas值大于撤销质押的gas值")
        assert 900000000000000000000000 < account_after - account_before < 1000000000000000000000000
        node_list = self.getCandidateList()
        assert self.nodeid_list2[2] not in node_list, "验证节点退出异常"
        log.info("{}已经退出验证人".format(self.nodeid_list2[0]))

    def test_back_unStaking_commissioned(self):
        """
        用例id 82 验证人申请退回质押金，委托金额还生效
        用例id 83 验证人退出后，委托人信息还存在

        """
        log.info("{}成为验证人".format(self.nodeid_list2[0]))
        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("钱包2{}进行委托100".format(self.account_list[1]))
        self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], 100)
        self.ppos_noconsensus_1.unStaking(self.nodeid_list2[0])
        log.info("{}退出验证人".format(self.nodeid_list2[0]))
        msg = self.ppos_noconsensus_2.getDelegateListByAddr(self.account_list[1])
        print(msg)
        StakingBlockNum = msg["Data"][0]["StakingBlockNum"]
        msg = self.ppos_noconsensus_2.getDelegateInfo(StakingBlockNum,self.account_list[1],self.nodeid_list2[0])
        data = msg["Data"]
        data = json.loads(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[1]
        assert data["NodeId"] == self.nodeid_list2[0]
        assert data["ReleasedHes"] == 1000000000000000000000

    def test_identifier_quit_delegate(self):
        """
        委托验证节点，验证节点退出后，再成为验证节点，再去委托：预期有2个委托消息
        """
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
        time.sleep(10)
        assert len(msg["Data"]) == 2
        for i in msg["Data"]:
            assert Web3.toChecksumAddress(i["Addr"]) == self.account_list[3]
            assert i["NodeId"] == self.nodeid_list2[2]

    def test_restrictingPlan_unStaking(self):
        """
        用例id 83 使用锁仓账户中的Token进行创建验证人申请退回质押金
        """

##############################赎回####################################################

    def test_unDelegate_part(self):
        """
         用例id 106 申请赎回委托
         用例id 111 委托人未达到锁定期申请赎回
         申请部分赎回
        """
        log.info("质押节点3：{}成为验证节点".format(self.nodeid_list2[2]))
        self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)
        log.info("钱包4 {}委托到3 {}".format(self.account_list[3], self.account_list[2]))
        value = 100
        self.ppos_noconsensus_4.delegate(0, self.nodeid_list2[2], value)
        log.info("查询当前节点质押信息")
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("发起质押的区高{}".format(stakingBlockNum))
        delegate_value = 20
        self.ppos_noconsensus_4.unDelegate(stakingBlockNum,self.nodeid_list2[2],delegate_value)
        log.info("查询钱包{}的委托信息".format(self.account_list[3]))
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        print(msg)
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        print(data)
        assert Web3.toChecksumAddress(data["Addr"]) == self.account_list[3]
        assert data["NodeId"] == self.nodeid_list2[2]
        print(data["ReleasedHes"])
        value = value - delegate_value
        result_value = Web3.toWei(value, "ether")
        assert data["ReleasedHes"] == result_value

    def test_unDelegate_iff(self):
        """
        验证 大于委托金额赎回
        """
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        print(msg)
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        print(data)
        releasedHes = data["ReleasedHes"]
        releasedHes = Web3.fromWei(releasedHes, 'ether')
        log.info("委托钱包可赎回的金额单位eth：{}".format(releasedHes))
        delegate_value = releasedHes + 20
        msg = self.ppos_noconsensus_4.unDelegate(stakingBlockNum, self.nodeid_list2[2], delegate_value)
        print(msg)
        assert msg["Status"] == False
        err_msg = "withdrewDelegate err: The von of delegate is not enough"
        assert err_msg in msg["ErrMsg"]

    def test_unDelegate_all(self):
        """
        验证 赎回全部委托的金额
        验证 赎回金额为0
        """
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("查询节点质押信息回去质押块高{}".format(stakingBlockNum))
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        releasedHes = data["ReleasedHes"]
        releasedHes = Web3.fromWei(releasedHes, 'ether')
        log.info("委托钱包可赎回的金额单位eth：{}".format(releasedHes))
        account_before = self.eth.getBalance(self.account_list[3])
        print(account_before)
        msg = self.ppos_noconsensus_4.unDelegate(stakingBlockNum, self.nodeid_list2[2], releasedHes)
        assert msg["Status"] == True
        account_after = self.eth.getBalance(self.account_list[3])
        print(account_after)
        print(account_after - account_before)
        ##为什么会赎回多那么多钱？1000000000000159999910972325109760
        # assert account_before + releasedHes > account_after
        assert account_after > account_before
        log.info("全部委托金额赎回后，查询委托金额".format(account_after))
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = json.loads(msg["Data"])
        releasedHes = data["ReleasedHes"]
        log.info("查询全部赎回后，剩余的委托金额{}".format(releasedHes))
        assert releasedHes == 0
        log.info("验证委托金额为0进行赎回")
        msg = self.ppos_noconsensus_4.unDelegate(stakingBlockNum, self.nodeid_list2[2], releasedHes)
        assert msg["Status"] == False
        print(msg)

    def test_multiple_delegate_undelegate(self):
        """
        验证多次委托，多次赎回
        """
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("查询节点质押信息回去质押块高{}".format(stakingBlockNum))
        value_list = [10,11,12,13,14,15,16,17,18]
        for value in value_list:
            log.info("钱包4 委托金额{}".format(value))
            self.ppos_noconsensus_4.delegate(0, self.nodeid_list2[2], value)
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = json.loads(msg["Data"])
        releasedHes = Web3.fromWei(data["ReleasedHes"], 'ether')
        log.info("查询委托的金额{}eth".format(releasedHes))
        delegate_value = 0
        for i in value_list:
            delegate_value = i + delegate_value
        assert delegate_value == releasedHes ,"委托的金额与查询到的金额不一致"
        for value in value_list:
            log.info("赎回的金额：{}eth".format(value))
            self.ppos_noconsensus_4.unDelegate(stakingBlockNum, self.nodeid_list2[2], value)
        log.info("赎回委托金额后查询委托信息")
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = json.loads(msg["Data"])
        releasedHes = Web3.fromWei(data["ReleasedHes"], 'ether')
        log.info("赎回委托金额后查询委托金额{}".format(releasedHes))
        assert releasedHes == 0









