
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

a = 2510 % 250
b = 250 - (2510 % 250) +1
c = int (250 * (20/100))
#print(a)
print(b)
print(c)