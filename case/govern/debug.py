# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-25 20:36
@LastEditors: huang
@LastEditTime: 2019-07-25 20:36
@Description:
"""
import json
import math
import time
import random
import allure
import pytest

from deploy.deploy import AutoDeployPlaton
from client_sdk_python import Web3
from utils.platon_lib.ppos import Ppos

from conf import setting as conf

from common.load_file import  get_node_info
from common import log
from common.str_util import StrUtil

from case.govern.test_govern import TestGovern


def number_add(self, a, b):
    self.result = a + b
    print('a+b')
    return self.result

# class TestDebug:
    # @allure.title("{a}-{b}")
    # @pytest.mark.parametrize('a,b',[('',4),(6,'a'),('aa',66)])
    # def test_check_param(self,a,b):
    #     status=0
    #     try:
    #         number_add(a,b)
    #     except:
    #         status=1
    #     assert status == 1, '两个数相加发生错误，{}加{}'.format(a, b)

if __name__ == "__main__":
    # block_len=6
    # for count in range(block_len):
    #     print('{}'.format(count)) 1750 7
    # pytest.main(["-s", "debug.py"])
    # list=get_all_invalid_end_block_number(1651,1,11)

    # list = get_all_invalid_end_block_number(1750, 1,11)

    # len=len(list)
    # for end_number,effect_number in(list):
    #     print(end_number,effect_number)

    # end_number,effect_number=get_invalid_end_and_effect_block_number(1500,2)
    # print(end_number,effect_number)

    # [(None,1792),('version',1792),('1001',None),('1001','version'),('1001',1793),('1001',1794)]

    # p = Ppos('http://192.168.120.121:6789', '0x493301712671ada506ba6ca7891f436d29185821', 101)
    # yes_node_id = '9bb716064d8dc7b6ac92b3562c7ccafa52a448e33aaa979b0b77ed26cc4b7ffabd647f53496bf781c53e8557bc88083aac8fb91fcffdeab989cd8aab39fc0d12'
    # no_node_id = '6f4d11f66b4d41c6b946cfca467e491d795eae02d6cdfb1b4d00e7a0f48524839251540dc71d0a9e0e8f5514789c2248774b1e7e3a3aa0e5393b7b7bbee9043e'

    # dict_result=p.getCandidateInfo(yes_node_id)
    # list1=p.getCandidateList()
    # list2=p.getVerifierList()
    # list3=p.getValidatorList()
    # print(list3)
    # print(dict_result)
    # print(dict_result['Status'])

    # # id='6f4d11f66b4d41c6b946cfca467e491d795eae02d6cdfb1b4d00e7a0f48524839251540dc71d0a9e0e8f5514789c2248774b1e7e3a3aa0e5393b7b7bbee9043e'
    # address=Web3.toChecksumAddress('0x493301712671ada506ba6ca7891f436d29185821')
    # new_address = Web3.toChecksumAddress('0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79')
    # privatekey = 'b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357'
    #
    # # ppos = Ppos('http://192.168.9.221:6789',address,chainid=101)
    # ppos = Ppos('http://192.168.120.121:6789', address, chainid=101,privatekey=privatekey)
    # # 单位 wei
    # gas_price = ppos.web3.toWei(0.000000000000000001, 'ether')
    # # gas_price=30000
    # # 交易gas数
    # gas1 = 30000
    # # 交易金额
    # amount1 = 1000000000
    # # ppos.send_raw_transaction('', address,new_address, 0, 0, amount1)

    test=TestGovern()
    test.setup_class()

    # @pytest.mark.parametrize('github_id,new_version',
    #                          [(None, 1792), ('version', 1792), ('1001', None), ('1001', 'version')])
    # @pytest.mark.parametrize('index,border', [(1, 5)])

    test.test_submit_version_version_not_empty(None, 7, 1, 5)
    # test.test_submit_version_end_block_number(1, 5)
    # test.test_submit_version_effect_block_number(1)
    # test.test_submit_version_success(1,5)

    # result=test.rpc_link2.listProposal()
    # ver=test.rpc_link2.getActiveVersion()
    # param=test.rpc_link2.listParam()

    # list=test.rpc_link2.getVerifierList()
    # list=test.rpc_link2.getValidatorList()

    # ls=test.no_link_1.getVerifierList()
    # print(ls)
