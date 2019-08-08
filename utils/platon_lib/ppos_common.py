# -*- coding: utf-8 -*-


import random

from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info,get_node_list
from deploy.deploy import AutoDeployPlaton
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

    def ppos_link(self, url=None, address=conf.ADDRESS, privatekey=conf.PRIVATE_KEY):
        if url is None:
            node_info = get_node_info (self.node_yml_path)
            self.rpc_list, enode_list, self.nodeid_list, ip_list, port_list = node_info.get (
                'collusion')
            rpc_list_length = len (self.rpc_list)
            index = random.randint (0, rpc_list_length - 1)
            url = self.rpc_list[index]
        self.platon_ppos = Ppos (url, address=address, chainid=101,
                                 privatekey=privatekey)
        return self.platon_ppos


    def ppos_Girokonto(self, to_address, from_address, private_key, value):
        platon_ppos = self.ppos_link ()

        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (from_address),
                                                   Web3.toChecksumAddress (to_address), self.transfer_gasPrice,
                                                   self.transfer_gas, value,
                                                   private_key)
        print (result)


    def ppos_sendTransaction(self, to_address, from_address, value):
        platon_ppos = self.ppos_link ()
        platon_ppos.web3.personal.unlockAccount (conf.ADDRESS, conf.PASSWORD, 2222)

        self.send_data = {
            "to": to_address,
            "from": from_address,
            "gas": self.transfer_gas,
            "gasPrice": self.transfer_gasPrice,
            "value": value,
        }
        tx_hash = platon_ppos.eth.sendTransaction (self.send_data)
        self.platon_ppos.eth.waitForTransactionReceipt (tx_hash)


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

    def read_private_key_list(self,file=conf.PRIVATE_KEY_LIST):
        with open (file, 'r') as f:
            private_key_list = f.read ().split ("\n")
            index = random.randrange (1, len (private_key_list) - 1)  # 生成随机行数
            address, private_key = private_key_list[index].split (',')
        return address, private_key