# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-22 11:05
@LastEditors: huang
@LastEditTime: 2019-07-22 11:05
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
from common.connect import connect_web3
from conf import setting as conf
from client_sdk_python.personal import (
    Personal,
)
from client_sdk_python.eth import Eth
from common.load_file import  get_node_info
from common import log
from common.str_util import StrUtil


def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number + 20
    else:
        return total_time - number + i + 20


# 构造各类合理的截止区块-块高数
def get_all_legal_end_and_effect_block_number(rpc_link,index,border):
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))
    # block_number=number

    # 设置截止块高 在第几个共识周期 N=index
    N = index

    # 共识周期的最大边界
    M= border

    if block_number % 250 == 0:
        end_number_list = [(block_number + 250 * N - 20, block_number + 250 * N+ (N + 5) * 250),
                           (block_number + 250 * N - 20, block_number + 250 * N+ (N + 8) * 250),
                           (block_number + 250 * M - 20, block_number + 250 * M+ (N + 10) * 250)]
    else:
        mod = block_number % 250
        interval = 250 - mod
        end_number_list = [(block_number + interval + 250 * N - 20, block_number + interval + 250 * N+ (N + 5) * 250),
                           (block_number + interval + 250 * N - 20, block_number + interval + 250 * N+ (N + 8) * 250),
                           (block_number + interval + 250 * M - 20, block_number + interval + 250 * M+ (N + 10) * 250)]
    return end_number_list


# 构造单个合理的截止块高和生效块高-块高数
def get_invalid_end_and_effect_block_number(rpc_link,index):
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))

    # 设置截止块高 在第几个共识周期 N=index
    N = index

    if block_number % 250 == 0:
        # 截止块高
        end_number = block_number + (N * 250) - 20

        # 生效块高
        effect_number = end_number + (N + 5) * 250
    else:
        mod = block_number % 250
        interval = 250 - mod
        # 截止块高
        end_number = block_number + interval + (N * 250) - 20

        # 生效块高
        effect_number = end_number + (N + 5) * 250
    return end_number, effect_number


# 构造各类不合理的截止区块-块高数
def get_all_invalid_end_block_number(rpc_link,index,border):
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))
    # block_number=number

    # 设置截止块高 在第几个共识周期 N=index
    N = index

    # 共识周期的最大边界
    M= border

    if block_number % 250 == 0:

        # 截止块高
        end_number = block_number + (N * 250) - 20

        # 生效块高
        effect_number = end_number + (N + 5) * 250

        end_number_list = [(None, effect_number),
                           ('number', effect_number),
                           ('0.a.0', effect_number),
                           (block_number, effect_number),
                           (block_number + 250 * N - 19, effect_number),
                           (block_number + 250 * M - 21, effect_number + 250 * M),
                           (block_number + 250 * (M + 1) - 20, effect_number + 250 * (M + 1))]
    else:
        mod = block_number % 250
        interval = 250 - mod

        # 截止块高
        end_number = block_number + interval + (N * 250) - 20

        # 生效块高
        effect_number = end_number + (N + 5) * 250

        end_number_list = [(None, effect_number),
                           ('number', effect_number),
                           ('0.a.0', effect_number),
                           (block_number, effect_number),
                           (block_number + interval + 250 * N - 19, effect_number),
                           (block_number + interval + 250 * M - 21, effect_number + 250 * M),
                           (block_number + interval + 250 * (M + 1) - 20, effect_number + 250 * (M + 1))]
    return end_number_list


# 构造各类不合理的生效区块-块高数
def get_all_invalid_effect_block_number(rpc_link,index):
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))
    # block_number=number

    # 设置截止块高 在第几个共识周期 N=index
    N = index

    if block_number % 250 == 0:
        # 截止块高
        end_number = block_number + (N * 250) - 20
        effect_number_list = [(end_number, None),
                              (end_number, 'number'),
                              (end_number, '0.a.0'),
                              (end_number, block_number),
                              (end_number, end_number),
                              (end_number, end_number + (N + 4) * 250),
                              (end_number, end_number + (N + 5) * 250 - 1),
                              (end_number, end_number + (N + 5) * 250 + 1),
                              (end_number, end_number + (N + 11) * 250)]
    else:
        mod = block_number % 250
        interval = 250 - mod

        # 截止块高
        end_number = block_number + interval + (N * 250) - 20
        effect_number_list = [(end_number, None),
                              (end_number, 'number'),
                              (end_number, '0.a.0'),
                              (end_number, block_number),
                              (end_number, end_number),
                              (end_number, end_number + (N + 4) * 250),
                              (end_number, end_number + (N + 5) * 250 - 1),
                              (end_number, end_number + (N + 5) * 250 + 1),
                              (end_number, end_number + (N + 11) * 250)]

    return effect_number_list


class TestGovern:
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.GOVERN_NODE_YML

    abi = conf.DPOS_CONTRACT_ABI
    file = conf.CASE_DICT

    node_info = get_node_info(node_yml_path)
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get('collusion')
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get('nocollusion')

    # 大量余额的账户
    address = Web3.toChecksumAddress(conf.ADDRESS)

    # 钱包私钥
    private_key = conf.PRIVATE_KEY
    pwd = conf.PASSWORD

    address_list = ["0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79", "0xE586041e95bea563C0835Db511c4ce1183E1A8d3",
                    "0x70C05d48740F912E9BBFA83EAAF67FF4e747477B"]

    private_key_list = ["b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357",
                       "61ba2dd3d2375d1c4138f85fae0cd10802021c743e3ecb86073c277c079c2822",
                       "a3d1652fed37c0353792b2cbcf35b39b01b07a7e81f1ee48ce2d8015632e6c1c"]

    def setup_class(self):
        # self.auto = AutoDeployPlaton(cbft=self.cbft_json_path)
        # self.auto.start_all_node(self.node_yml_path)

        self.ppos_link = Ppos(self.rpc_list[0], self.address)
        self.w3_list = [connect_web3(url) for url in self.rpc_list]

        """用新的钱包地址和未质押过的节点id封装对象"""
        self.no_link_1 = Ppos(self.rpc_list[0], self.address_list[0], privatekey= self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[0], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[0], self.address_list[2], privatekey=self.private_key_list[2])

        for to_account in self.address_list:
            self.transaction(self.w3_list[0],self.address,to_account)
        self.eth = Eth(self.w3_list[0])

    def transaction(self,w3, from_address, to_address=None, value=1000000000000000000000000000000000,gas=91000000, gasPrice=9000000000):
        personal = Personal(self.w3_list[0])
        personal.unlockAccount(self.address, self.pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': gas,
            'gasPrice': gasPrice,
            'value': value
        }
        tx_hash = w3.eth.sendTransaction(params)
        return tx_hash

    @allure.title('1-发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证')
    @pytest.mark.parametrize('github_id,new_version',
                             [(None, 1792), ('version', 1792), ('1001', None), ('1001', 'version')])
    @pytest.mark.parametrize('index,border', [(1, 5)])
    def test_submit_version_version_not_empty(self, github_id, new_version, index, border):
        '''
        用例id 9,12,19~22
        发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 节点ID和名称
        str = StrUtil(8)
        rand_str = str.gen_random_string()
        topic = 'topic'.join(rand_str)
        desc = 'desc'.join(rand_str)

        # 当前版本号
        new_version = new_version

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=rand_str, nodeName=rand_str,
                                            website='https://www.platon.network/#/', details='发起质押', amount=1100000,
                                            programVersion=new_version)

            log.info('质押结束：节点ID={}-钱包={}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number=get_invalid_end_and_effect_block_number(rpc_link,index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        new_version = 2048

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            msg = rpc_link.submitVersion(verifier=self.address, githubID=github_id, topic=topic, desc=desc,
                                         url='www.platon.network', newVersion=new_version,
                                         endVotingBlock=end_number,
                                         activeBlock=effect_number)
            # msg = rpc_link.submitVersion(self.address, github_id, topic, desc,'www.platon.network', new_version,end_number,effect_number)

            log.info('msg={}'.format(msg))
            assert msg.get('Status') == False, '升级版本号不正确，发起升级提案失败'
        except:
            log.info('发起升级提案失败')

    @allure.title('2-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性')
    @pytest.mark.parametrize('index,border', [(1, 5)])
    def test_submit_version_end_block_number(self, index, border):
        '''
        用例id 10,24~28,32~34
        发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 节点ID和名称
        str = StrUtil(8)
        rand_str = str.gen_random_string()
        topic = 'topic'.join(rand_str)
        desc = 'desc'.join(rand_str)

        # 当前版本号
        new_version = 1792

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=rand_str, nodeName=rand_str,
                                            website='https://www.platon.network/#/', details='发起质押', amount=1100000,
                                            programVersion=new_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list=get_all_invalid_end_block_number(rpc_link,index,border)

        # 升级版本号
        new_version = 2048

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            msg = rpc_link.submitVersion(verifier=self.address, githubID='101', topic=topic, desc=desc,
                                         url='https://www.platon.network/#/', newVersion=new_version,
                                         endVotingBlock=end_number,activeBlock=effect_number)
            assert msg.get('Status') == False, '截止区块块高不正确，发起升级提案失败'
        except:
            log.info('发起升级提案失败')

    @allure.title('3-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性')
    @pytest.mark.parametrize('index', [1])
    def test_submit_version_effect_block_number(self, index):
        '''
        用例id 11,38~43
        发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 节点ID和名称
        str = StrUtil(8)
        rand_str = str.gen_random_string()
        topic = 'topic'.join(rand_str)
        desc = 'desc'.join(rand_str)

        # 当前版本号
        new_version = 1792

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=rand_str, nodeName=rand_str,
                                            website='https://www.platon.network/#/', details='发起质押', amount=1100000,
                                            programVersion=new_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = get_all_invalid_effect_block_number(rpc_link, index)

        # 升级版本号
        new_version = 2048

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            msg = rpc_link.submitVersion(verifier=self.address, githubID='101', topic=topic, desc=desc,
                                         url='https://www.platon.network/#/', newVersion=new_version,
                                         endVotingBlock=end_number,
                                         activeBlock=effect_number)
            assert msg.get('Status') == False, '生效区块块高不正确，发起升级提案失败'
        except:
            log.info('发起升级提案失败')

    @allure.title('6-发起升级提案-升级提案成功的验证')
    @pytest.mark.parametrize('index,border', [(1,5)])
    def test_submit_version_success(self,index,border):
        '''
        用例id 15,18   正确的截止块高29~31,35~37,正确的生效块高44~46,47
        发起升级提案-升级提案成功的验证
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 节点ID和名称
        str = StrUtil(8)
        rand_str = str.gen_random_string()
        topic = 'topic'.join(rand_str)
        desc = 'desc'.join(rand_str)

        # 当前版本号
        new_version = 1792

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=rand_str, nodeName=rand_str,
                                            website='https://www.platon.network/#/', details='发起质押', amount=1100000,
                                            programVersion=new_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = get_all_legal_end_and_effect_block_number(rpc_link, index, border)

        # 升级版本号
        new_version=2048

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            msg = rpc_link.submitVersion(verifier=self.address, githubID='101', topic=topic, desc=desc,
                                            url='https://www.platon.network/#/', newVersion=new_version, endVotingBlock=end_number,
                                            activeBlock=effect_number)
            assert msg.get('Status') == True
            assert msg.get('ErrMsg') == 'ok','发起升级提案成功'
        except:
            log.info('发起升级提案失败')

    @allure.title('版本声明')
    def test_declare_version_nostaking_address(self):
        '''
        版本声明,非质押钱包进行版本声明失败
        '''
        # # 发送交易
        rpc_link = self.no_link_2
        version = rpc_link.getActiveVersion()
        personal = Personal(self.w3_list[0])
        amount = rpc_link.eth.getBalance(self.address_list[0])

        msg = rpc_link.declareVersion(self.nodeid_list2[0], version, self.address_list[0])
        assert msg.get('Status') == False
        assert msg.get('ErrMsg') == "Declare version error:tx sender should be node's staking address."

    @pytest.mark.parametrize('version',[1536,1792,1808,2048])
    def test_declare_version_noproposal(self,version):
        '''
        无有效的升级提案，进行版本声明,质押钱包进行版本声明链上版本号成功
        '''
        # # 发送交易
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        # version = rpc_link.getActiveVersion()
        amount = rpc_link.eth.getBalance(self.address_list[0])
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []
        for nodeid in node_info:
            candidate_list.append(node_info.get('NodeId'))
        for i in range(0,len(self.nodeid_list2)):
            if self.nodeid_list2[i] not in candidate_list:
                try:
                        msg = rpc_link.createStaking(0, self.address_list[0],
                                                            self.nodeid_list2[2], '11111', 'NodeName', 'Platon.com',
                                                            'detail',
                                                            1100000, 1792)
                        assert msg.get('Status') == True
                        assert msg.get('ErrMsg') == 'ok'
                except:
                    log.info('质押失败')
        try:
            if version == 1536:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
            elif version == 1792:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == True
            elif version == 1808:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
            else:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
        except:
            log.info('无有效升级提案，发起版本声明失败')

    def test_declare_version_hasproposal(self,version):
        '''
        有生效的升级提案，进行版本声明,质押钱包进行版本声明链上版本号成功
        '''
        # # 发送交易
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        if rpc_link.listproposal():
            try:
                self.test_submitversion()
            except:
                log.info('发起升级提案失败')
        # version = rpc_link.getActiveVersion()
        amount = rpc_link.eth.getBalance(self.address_list[0])
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []
        for nodeid in node_info:
            candidate_list.append(node_info.get('NodeId'))
        for i in range(0,len(self.nodeid_list2)):
            if self.nodeid_list2[i] not in candidate_list:
                try:
                        msg = rpc_link.createStaking(0, self.address_list[0],
                                                            self.nodeid_list2[2], '11111', 'NodeName', 'Platon.com',
                                                            'detail',
                                                            1100000, 1792)
                        assert msg.get('Status') == True
                        assert msg.get('ErrMsg') == 'ok'
                except:
                    log.info('质押失败')
        try:
            if version == 1536:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
            elif version == 1792:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == True
            elif version == 1808:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
            else:
                msg = rpc_link.declareVersion(self.nodeid_list2[2], version, Web3.toChecksumAddress(self.address_list[1]))
                assert msg.get('Status') == False
        except:
            log.info('无有效升级提案，发起版本声明失败')

    def test_getactiveversion(self):
        '''
        查询节点链生效的版本
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        log.info(rpc_link.getActiveVersion())

    def test_listproposal(self):
        '''
        查询提案列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        msg = rpc_link.listProposal()
        log.info(msg)

    def test_gettallyresult(self):
        '''
        查询节点列表
        :return:
        '''
        rpc_link = self.no_link_2
        ga2 = 21000 + 6000 + 32000 + 12000
        gas_price = rpc_link.web3.toWei(0.000000001, 'ether')
        rpc_link.eth.getBalance(self.address)
        msg = rpc_link.getTallyResult('111',self.address, gas_price, ga2)
        log.info(msg)

    def test(self):
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        msg = rpc_link.getCandidateInfo(self.nodeid_list2[2])
        log.info(msg)


if  __name__ == '__main__':
    pytest.main(["-s", "test_govern.py"])
