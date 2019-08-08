# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-25 20:36
@LastEditors: huang
@LastEditTime: 2019-07-25 20:36
@Description:
"""
from case.govern.test_govern import TestGovern
from common import log
from utils.platon_lib.ppos import Ppos
from client_sdk_python import Web3
import json
import os
import time,random
import threading

from common.govern_util import *


# def number_add(self, a, b):
#     self.result = a + b
#     print('a+b')
#     return self.result

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

def get_proposal(rpc_link):
    '''
    判断链上是否存在有效的升级提案-用于判断是否可以发起投票
    :param rpc_link:
    :return:
    '''
    # result = rpc_link.listProposal()
    # proposalinfo = result.get('Data')
    proposalinfo='null'

    # if not result.get('Data'):
    #     log.info('查询提案列表失败')
    #     while 1:
    #         if result.get('Data'):
    #             flag=True
    #             break
    #     return flag
    if proposalinfo=='null' or proposalinfo ==False:
        log.info('查询提案列表失败')
        while 1:
            if proposalinfo:
                flag = True
                break
        return flag
    else:
        log.info('查询提案列表成功')
        flag = False
        return flag

if __name__ == "__main__":
    address=Web3.toChecksumAddress('0x493301712671ada506ba6ca7891f436d29185821')
    new_address = Web3.toChecksumAddress('0xb2fC346DF94cBE871AF2ea56B9E56E477569FcDb')
    privatekey = '0aea84e2169919c796b4983b130bf31ac152f78319f91f56563bd75cf842314c'

    # ppos = Ppos('http://10.10.8.157:6789', address, chainid=102, privatekey=privatekey)
    # ppos = Ppos('http://192.168.9.221:6789',address,chainid=101)
    # ppos = Ppos('http://192.168.120.121:6789', new_address, chainid=101,privatekey=privatekey)


    # la=ppos.listProposal()
    # log.info(la)
    # flag=is_exist_ineffective_proposal_info(ppos)
    # print(flag)


    # result = ppos.listProposal()
    # proposalinfo = result.get('Data')
    # print(proposalinfo)

    # if not result.get('Data'):
    #     log.info('查询提案列表失败')
    #     while 1:
    #         if result.get('Data'):
    #             print('1-True')
    #             break
    # else:
    #     print('2-True')

    # flag=get_proposal(ppos)
    # log.info(flag)

    # flag=is_exist_ineffective_proposal_info(ppos)
    # log.info(flag)
    # list=ppos.listProposal()
    # ls=len(list)
    #
    # print(ls)
    # print(list)
    # if False==True:
    #     print('False')
    # elif True==True:
    #     print('True')
    # elif False==False:
    #     print('aa1')
    # else:
    #     print('aaa')
    #
    # if not 'test':
    #     print('4')
    # else:
    #     print('5')

    # if None ==False:
    #     print('a')
    # else:
    #     print('b')

    # if not None:
    #     print('a')


    test=TestGovern()
    test.setup_class()
    test.test_submit_version_version_not_empty()
    # test.test_submit_version_end_block_number()
    # test.test_submit_version_effect_block_number()
    # test.test_submit_version_on_newnode()
    # test.test_submit_version_on_candidatenode()
    # test.test_submit_version_success()
    # test.test_submit_ineffective_verify()

    # test.test_vote_vote_trans()

    # test.test_vote_notin_vote_cycle_a()
    # test.test_vote_notin_vote_cycle_b()
    # test.test_vote_notin_vote_cycle_c()

    # test.test_vote_new_node_vote()
    # test.test_vote_candidate_node_vote()
    # test.test_vote_vote_double_cycle()
    # test.test_vote_vote_version_error()
    # test.test_vote_vote_success()

    # test.test_declare_version_nostaking_address()
    # test.test_declare_version_noproposal_newnode()
    # test.test_declare_version_hasproposal_newnode()
    # test.test_declare_version_noproposal_Candidate()
    # test.test_declare_version_propsal_verifier()
    # test.test_declare_version_nopropsal_verifier()

    # test.test_get_active_version()
    # test.test_get_proposal_list()
    # test.test_get_node_list()

    # log.info('aaa')

