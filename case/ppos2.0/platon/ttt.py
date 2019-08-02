
import json
import math
import rlp
from common.load_file import LoadFile
from hexbytes import HexBytes
from client_sdk_python.eth import Eth
from conf import setting as conf
from common.connect import connect_web3
from client_sdk_python import (
    Web3,
)
import random
def read_private_key_list(key1,key2,key3=None,value=None):
    data = LoadFile (conf.PPOS_CONFIG_PATH).get_data ()
    if key3 == None:
        data[key1][key2] = value
    else:
        data[key1][key2][key3] = value

    data = json.dumps (data)
    with open (conf.PPOS_CONFIG_PATH, "w") as f:
        f.write (data)
        f.close ()
#     # if key2 :
#     #     data = LoadFile (conf.PPOS_CONFIG_PATH).get_data ()
#     #     data[key] = value
#     #     #print(data)
# def write_config(data):
#     data = json.dumps (data)
#     with open (conf.PPOS_CONFIG_PATH, "w") as f:
#         f.write(data)
#         f.close()
#
# def test():
#     data = LoadFile (conf.PPOS_CONFIG_PATH).get_data ()
#     data['EconomicModel']['Staking']['DelegateThreshold'] = 9
#     write_config(data)
if __name__ == '__main__':
    #update_config()
    #update_config('eth','SyncMode','one')
    #read_private_key_list('eth','SyncMode',value='one')
    read_private_key_list('EconomicModel','Staking','DelegateThreshold',8)