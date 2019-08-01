# -*- coding: utf-8 -*-

import json
import random
from conf import  setting as conf
from common.load_file import LoadFile





def read_private_key_list(key1, key2, key3=None, value=None):
    data = LoadFile (conf.PPOS_CONFIG_PATH).get_data ()
    if key3 == None:
        data[key1][key2] = value
    else:
        data[key1][key2][key3] = value

    data = json.dumps (data)
    with open (conf.PPOS_CONFIG_PATH, "w") as f:
        f.write (data)
        f.close ()

def read_private_key_list(self):
    with open (conf.PRIVATE_KEY_LIST, 'r') as f:
        private_key_list = f.read ().split ("\n")
        index = random.randrange (1, len (private_key_list) - 1)  # 生成随机行数
        address, private_key = private_key_list[index].split (',')
    return address, private_key