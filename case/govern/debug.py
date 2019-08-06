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
import os
import time,random
import threading


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


# def transaction(from_address, to_address=None, value=1000000000000000000000000000000000,gas=91000000, gasPrice=9000000000):
#     privatekey = '0xa11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7'
#     platon_ppos = Ppos('http://10.10.8.157:6789', address, chainid=102, privatekey=privatekey)
#     platon_ppos.web3.personal.unlockAccount(address, 88888888, 666666)
#     params = {
#         'to': to_address,
#         'from': from_address,
#         'gas': gas,
#         'gasPrice': gasPrice,
#         'value': value
#     }
#     tx_hash = platon_ppos.eth.sendTransaction(params)
#
#     von=platon_ppos.eth.getBalance(to_address)
#     log.info('von={}'.format(von))
#     return tx_hash


if __name__ == "__main__":
    # # id='6f4d11f66b4d41c6b946cfca467e491d795eae02d6cdfb1b4d00e7a0f48524839251540dc71d0a9e0e8f5514789c2248774b1e7e3a3aa0e5393b7b7bbee9043e'

    # address=Web3.toChecksumAddress('0x493301712671ada506ba6ca7891f436d29185821')
    # new_address = Web3.toChecksumAddress('0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79')
    # privatekey = '0xa11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7'
    # ppos = Ppos('http://10.10.8.157:6789', address, chainid=102, privatekey=privatekey)

    # ppos = Ppos('http://192.168.9.221:6789',address,chainid=101)
    # ppos = Ppos('http://192.168.120.121:6789', address, chainid=101,privatekey=privatekey)

    # transaction(address,new_address)
    # von = ppos.eth.getBalance(new_address)
    # log.info('von={}'.format(von))


    test=TestGovern()
    test.setup_class()
    # test.test_submit_version_version_not_empty()
    # test.test_submit_ineffective_verify()
    # test.test_submit_version_end_block_number()
    # test.test_submit_version_effect_block_number()
    test.test_submit_version_success()
    # test.test_submit_ineffective_verify()
    # test.test_submit_version_on_newnode()
    # test.test_submit_version_on_candidatenode()

    # test.test_vote_vote_trans()
    # test.test_vote_notin_vote_cycle_a()
    # test.test_vote_notin_vote_cycle_b()
    # test.test_vote_notin_vote_cycle_c()
    # test.test_vote_vote_double_cycle()
    # test.test_vote_vote_version_error()
    # test.test_vote_new_node_vote()
    # test.test_vote_candidate_node_vote()

    # test.test_declare_version_nostaking_address()
    # test.test_declare_version_noproposal_newnode()
    # test.test_declare_version_hasproposal_newnode()
    # test.test_declare_version_noproposal_Candidate()
    # test.test_declare_version_propsal_verifier()
    # test.test_declare_version_nopropsal_verifier()

    # test.test_get_active_version()
    # test.test_get_proposal_list()
    # test.test_get_node_list()

    # if proposal_list!='null':
    #     log.info('当前链上存在生效的升级提案，该用例执行失败')
    # else:
    #     log.info('2')
    #     pass
    # delay_time=20
    # def thread_fun(delay_time):
    #     count=0
    #     while 1:
    #         count=count+1
    #         print(count)
    #         if count>=delay_time:
    #             break
    #
    # # def start_operate(delay_time):
    # t = threading.Thread(target=thread_fun,args=(delay_time,))
    #     # t.setDaemon(True)
    # t.start()
    # t.join()

    # start_operate(20)




