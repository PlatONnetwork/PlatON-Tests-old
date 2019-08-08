
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

gasPrice = Web3.toWei (0.000000000000000001, 'ether')
a = 159000
b = 60000000000000
c = 9540000000000000000
print(a*b)
d = (a*b) - c
print(d)