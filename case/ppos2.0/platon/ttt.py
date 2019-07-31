
import json
import math
import rlp
from hexbytes import HexBytes
from client_sdk_python.eth import Eth
from conf import setting as conf
from common.connect import connect_web3
from client_sdk_python import (
    Web3,
)
import random
def read_private_key_list(self):
    with open(conf.PRIVATE_KEY_LIST,'r') as f:
        private_key_list = f.read().split("\n")
        index=random.randrange(1,len(private_key_list)-1)#生成随机行数
        address,private_key = private_key_list[index].split(',')
        print(address)
        print(private_key)

def update_config(key,value):
    with open(conf.PPOS_CONFIG_PATH, 'r', encoding='utf-8') as f:
        res = json.loads(f.read())
        res[key] = value
    return res

if __name__ == '__main__':
    update_config('SyncMode','one')