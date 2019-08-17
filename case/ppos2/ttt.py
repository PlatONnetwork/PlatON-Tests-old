
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





# a = 900000000000000000000 - (900000000000000000000*(20/100))
# b = 997076800000000000000
# c = a -b
# print(c)
# print(int(a))
# 720000000000000000000
# 720000000000000000000
amount = 900
aa = Web3.toWei (amount-(amount * 0.2), 'ether')
print(aa)