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
    ConsensusSize = 50
    chainid = 101

    def link_list(self):
        rpc_lastlist = []
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, self.nodeid_list, ip_list, port_list = node_info.get (
            'collusion')
        for i in self.rpc_list:
            self.web3 = connect_web3 (i)
            if self.web3.isConnected():
                rpc_lastlist.append(i)
        log.info("目前可连接节点列表:{}".format(rpc_lastlist))
        index = random.randint (0, len(rpc_lastlist) - 1)
        url = rpc_lastlist[index]
        log.info("当前连接节点：{}".format(url))
        return url

    def get_block_number(self):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)
        current_block = platon_ppos.eth.blockNumber
        differ_block = self.ConsensusSize - (current_block % self.ConsensusSize)
        current_end_block = current_block + differ_block
        log.info ('当前块高：{} ，当前共识轮最后一个块高：{}'.format (current_block,current_block + differ_block))

        while 1:
            time.sleep (self.time_interval)
            current_block = platon_ppos.eth.blockNumber
            differ_block = self.ConsensusSize - (current_block % self.ConsensusSize)
            log.info ('当前块高度：{}，还差块高：{}'.format ((current_block),differ_block))
            if current_block > current_end_block :
                break


    def read_out_nodeId(self, code):
        node_info = get_node_info (self.node_yml_path)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
            code)
        node_list_length = len (nodeid_list)
        index = random.randint (0, node_list_length - 1)
        nodeId = nodeid_list[index]
        print (nodeId)


    def test(self):
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)
        # print(self.nodeid_list)


    def update_config(self,key1, key2, key3=None, value=None,file = conf.PPOS_CONFIG_PATH):
        data = LoadFile (file).get_data ()
        if key3 == None:
            data[key1][key2] = value
        else:
            data[key1][key2][key3] = value

        data = json.dumps (data)
        with open (conf.PPOS_CONFIG_PATH, "w") as f:
            f.write (data)
            f.close ()

    def read_private_key_list(file=conf.PRIVATE_KEY_LIST):
        with open (file, 'r') as f:
            private_key_list = f.read ().split ("\n")
            index = random.randrange (1, len (private_key_list) - 1)  # 生成随机行数
            address, private_key = private_key_list[index].split (',')
        return address, private_key


if __name__ == '__main__':
    a = CommonMethod()
    #a.get_block_number()
    a.link_list()