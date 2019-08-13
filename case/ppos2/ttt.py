
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
c =900000000000000000000 - (900000000000000000000 *  0.2)
d = c -576000000000000000000
print('d',int(d))
print('c',int(c))

a =995851360000000000000 + 800000000000000000000 - int(c)
print(a)
b = 995851360000000000000 - a
print(b)

