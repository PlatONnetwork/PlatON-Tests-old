# -*- coding: utf-8 -*-

import json
import math
import time
import random

import allure
import pytest
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos
from conf import  setting as conf
from common import log
import json
from utils.platon_lib.ppos_common import CommonMethod
from deploy.deploy import AutoDeployPlaton



class TestLockeDpositionConfig:
    address = conf.ADDRESS
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.PPOS_NODE_TEST_YML
    file = conf.CASE_DICT
    privatekey = conf.PRIVATE_KEY
    gasPrice = 60000000000000
    gas = 21000
    transfer_gasPrice = Web3.toWei (1, 'ether')
    transfer_gas = 210000000
    value = 1000
    chainid = 101
    ConsensusSize = 250
    time_interval = 10
    initial_amount = {'FOUNDATION': 905000000000000000000000000,
                      'FOUNDATIONLOCKUP': 20000000000000000000000000,
                      'STAKING': 25000000000000000000000000,
                      'INCENTIVEPOOL': 45000000000000000000000000,
                      'DEVELOPERS': 5000000000000000000000000
                      }
    def test(self):
        CommonMethod.update_config('EconomicModel','Common','StakeThreshold',1000)
        self.auto = AutoDeployPlaton ()
        self.auto.start_all_node (self.node_yml_path)

    def initial_unlock_Normal(self,amount):
        url = CommonMethod.link_list (self)
        platon_ppos = Ppos (url, self.address, self.chainid)

        address1, private_key1 = CommonMethod.read_private_key_list ()

        # 签名转账
        result = platon_ppos.send_raw_transaction ('', Web3.toChecksumAddress (conf.ADDRESS),
                                                   Web3.toChecksumAddress (address1),
                                                   self.transfer_gasPrice, self.gas, self.value, conf.PRIVATE_KEY)
        return_info = platon_ppos.eth.waitForTransactionReceipt (result)
        if return_info is not None:
            nodeId = CommonMethod.read_out_nodeId (self,'nocollusion')
            platon_ppos2 = Ppos (url, address1, self.chainid, private_key1)
            result = platon_ppos2.createStaking (1, address1, nodeId, 'externalId', 'nodeName', 'website', 'details',
                                                 amount, 1792, gasPrice=self.gasPrice)
            assert result['status'] == True, "申请质押返回的状态：{},用例失败".format (result['status'])


if __name__ == '__main__':
    a = TestLockeDpositionConfig()
    a.initial_unlock_Normal(1000)