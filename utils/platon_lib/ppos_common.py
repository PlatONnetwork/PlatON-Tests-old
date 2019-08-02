# -*- coding: utf-8 -*-

import json
import random
from conf import  setting as conf
from common.load_file import LoadFile




def update_config(key1, key2, key3=None, value=None,file = conf.PPOS_CONFIG_PATH):
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