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
from common.operate_block_number import OperateBlockNumber
from common.operate_version import OperateVersion

def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number + 20
    else:
        return total_time - number + i + 20


def get_candidate_no_verify(rpc_link):
    '''
    获取当前结算周期非验证人的候选人列表
    :return:
    '''
    revice = rpc_link.getCandidateList()
    revice = rpc_link.getVerifierList()
    node_info1 = revice.get('Data')
    node_info2 = revice.get('Data')
    candidate_list = []
    verifier_list = []

    for nodeid in node_info1:
        candidate_list.append(nodeid.get('NodeId'))
    for nodeid in node_info2:
        verifier_list.append(nodeid.get('NodeId'))

    candidate_no_verify_list = []
    for list1 in candidate_list:
        if list1 not in verifier_list:
            candidate_no_verify_list.append(list1)
    return  candidate_no_verify_list

def get_staking_address(rpc_link,nodeid):
    '''
    根据节点id获取质押钱包地址
    :param rpc_link:
    :param nodeid:
    :return:
    '''
    revice = rpc_link.getCandidateList()
    nodeinfo = revice.get('Data')
    nodeid_list = []
    for nd in nodeinfo:
        nodeid_list.append(nd.get('NodeId'))
    if nodeid not in nodeid_list:
        log.info('输入的节点未质押成为候选人')
        return
    else:
        revice2 = rpc_link.getCandidateInfo(nodeid)
        nodeinfo2 = revice.get('Data')
        stakingaddress = nodeinfo2.get('StakingAddress')
        return  stakingaddress

def submitversion():
    pass


class TestGovern:
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.GOVERN_NODE_YML
    node_info = get_node_info(node_yml_path)

    # 共识节点信息
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get('collusion')

    # 非共识节点信息
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get('nocollusion')

    # 内置账户-拥有无限金额
    address = Web3.toChecksumAddress(conf.ADDRESS)

    # 钱包私钥
    private_key = conf.PRIVATE_KEY

    # 内置账户密码-拥有无限金额
    pwd = conf.PASSWORD

    # 没有绑定节点的钱包地址
    address_list = ["0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79", "0xE586041e95bea563C0835Db511c4ce1183E1A8d3",
                    "0x70C05d48740F912E9BBFA83EAAF67FF4e747477B"]

    # 没有绑定节点的钱包私钥
    private_key_list = ["b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357",
                       "61ba2dd3d2375d1c4138f85fae0cd10802021c743e3ecb86073c277c079c2822",
                       "a3d1652fed37c0353792b2cbcf35b39b01b07a7e81f1ee48ce2d8015632e6c1c"]

    # 共识周期块高数
    conse_size=250

    # 设置截止块高 在第几个共识周期
    index=1

    # 共识周期个数的最大边界值
    border=5

    # 随机字符个数
    length=6

    # 节点的第三方主页
    website = 'https://www.platon.network/#/'

    # 节点的描述
    details = '发起升级提案'

    # 提案在github上的id
    github_id = '101'

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

        # 获取处理区块块高的对象
        self.operate_block=OperateBlockNumber(self.no_link_1,self.conse_size,self.index,self.border)

        # 获取随机生成字符的对象
        self.rand_str = StrUtil(self.length)

        str = self.rand_str.gen_random_string()
        self.topic = 'topic'.join(str)
        self.desc = 'desc'.join(str)

        # # 当前版本号
        # cur_version_result = self.no_link_1.getActiveVersion()
        # self.cur_version = cur_version_result['Data']

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
    def test_submit_version_version_not_empty(self):
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

        # 当前版本号
        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包={}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number=self.operate_block.get_invalid_end_and_effect_block_number()
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version1 = OperateVersion(rpc_link,1)
        version2 = OperateVersion(rpc_link,2)
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()

        # 版本号参数列表
        version_list = [None, 'version',new_version1,new_version2]

        try:
            for new_version in version_list:
                if new_version==version_list[0]:
                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number,from_address=new_address)
                    log.info('msg={}'.format(msg))
                    assert msg.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（为空）,发起升级提案失败'
                elif new_version==version_list[1]:
                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('msg={}'.format(msg))
                    assert msg.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（格式不正确），发起升级提案失败'
                elif new_version==version_list[2]:
                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('msg={}'.format(msg))
                    assert msg.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（升级目的版本号<=链上当前版本号），发起升级提案失败'
                elif new_version==version_list[3]:
                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('msg={}'.format(msg))
                    assert msg.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（升级目标版本的大版本号等于链上当前版本号，升级目的版本号为小版本号大于链上链上当前小版本号），发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败')

    @allure.title('2-发起升级提案-未生效的升级提案的验证')
    def test_submit_ineffective_verify(self):
        '''
        用例id 16,17
        发起升级提案-未生效的升级提案的验证
        '''

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 升级版本号
        version = OperateVersion(rpc_link,3)
        new_version = version.get_version()

        # 获取升级提案列表信息
        proposal_list=rpc_link.listProposal()

        # 判断是否存在有效的升级提案
        if proposal_list:
            try:
                # 发起升级提案 版本号=0.0.7 即为：1792->2048
                end_number = block_list[0][0]
                effect_number = block_list[0][1]

                log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                             url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                             activeBlock=effect_number, from_address=new_address)

                assert msg.get('Status') == False,'有未生效的升级提案，发起升级提案失败'
            except:
                log.info('发起升级提案请求失败')
        else:
            log.info('不存在有效的升级提案')

    @allure.title('3-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性')
    def test_submit_version_end_block_number(self):
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

        # 当前版本号
        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list=self.operate_block.get_all_invalid_end_block_number()

        # 升级版本号
        version = OperateVersion(rpc_link,3)
        new_version = version.get_version()

        try:
            for count in range(len(block_list)):
                if count==0:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，不能为空，发起升级提案失败'
                elif count==1:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，格式不正确，发起升级提案失败'
                elif count == 2:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，格式不正确，发起升级提案失败'
                elif count == 3:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，不能等于当前块高，发起升级提案失败'
                elif count == 4:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
                elif count == 5:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
                elif count == 6:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '截止区块块高不正确，为N+1周期的第230块块高，发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败')

    @allure.title('3-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性')
    def test_submit_version_effect_block_number(self):
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

        # 当前版本号
        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_invalid_effect_block_number()

        # 升级版本号
        version = OperateVersion(rpc_link, 3)
        new_version = version.get_version()

        try:
            for count in range(len(block_list)):
                if count == 0:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高设置为=number，发起升级提案失败'
                elif count == 1:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高设置为=0.a.0，发起升级提案失败'
                elif count == 2:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高设置为=当前块高，发起升级提案失败'
                elif count == 3:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高设置为=截止块高，发起升级提案失败'
                elif count == 4:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 4)个共识周期的第230块块高，发起升级提案失败'
                elif count == 5:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第229块块高，发起升级提案失败'
                elif count == 6:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第231块块高，发起升级提案失败'
                elif count == 7:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert msg.get('Status') == False, '生效区块块高不正确，为第(N + 11)个共识周期的第250块块高，发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败')

    @allure.title('4-发起升级提案-升级提案成功的验证')
    def test_submit_version_success(self):
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

        # 当前版本号
        version= OperateVersion(rpc_link)
        cur_version=version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 升级版本号
        version = OperateVersion(rpc_link,3)
        new_version = version.get_version()

        try:
        # 发起升级提案 版本号=0.0.7 即为：1792->2048
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            msg = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                     url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                     activeBlock=effect_number, from_address=new_address)
            assert msg.get('Status') == True
            assert msg.get('ErrMsg') == 'ok','发起升级提案成功'
        except:
            log.info('发起升级提案请求失败')

    @allure.title('5-对升级提案进行投票-投票交易的验证的验证')
    def test_vote_trans_verify(self):
        '''
        用例id 48~50
        对升级提案进行投票-投票交易的验证的验证
        '''
        rpc_link=self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 版本号
        version1 = OperateVersion(rpc_link,1)
        little_version = version1.get_version()

        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        version_list=[None,'node_version',little_version,cur_version]

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option='Yeas'
        proposal_id=1091

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=1100000,
                                            programVersion=cur_version)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        try:
            for node_version in version_list:
                if node_version is None:
                    msg=rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=node_version)
                    assert msg.get('Status') == False,'发起升级投票交易时节点版本号不正确（为空）'
                elif node_version =='node_version':
                    msg = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert msg.get('Status') == False,'发起升级投票交易时节点版本号不正确（格式不正确）'
                elif node_version ==version1:
                    msg = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert msg.get('Status') == False,'发起升级投票交易时节点版本号不正确（小于提案升级版本号）'
                elif node_version == cur_version:
                    msg = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert msg.get('Status') == False,'发起升级投票交易时节点版本号不正确（等于提案升级版本号）'
                else:
                    pass
        except:
            log.info('对升级提案进行投票请求失败')

    @allure.title('版本声明')
    def test_declare_version_nostaking_address(self):
        '''
        版本声明,非质押钱包进行版本声明失败
        '''
        rpc_link = self.no_link_2

        # 版本号
        version = OperateVersion(rpc_link)
        cur_version = version.get_version()

        try:
            msg = rpc_link.declareVersion(self.nodeid_list2[0], cur_version, self.address_list[0])
            assert msg.get('Status') == False
            assert msg.get('ErrMsg') == "Declare version error:tx sender should be node's staking address."
        except:
            log.info('test_declare_version_nostaking_address验证失败')

    @allure.title('无有效的升级提案，新节点进行版本声明')
    def test_declare_version_noproposal_newnode(self):
        '''
        无有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = OperateVersion(rpc_link)
        version1 = OperateVersion(rpc_link, 1)
        version2 = OperateVersion(rpc_link, 2)
        version3 = OperateVersion(rpc_link, 3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        # 版本号参数列表
        version_list=[new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_list=rpc_link.listProposal()
        if proposal_list:
            log.info('当前链上存在生效的升级提案，该用例执行失败')
        else:
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            # 判断配置文件中的节点是否都已质押
            if set(self.nodeid_list2) < set(candidate_list):
                log.info('节点配置文件中的地址已全部质押，该用例执行失败')
            else:
                for i in range(0, len(self.nodeid_list2)):
                    if self.nodeid_list2[i] not in candidate_list:
                        try:
                            for version in version_list:
                                if version == version_list[0]:
                                    msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert msg.get('Status') == False
                                elif version == version_list[1]:
                                    msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert msg.get('Status') == False
                                elif version == version_list[2]:
                                    msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert msg.get('Status') == False
                                elif version == version_list[3]:
                                    msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert msg.get('Status') == False
                                else:
                                    pass
                        except:
                            log.info('test_declare_version_noproposal_newnode验证失败')
                        break

    @allure.title('存在有效的升级提案，新节点进行版本声明')
    def test_declare_version_hasproposal_newnode(self):
        '''
        版本声明-存在有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = OperateVersion(rpc_link)
        version1 = OperateVersion(rpc_link, 1)
        version2 = OperateVersion(rpc_link, 2)
        version3 = OperateVersion(rpc_link, 3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_list = rpc_link.listProposal()
        if proposal_list:
            log.info('当前链上存在生效的升级提案，该用例执行失败')
            try:
                submitversion()
            except:
                log.info('发起升级提案失败')

        # 获取候选人的节点id
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        if (set(self.nodeid_list2) < set(candidate_list)):
            log.info('节点配置文件中的地址已全部质押,用例执行失败')
        else:
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    try:
                        for version in version_list:
                            if version == version_list[0]:
                                msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert msg.get('Status') == False
                            elif version == version_list[1]:
                                msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert msg.get('Status') == False
                            elif version == version_list[2]:
                                msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert msg.get('Status') == False
                            elif version == version_list[3]:
                                msg = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert msg.get('Status') == False
                            else:
                                pass
                    except:
                        log.info('test_declare_version_hasproposal_newnode验证失败')
                    break

    @allure.title('不存在有效的升级提案，候选节点进行版本声明')
    def test_declare_version_noproposal_Candidate(self):
        '''
        版本声明-不存在有效的升级提案，候选节点进行版本声明
        '''

        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = OperateVersion(rpc_link)
        version1 = OperateVersion(rpc_link, 1)
        version2 = OperateVersion(rpc_link, 2)
        version3 = OperateVersion(rpc_link, 3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        n_list = get_candidate_no_verify()

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行版本声明，不存在就先进行质押
        if n_list:
            dv_nodeid = n_list[0]
        else:
            # 获取候选人节点id列表
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    try:
                        msg = rpc_link.createStaking(0, self.address_list[0],
                                                     self.nodeid_list2[i], self.rand_str, self.rand_str, self.website,
                                                     self.details,1100000, version0)
                        dv_nodeid = self.nodeid_list2[i]
                        assert msg.get('Status') == True
                        assert msg.get('ErrMsg') == 'ok'
                    except:
                        log.info('质押失败')
                    break
            try:
                for version in version_list:
                    if version == version_list[0]:
                        msg = rpc_link.declareVersion(self.dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    elif version == version_list[1]:
                        msg = rpc_link.declareVersion(self.dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == True
                    elif version == version_list[2]:
                        msg = rpc_link.declareVersion(self.dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    elif version == version_list[3]:
                        msg = rpc_link.declareVersion(self.dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    else:
                        pass
            except:
                log.info('test_declare_version_noproposal_Candidate验证失败')

    @allure.title('存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_propsal_verifier(self):
        '''
        版本声明-存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = OperateVersion(rpc_link)
        version1 = OperateVersion(rpc_link, 1)
        version2 = OperateVersion(rpc_link, 2)
        version3 = OperateVersion(rpc_link, 3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断链上是否存在有效的升级提案，不存在则提交升级提案
        proposal_list = rpc_link.listProposal()
        if not proposal_list:
            try:
                submitversion()
            except:
                log.info('提交升级提案失败')

        # 获取验证人id列表
        revice = rpc_link.getVerifierList()
        node_info = revice.get('Data')
        verifier_list = []

        for nodeid in node_info:
            verifier_list.append(node_info.get('NodeId'))

        for i in range(0, len(verifier_list)):
            if verifier_list[i] not in self.nodeid_list:
                dv_nodeid = verifier_list[i]
                break

        if not dv_nodeid:
            log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')
        else:
            try:
                for version in version_list:
                    if version == version_list[0]:
                        msg = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    elif version == version_list[1]:
                        msg = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == True
                    elif version == version_list[2]:
                        msg = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    elif version == version_list[3]:
                        msg = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert msg.get('Status') == False
                    else:
                        pass
            except:
                log.info('test_declare_version_propsal_verifier验证失败')

    @allure.title('不存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_nopropsal_verifier(self):
        '''
        版本声明-不存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = OperateVersion(rpc_link)
        version1 = OperateVersion(rpc_link, 1)
        version2 = OperateVersion(rpc_link, 2)
        version3 = OperateVersion(rpc_link, 3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断是否存在有效的升级提案
        proposal_list = rpc_link.listProposal()
        if proposal_list:
            log.info('存在有效的升级提案，该用例执行失败')
        else:
            revice = rpc_link.getVerifierList()
            node_info = revice.get('Data')
            verifier_list = []

            for nodeid in node_info:
                verifier_list.append(node_info.get('NodeId'))

            for i in range(0, len(verifier_list)):
                if verifier_list[i] not in self.nodeid_list:
                    dv_nodeid = verifier_list[i]
                    break

            # 判断是否存在验证
            if dv_nodeid:
                try:
                    for version in version_list:
                        if version == version_list[0]:
                            msg = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert msg.get('Status') == False
                        elif version == version_list[1]:
                            msg = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert msg.get('Status') == True
                        elif version == version_list[2]:
                            msg = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert msg.get('Status') == False
                        elif version == version_list[3]:
                            msg = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert msg.get('Status') == False
                        else:
                            pass
                except:
                    log.info('test_declare_version_nopropsal_verifier验证失败')
            else:
                log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')

    @allure.title('查询节点链生效的版本')
    def test_getactiveversion(self):
        '''
        查询节点链生效的版本
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        log.info('查询节点链生效的版本={}'.format(rpc_link.getActiveVersion()))

    @allure.title('查询提案列表')
    def test_listproposal(self):
        '''
        查询提案列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        msg = rpc_link.listProposal()

        log.info('查询提案列表,msg={}'.format(msg))

    @allure.title('查询节点列表')
    def test_gettallyresult(self):
        '''
        查询节点列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address, chainid=101, privatekey=self.private_key)

        ga2 = 21000 + 6000 + 32000 + 12000

        gas_price = rpc_link.web3.toWei(0.000000001, 'ether')

        rpc_link.eth.getBalance(self.address)

        msg = rpc_link.getTallyResult('111', self.address, gas_price, ga2)

        log.info('查询节点列表,msg={}'.format(msg))


if  __name__ == '__main__':
    pytest.main(["-s", "test_govern.py"])
