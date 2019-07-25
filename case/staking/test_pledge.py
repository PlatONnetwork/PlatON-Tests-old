# -*- coding: utf-8 -*-

import json
import math
import time

from client_sdk_python import Web3
from common.connect import connect_web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info
from common import log
from deploy.deploy import AutoDeployPlaton

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
    rpc_list += rpc_list2
    enode_list += enode_list2
    nodeid_list += nodeid_list2
    ip_list += ip_list2
    port_list += port_list2
    key_list = ["node" + str(i) for i in range(1, 1 + len(rpc_list))]
    print(key_list)
    rpc_dict = dict(zip(key_list, rpc_list))
    enode_dict = dict(zip(key_list, enode_list))
    nodeid_dict = dict(zip(key_list, nodeid_list))
    ip_dict = dict(zip(key_list, ip_list))
    port_dict = dict(zip(key_list, port_list))

    def hellp(self):
        print("1")


if __name__ == '__main__':
    a = TestPledge()
    a.hellp()





