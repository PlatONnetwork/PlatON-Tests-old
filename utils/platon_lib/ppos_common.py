# -*- coding: utf-8 -*-


import random
import time
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from common import log
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info,get_node_list
from deploy.deploy import AutoDeployPlaton
from common.connect import connect_web3

import json

class CommonMethod():
    address = conf.ADDRESS
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_TEST_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    gasPrice = Web3.toWei (0.000000000000000001, 'ether')
    gas = 21000
    transfer_gasPrice = Web3.toWei (1, 'ether')
    transfer_gas = 210000000
    value = 1000
    time_interval = 10
    #ConsensusSize = 50
    ExpectedMinutes = 180
    chainid = 101

    def link_list(self):
        '''
        获取随机一个可以连接正常节点url
        :return:
        '''
        rpc_lastlist = []
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, self.nodeid_list, ip_list, port_list = node_info.get (
            'collusion')
        for i in self.rpc_list:
            self.web3 = connect_web3 (i)
            if self.web3.isConnected():
                rpc_lastlist.append(i)
        if rpc_lastlist:
            #log.info("目前可连接节点列表:{}".format(rpc_lastlist))
            index = random.randint (0, len(rpc_lastlist) - 1)
            url = rpc_lastlist[index]
            log.info("当前连接节点：{}".format(url))
            return url
        else:
            log.info("无可用节点")

    def get_next_settlement_interval(self,number = 1,file = conf.PLATON_CONFIG_PATH):
        '''
        获取下个结算周期
        :param :
        :return:
        '''
        data = LoadFile (file).get_data ()
        ExpectedMinutes = data['EconomicModel']['Common']['ExpectedMinutes']
        Interval = data['EconomicModel']['Common']['Interval']
        PerRoundBlocks = data['EconomicModel']['Common']['PerRoundBlocks']
        ValidatorCount = data['EconomicModel']['Common']['ValidatorCount']
        Consensuswheel = (ExpectedMinutes * 60) // (Interval * PerRoundBlocks * ValidatorCount)
        ConsensusSize = Consensuswheel * (Interval * PerRoundBlocks * ValidatorCount)
        ConsensusSize = ConsensusSize * number
        log.info("结算周期块高：{}".format(ConsensusSize))
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        current_block = platon_ppos.eth.blockNumber
        differ_block = ConsensusSize - (current_block % ConsensusSize)
        current_end_block = current_block + differ_block
        log.info ('当前块高：{} ，下个结算周期结束块高：{}'.format (current_block,current_end_block))

        while 1:
            time.sleep (self.time_interval)
            current_block = platon_ppos.eth.blockNumber
            differ_block = ConsensusSize - (current_block % ConsensusSize)
            log.info ('当前块高度：{}，还差块高：{}'.format ((current_block),differ_block))
            if current_block > current_end_block :
                break

    def get_next_consensus_wheel(self,number = 1,file = conf.PLATON_CONFIG_PATH):
        '''
        获取下个共识轮
        :param :
        :return:
        '''
        data = LoadFile (file).get_data ()
        Interval = data['EconomicModel']['Common']['Interval']
        PerRoundBlocks = data['EconomicModel']['Common']['PerRoundBlocks']
        ValidatorCount = data['EconomicModel']['Common']['ValidatorCount']
        ConsensusSize = Interval * PerRoundBlocks * ValidatorCount
        ConsensusSize = ConsensusSize * number
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        current_block = platon_ppos.eth.blockNumber
        differ_block = ConsensusSize - (current_block % ConsensusSize)
        current_end_block = current_block + differ_block
        log.info ('当前块高：{} ，下个共识轮周期结束块高：{}'.format (current_block,current_end_block))

        while 1:
            time.sleep (self.time_interval)
            current_block = platon_ppos.eth.blockNumber
            differ_block = ConsensusSize - (current_block % ConsensusSize)
            log.info ('当前块高度：{}，还差块高：{}'.format ((current_block),differ_block))
            if current_block > current_end_block :
                break


    def read_out_nodeId(self, code):
        """
        读取节点id列表
        :param code: 共识节点或者非共识节点标识
        :return:
        """
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
            code)
        node_list_length = len (nodeid_list)
        index = random.randint (0, node_list_length - 1)
        nodeId = nodeid_list[index]
        return nodeId


    def test(self):
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)
        # print(self.nodeid_list)

    def query_blockNumber(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        while 1:
            current_block = platon_ppos.eth.blockNumber
            time.sleep(10)
            print(current_block)


    def update_config(self,key1, key2, key3=None, value=None,file = conf.PLATON_CONFIG_PATH):
        '''
        修改config配置参数
        :param key1: 第一层级key
        :param key2: 第二层级key
        :param key3: 第三层级key
        :param value:
        :param file:
        :return:
        '''
        data = LoadFile (file).get_data ()
        if key3 == None:
            data[key1][key2] = value
        else:
            data[key1][key2][key3] = value

        data = json.dumps (data)
        with open (conf.PLATON_CONFIG_PATH, "w") as f:
            f.write (data)
            f.close ()

    def read_private_key_list(file=conf.PRIVATE_KEY_LIST):
        '''
        随机获取一组钱包地址和私钥
        :return:
        '''
        with open (file, 'r') as f:
            private_key_list = f.read ().split ("\n")
            index = random.randrange (1, len (private_key_list) - 1)  # 生成随机行数
            address, private_key = private_key_list[index].split (',')
        return address, private_key

    def get_no_candidate_list(self):
        '''
        获取未被质押的节点ID列表
        :return:
        '''
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get ('nocollusion')
        no_candidate_list = []
        for index in range (len (nodeid_list)):
            nodeid = nodeid_list[index]
            result = platon_ppos.getCandidateInfo (nodeid)
            flag = result['Status']

            if not flag:
                no_candidate_list.append (nodeid)
        if no_candidate_list :
            node_list_length = len (no_candidate_list)
            index = random.randint (0, node_list_length - 1)
            nodeId = no_candidate_list[index]
            return nodeId
        else:
            CommonMethod.start_init(self)
            # self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get ('nocollusion')
            return nodeid_list[0]


    def start_init(self):
        #修改config参数
        CommonMethod.update_config(self,'EconomicModel','Common','ExpectedMinutes',3)
        CommonMethod.update_config(self,'EconomicModel','Common','PerRoundBlocks',10)
        CommonMethod.update_config(self,'EconomicModel','Common','ValidatorCount',5)
        CommonMethod.update_config(self,'EconomicModel','Staking','ElectionDistance',20)
        CommonMethod.update_config(self,'EconomicModel','Staking','StakeThreshold',1000)
        #启动节点
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)

    def View_available_nodes(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get ('nocollusion')
        candidateinfo = platon_ppos.getCandidateList ()
        candidateinfo = candidateinfo.get('Data')
        candidate_list = []
        for nodeid in candidateinfo:
            candidate_list.append(nodeid.get('NodeId'))

        if set(nodeid_list) <= set(candidate_list):
            CommonMethod.start_init(self)




if __name__ == '__main__':
    a = CommonMethod()
    #a.get_block_number()
    #a.read_out_nodeId('nocollusion')
    #a.link_list()
    #a.update_config('EconomicModel','Staking','ElectionDistance',2)
    #a.test()
    #a.query_blockNumber()
    #a.get_no_candidate_list()
    #a.start_init()
    #a.View_available_nodes()
    a.get_no_candidate_list()