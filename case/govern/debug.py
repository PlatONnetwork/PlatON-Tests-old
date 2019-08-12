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
from conf import setting as conf
from utils.platon_lib.govern_util import *
from common.load_file import  get_node_info

from utils.platon_lib.govern_util import *


if __name__ == "__main__":
    # cbft_json_path = conf.CBFT2
    # node_yml_path = conf.GOVERN_NODE_YML
    #
    # node_info = get_node_info(node_yml_path)
    #
    # # 共识节点信息
    # rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get('nocollusion')

    # address = Web3.toChecksumAddress('0x493301712671ada506ba6ca7891f436d29185821')
    # new_address = Web3.toChecksumAddress('0xb2fC346DF94cBE871AF2ea56B9E56E477569FcDb')
    # privatekey = '0aea84e2169919c796b4983b130bf31ac152f78319f91f56563bd75cf842314c'

    # rpc_link = Ppos('http://10.10.8.157:6789', address, chainid=102, privatekey=privatekey)
    # rpc_link = Ppos('http://192.168.9.221:6789',address,chainid=101)
    # rpc_link = Ppos('http://192.168.120.121:6789', new_address, chainid=101,privatekey=privatekey)

    test = TestGovern()
    test.setup_class()

    # test.test_submit_version_version_not_empty()
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
    # test.test_vote_vote_success()
    # test.test_vote_candidate_to_verifier()
    # test.test_vote_verifier_withdraw()

    # test.test_declare_version_nostaking_address()
    # test.test_declare_version_noproposal_newnode()
    # test.test_declare_version_hasproposal_newnode()
    # test.test_declare_version_noproposal_Candidate()
    # test.test_declare_version_propsal_verifier()
    # test.test_declare_version_nopropsal_verifier()

    test.test_implementing_upgrade_a()

    # test.test_get_active_version()
    # test.test_get_proposal_list()
    # test.test_get_node_list()

    # verifier_list=get_current_verifier(rpc_link)
    # log.info(verifier_list)

    # # 获取截止、生效块高
    # block_number_list=get_cross_sellte_cycle_legal_end_and_effect_block_number(ppos,50,10,5)
    # end_number, effect_number = block_number_list[0][0],block_number_list[0][1]
    # log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))
    #
    # versoion=get_version(ppos,3)
    #
    # submit_version1(ppos,versoion,end_number, effect_number)

    # la=ppos.listProposal()
    # log.info(la)
    # flag=is_exist_ineffective_proposal_info(ppos)
    # print(flag)

    # log.info('aaa')
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
