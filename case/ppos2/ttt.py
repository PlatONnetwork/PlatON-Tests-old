
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

a = Web3.toWei (1000, 'ether')
b = Web3.toWei (800, 'ether')
a =1042190400000000000000 +50000000000000000000
print(a)
b = 1092190400000000000000 - a
print(b)