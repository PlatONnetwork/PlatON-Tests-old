
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



#a:结算周期时长
#b:当前验证人
#c:每个验证人出的块数
#d:出块间隔
#e:每个结算周期的共识轮数

#结算周期 e = a / b * c * d

#下个结算期的块数 = 当前块高 + 150

a  = 2173 % 150
print(a)
b = 150 - 73
print(b)

c = 2173 + b
print(c)