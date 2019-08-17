# -*- coding: utf-8 -*-
"""
@Author: wuyiqin
@Date: 2019/8/16 11:45
@Description:主要是ppos赎回的用例
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
    genesis_dict = LoadFile(genesis_path).get_data()
    chainid = int(genesis_dict["config"]["chainId"])

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



##############################赎回####################################################

    @allure.title("委托人未达到锁定期申请赎回")
    def test_unDelegate_part(self):
        """
         用例id 106 申请赎回委托
         用例id 111 委托人未达到锁定期申请赎回
         申请部分赎回
        """
        log.info("转账到钱包3")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[2])
        log.info("转账到钱包4")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[3])
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[2])
        if msg['Data']== "":
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


    @allure.title("大于委托金额赎回")
    def test_unDelegate_iff(self):
        """
        验证 大于委托金额赎回
        """
        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[2])
        if msg['Data']== "":
            log.info("质押节点3成为验证节点")
            self.ppos_noconsensus_3.createStaking(0, self.account_list[2], self.nodeid_list2[2],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
        log.info("钱包4 委托到3 {}")
        value = 100
        self.ppos_noconsensus_4.delegate(0, self.nodeid_list2[2], value)
        msg = self.ppos_noconsensus_3.getCandidateInfo(self.nodeid_list2[2])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        msg = self.ppos_noconsensus_4.getDelegateInfo(stakingBlockNum, self.account_list[3], self.nodeid_list2[2])
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        releasedHes = data["ReleasedHes"]
        releasedHes = Web3.fromWei(releasedHes, 'ether')
        log.info("委托钱包可赎回的金额单位eth：{}".format(releasedHes))
        delegate_value = releasedHes + 20
        msg = self.ppos_noconsensus_4.unDelegate(stakingBlockNum, self.nodeid_list2[2], delegate_value)
        assert msg["Status"] == False
        err_msg = "withdrewDelegate err: The von of delegate is not enough"
        assert err_msg in msg["ErrMsg"]


    @allure.title("赎回全部委托的金额与赎回金额为0")
    def test_unDelegate_all(self):
        """
        验证 赎回全部委托的金额
        验证 赎回金额为0
        """
        log.info("转账到钱包1")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[0])
        log.info("转账到钱包2")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[1])

        log.info("节点1质押成为验证人")
        self.ppos_noconsensus_1.createStaking(0, self.account_list[0], self.nodeid_list2[0],
                                              self.externalId, self.nodeName, self.website, self.details,
                                              self.amount, self.programVersion)

        msg = self.ppos_noconsensus_1.getCandidateInfo(self.nodeid_list2[0])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("查询节点质押信息,质押块高{}".format(stakingBlockNum))
        log.info("钱包2进行委托")
        value=80
        self.ppos_noconsensus_2.delegate(0, self.nodeid_list2[0], value)
        msg = self.ppos_noconsensus_2.getDelegateInfo(stakingBlockNum, self.account_list[1], self.nodeid_list2[0])
        data = msg["Data"]
        """不清楚msg["Data"]对应value是str类型，需要再转字典"""
        data = json.loads(data)
        log.info(data)
        releasedHes = data["ReleasedHes"]
        releasedHes = Web3.fromWei(releasedHes, 'ether')
        log.info("委托钱包可赎回的金额单位eth：{}".format(releasedHes))
        account_before = self.eth.getBalance(self.account_list[1])
        msg = self.ppos_noconsensus_2.unDelegate(stakingBlockNum, self.nodeid_list2[0], releasedHes)
        assert msg["Status"] == True
        account_after = self.eth.getBalance(self.account_list[1])
        result_value = account_after - account_before
        ##为什么会赎回多那么多钱？1000000000000159999910972325109760
        assert account_before + data["ReleasedHes"] > account_after
        assert  70 < Web3.fromWei(result_value,"ether") < releasedHes ,"赎回的金额减去gas应在这范围"
        log.info("全部委托金额赎回后，查询委托金额".format(account_after))
        msg = self.ppos_noconsensus_2.getDelegateInfo(stakingBlockNum, self.account_list[1], self.nodeid_list2[0])
        log.info(msg)
        """如果全部金额赎回，再查getDelegateInfo返回数据为空"""
        assert msg["Status"] == False
        assert msg["ErrMsg"] =="Delegate info is not found"



    def test_multiple_delegate_undelegate(self):
        """
        验证多次委托，多次赎回
        """
        log.info("转账到钱包5")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[4])
        log.info("转账到钱包6")
        self.transaction(self.w3_list[0], self.address, to_address=self.account_list[5])
        msg = self.ppos_noconsensus_5.getCandidateInfo(self.nodeid_list2[4])
        if msg['Data']== "":
            log.info("质押节点5成为验证节点")
            self.ppos_noconsensus_5.createStaking(0, self.account_list[4], self.nodeid_list2[4],
                                                  self.externalId, self.nodeName, self.website, self.details,
                                                  self.amount, self.programVersion)
        msg = self.ppos_noconsensus_5.getCandidateInfo(self.nodeid_list2[4])
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
        log.info("查询节点质押信息回去质押块高{}".format(stakingBlockNum))
        value_list = [10,11,12,13,14,15,16,17,18]
        for value in value_list:
            log.info("钱包6 委托金额{}".format(value))
            self.ppos_noconsensus_6.delegate(0, self.nodeid_list2[4], value)
        msg = self.ppos_noconsensus_6.getDelegateInfo(stakingBlockNum, self.account_list[5], self.nodeid_list2[4])
        log.info(msg)
        data = json.loads(msg["Data"])
        releasedHes = Web3.fromWei(data["ReleasedHes"], 'ether')
        log.info("查询委托的金额{}eth".format(releasedHes))
        delegate_value = 0
        for i in value_list:
            delegate_value = i + delegate_value
        assert delegate_value == releasedHes ,"委托的金额与查询到的金额不一致"
        for value in value_list:
            log.info("赎回的金额：{}eth".format(value))
            log.info("钱包6进行赎回")
            self.ppos_noconsensus_6.unDelegate(stakingBlockNum, self.nodeid_list2[4], value)
        log.info("赎回委托金额后查询委托信息")
        msg = self.ppos_noconsensus_6.getDelegateInfo(stakingBlockNum, self.account_list[5], self.nodeid_list2[4])
        """如果全部金额赎回，再查getDelegateInfo返回数据为空"""
        log.info(msg)
        # assert msg["Status"] == False
        # assert msg["ErrMsg"] == "Delegate info is not found"


