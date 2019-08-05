# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-22 11:05
@LastEditors: huang
@LastEditTime: 2019-07-22 11:05
@Description:
"""

import allure
import pytest

import time
import threading

from client_sdk_python import Web3
from conf import setting as conf
from utils.platon_lib.ppos import Ppos

from common.load_file import  get_node_info
from common import log
from common.govern_util import GovernUtil
from common.govern_util import gen_random_string

from deploy.deploy import AutoDeployPlaton
from common.connect import connect_web3
from client_sdk_python.personal import (
    Personal,
)
from client_sdk_python.eth import Eth


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
    border=2

    # 随机字符个数
    length=6

    # 节点的第三方主页
    website = 'https://www.platon.network/#/'

    # 节点的描述
    details = '发起升级提案'

    # 提案在github上的id
    github_id = '101'

    # 时间间隔-秒
    time_interval=21

    # 基本的gas
    base_gas = 21000

    # 基本的gasprice
    base_gas_price=60000000000000

    # 每次转账的金额
    trans_amount=100000000000000000000000000

    # 进行质押的gas
    staking_gas = base_gas + 32000 + 6000 + 100000

    # 发起提案的gas
    proposal_gas = base_gas + 450000 + 9000 + 50000

    # 发起投票的gas
    vote_gas = base_gas + 2000 + 9000 + 50000

    # 发起版本声明的gas
    declare_gas=base_gas + 3000 + 9000 + 50000

    # 进行质押的金额
    staking_amount=10000000

    # 发起提案的金额
    proposal_amount=10000000

    # 发起投票的金额
    vote_amount=10000000

    # 发起版本声明的金额
    declare_amount=10000000

    def setup_class(self):
        # self.auto = AutoDeployPlaton(cbft=self.cbft_json_path)
        # self.auto.start_all_node(self.node_yml_path)

        self.link_1 = Ppos(self.rpc_list[0], self.address)

        # 新钱包地址和私钥
        self.no_link_1 = Ppos(self.rpc_list[0], self.address_list[0], privatekey= self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[0], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[0], self.address_list[2], privatekey=self.private_key_list[2])

        # self.w3_list = [connect_web3(url) for url in self.rpc_list]
        # for to_account in self.address_list:
        #     self.transaction(self.w3_list[0],self.address,to_account)

        # 默认初始化后，给所有钱包进行转账处理
        for to_account in self.address_list:
            self.transaction(self.address,to_account)

        # 获取处理区块块高的对象
        self.operate_block=GovernUtil(self.no_link_1,self.conse_size,self.index,self.border)

        # 获取随机生成字符的对象 随机设置主题和说明
        self.rand_str = gen_random_string(self.length)
        self.topic = 'topic'.join(self.rand_str)
        self.desc = 'desc'.join(self.rand_str)

    # 重新部署链
    def re_deploy(self):
        self.auto = AutoDeployPlaton(self.cbft_json_path)
        self.auto.kill_of_yaml(self.node_yml_path)
        self.auto.start_all_node(self.node_yml_path)

        # self.link_1 = Ppos(self.rpc_list[0], self.address)
        #
        # # 新钱包地址和私钥
        # self.no_link_1 = Ppos(self.rpc_list[0], self.address_list[0], privatekey=self.private_key_list[0])
        # self.no_link_2 = Ppos(self.rpc_list[0], self.address_list[1], privatekey=self.private_key_list[1])
        # self.no_link_3 = Ppos(self.rpc_list[0], self.address_list[2], privatekey=self.private_key_list[2])
        #
        # # 默认初始化后，给所有钱包进行转账处理
        # for to_account in self.address_list:
        #     self.transaction(self.address, to_account)
        #
        # # 获取处理区块块高的对象
        # self.operate_block = GovernUtil(self.no_link_1, self.conse_size, self.index, self.border)
        #
        # # 获取随机生成字符的对象 随机设置主题和说明
        # self.rand_str = gen_random_string(self.length)
        # self.topic = 'topic'.join(self.rand_str)
        # self.desc = 'desc'.join(self.rand_str)

    def transaction(self,from_address, to_address=None):
        self.link_1.web3.personal.unlockAccount(self.address, self.pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': self.base_gas,
            'gasPrice': self.base_gas_price,
            'value': self.trans_amount
        }
        tx_hash = self.link_1.eth.sendTransaction(params)
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
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        log.info('cur_version={}'.format(cur_version))

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包={}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number=self.operate_block.get_invalid_end_and_effect_block_number()
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version1 = GovernUtil(rpc_link,flag=1)
        version2 = GovernUtil(rpc_link,flag=2)
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()

        # 版本号参数列表
        version_list = [None, 'version',new_version1,new_version2]

        try:
            for new_version in version_list:
                if new_version==version_list[0]:
                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number,from_address=new_address)
                    log.info('result={}'.format(result))
                    assert result.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（为空）,发起升级提案失败'
                elif new_version==version_list[1]:
                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('result={}'.format(result))
                    assert result.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（格式不正确），发起升级提案失败'
                elif new_version==version_list[2]:
                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('result={}'.format(result))
                    assert result.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（升级目的版本号<=链上当前版本号），发起升级提案失败'
                elif new_version==version_list[3]:
                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    log.info('result={}'.format(result))
                    assert result.get('Status') == False, '提交升级提案参数中升级目的版本号不正确（升级目标版本的大版本号等于链上当前版本号，升级目的版本号为小版本号大于链上链上当前小版本号），发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败-test_submit_version_version_not_empty')

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
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 升级版本号
        version = GovernUtil(rpc_link,flag=3)
        new_version = version.get_version()

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            try:
                # 发起升级提案 版本号=0.0.7 即为：1792->2048
                end_number = block_list[0][0]
                effect_number = block_list[0][1]

                log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                             url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                             activeBlock=effect_number, from_address=new_address)

                assert result.get('Status') == False
                assert 'error' in result.get('ErrMsg'), '有未生效的升级提案，发起升级提案失败'
            except:
                log.info('发起升级提案请求失败')
        else:
            log.info('不存在有效的升级提案-test_submit_ineffective_verify')

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
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包={}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list=self.operate_block.get_all_invalid_end_block_number()

        # 升级版本号
        version = GovernUtil(rpc_link,flag=3)
        new_version = version.get_version()

        try:
            for count in range(len(block_list)):
                if count==0:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，不能为空，发起升级提案失败'
                elif count==1:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，格式不正确，发起升级提案失败'
                elif count == 2:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，格式不正确，发起升级提案失败'
                elif count == 3:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，不能等于当前块高，发起升级提案失败'
                elif count == 4:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
                elif count == 5:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
                elif count == 6:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '截止区块块高不正确，为N+1周期的第230块块高，发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败-test_submit_version_end_block_number')

    @allure.title('4-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性')
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
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_invalid_effect_block_number()

        # 升级版本号
        version = GovernUtil(rpc_link,flag=3)
        new_version = version.get_version()

        try:
            for count in range(len(block_list)):
                if count == 0:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高设置为=None，发起升级提案失败'
                elif count == 1:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高设置为=number，发起升级提案失败'
                elif count == 2:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高设置为=0.a.0，发起升级提案失败'
                elif count == 3:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高设置为=当前块高，发起升级提案失败'
                elif count == 4:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高设置为=截止块高，发起升级提案失败'
                elif count == 5:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 4)个共识周期的第230块块高，发起升级提案失败'
                elif count == 6:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第229块块高，发起升级提案失败'
                elif count == 7:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第231块块高，发起升级提案失败'
                elif count == 8:
                    end_number = block_list[count][0]
                    effect_number = block_list[count][1]

                    log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                    result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic,
                                                 desc=self.desc,
                                                 url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                                 activeBlock=effect_number, from_address=new_address)
                    assert result.get('Status') == False, '生效区块块高不正确，为第(N + 11)个共识周期的第250块块高，发起升级提案失败'
                else:
                    pass
        except:
            log.info('发起升级提案请求失败-test_submit_version_effect_block_number')

    @allure.title('5-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案')
    def test_submit_version_on_newnode(self):
        '''
        用例id 14
        发起升级提案-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        log.info('当前生成的提案升级版本号={}'.format(new_version))

        # 获取候选人的节点id
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        if set(self.nodeid_list2) < set(candidate_list):
            log.info('节点配置文件中的地址已全部质押,用例执行失败')
        else:
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    try:
                        # 发起升级提案 版本号=0.0.7 即为：1792->2048
                        end_number = block_list[0][0]
                        effect_number = block_list[0][1]

                        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

                        result = rpc_link.submitVersion(verifier=self.nodeid_list2[i], githubID=self.github_id, topic=self.topic,
                                                     desc=self.desc,
                                                     url=self.website, newVersion=new_version,
                                                     endVotingBlock=end_number,
                                                     activeBlock=effect_number, from_address=new_address)
                        assert result.get('Status') == False, '发起升级提案时，该节点是新人节点，而不是验证人节点，发起升级提案失败'
                    except:
                        log.info('发起升级提案请求失败-test_submit_version_on_newnode')
                    break

    @allure.title('6-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案')
    def test_submit_version_on_candidatenode(self):
        '''
        用例id 13
        发起升级提案-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        log.info('当前生成的提案升级版本号为={}'.format(new_version))

        opver = GovernUtil(rpc_link)
        n_list = opver.get_candidate_no_verify()

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
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
                        result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i], externalId=self.rand_str,nodeName=self.rand_str,
                                                        website=self.website, details=self.details,amount=self.staking_amount,
                                                        programVersion=cur_version, gasPrice=self.base_gas_price,gas=self.staking_gas)
                        dv_nodeid = self.nodeid_list2[i]
                        assert result.get('Status') == True
                        assert result.get('ErrMsg') == 'ok'
                    except:
                        log.info('质押失败')
                    break
        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            result = rpc_link.submitVersion(verifier=dv_nodeid, githubID=self.github_id, topic=self.topic,
                                         desc=self.desc,
                                         url=self.website, newVersion=new_version,
                                         endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == False, '发起升级提案时，该节点是候选人节点，而不是验证人节点，发起升级提案失败'
        except:
            log.info('发起升级提案请求失败-test_submit_version_on_candidatenode')

    @allure.title('7-发起升级提案-升级提案成功的验证')
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
        version= GovernUtil(rpc_link)
        cur_version=version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            # result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,nodeName=self.rand_str,
            #                                 website=self.website, details=self.details,amount=self.staking_amount,value=self.staking_amount,
            #                                 programVersion=cur_version, privatekey=rpc_link.privatekey,gasPrice=self.base_gas_price,gas=self.staking_gas)
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str, nodeName=self.rand_str,
                                            website=self.website, details=self.details, amount=self.staking_amount,
                                            value=self.staking_amount,
                                            programVersion=cur_version, privatekey=rpc_link.privatekey,from_address=self.address,
                                            gasPrice=self.base_gas_price, gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 升级版本号
        version = GovernUtil(rpc_link,flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

            result = rpc_link.submitVersion(verifier=node_id,url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                            activeBlock=effect_number, from_address=new_address,gasPrice=self.base_gas_price,gas=self.proposal_gas)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok','发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_submit_version_success')

    @allure.title('8-对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）')
    def test_vote_vote_trans(self):
        '''
        用例id 48~50
        对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）
        '''
        rpc_link=self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 版本号
        version1 =GovernUtil(rpc_link,flag=1)
        little_version = version1.get_version()

        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}'.format(little_version,cur_version))

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
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,nodeName=self.rand_str,
                                            website=self.website, details=self.details,amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 在等待一定时间后再投票
        time.sleep(self.time_interval)

        try:
            for node_version in version_list:
                if node_version is None:
                    result=rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=node_version)
                    assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（为空）'
                elif node_version =='node_version':
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（格式不正确）'
                elif node_version ==version1:
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（小于提案升级版本号）'
                elif node_version == cur_version:
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                    assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（等于提案升级版本号）'
                else:
                    pass
        except:
            log.info('对升级提案进行投票请求失败-test_vote_vote_trans')

    @allure.title('9-对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20')
    def test_vote_notin_vote_cycle_a(self):
        '''
        用例id 51,54
        对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20
        '''

        # 投票前重新部署链
        # self.re_deploy()
        # time.sleep(120)

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,
                                            nodeName=self.rand_str,
                                            website=self.website, details=self.details,
                                            amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number_for_vote()

        end_number = block_list[0][0]
        effect_number = block_list[0][1]

        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                         url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_vote_notin_vote_cycle_a')

        govern = GovernUtil(rpc_link, end_number=end_number)

        # 当查询到当前块高在截止块高后进行投票，投票是不成功的
        t = threading.Thread(target=govern.get_block_number())
        t.start()
        t.join()

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        try:
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            assert result.get('Status') == False,'发起升级投票交易时，不在投票周期，投票不成功'
        except:
            log.info('对升级提案进行投票请求失败-test_vote_notin_vote_cycle_a')

    @allure.title('10-对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1) - 20')
    def test_vote_notin_vote_cycle_b(self):
        '''
        用例id 52,55
        对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1) - 20
        '''

        # 投票前重新部署链
        # self.re_deploy()
        # time.sleep(120)

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,
                                            nodeName=self.rand_str,
                                            website=self.website, details=self.details,
                                            amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number_for_vote()

        end_number = block_list[1][0]
        effect_number = block_list[1][1]

        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                         url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_vote_notin_vote_cycle_a')

        govern = GovernUtil(rpc_link, end_number=end_number)

        # 当查询到当前块高在截止块高后进行投票，投票是不成功的
        t = threading.Thread(target=govern.get_block_number())
        t.start()
        t.join()

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        try:
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'
        except:
            log.info('对升级提案进行投票请求失败-test_vote_notin_vote_cycle_b')

    @allure.title('11-对升级提案进行投票-是否在投票周期内的验证 conse_size * M- 20')
    def test_vote_notin_vote_cycle_c(self):
        '''
        用例id 53,56
        对升级提案进行投票-是否在投票周期内的验证 conse_size * M- 20
        '''

        # 投票前重新部署链
        # self.re_deploy()
        # time.sleep(120)

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,
                                            nodeName=self.rand_str,
                                            website=self.website, details=self.details,
                                            amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number_for_vote()

        end_number = block_list[2][0]
        effect_number = block_list[2][1]

        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                         url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_vote_notin_vote_cycle_a')

        govern = GovernUtil(rpc_link, end_number=end_number)

        # 当查询到当前块高在截止块高后进行投票，投票是不成功的
        t = threading.Thread(target=govern.get_block_number())
        t.start()
        t.join()

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        try:
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'
        except:
            log.info('对升级提案进行投票请求失败-test_vote_notin_vote_cycle_c')

    @allure.title('12-对升级提案进行投票-是否已经投票过的验证')
    def test_vote_vote_double_cycle(self):
        '''
        用例id 59
        对升级提案进行投票-是否已经投票过的验证
        '''

        # 投票前重新部署链
        # self.re_deploy()
        # time.sleep(120)

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,
                                            nodeName=self.rand_str,
                                            website=self.website, details=self.details,
                                            amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number_for_vote()

        end_number = block_list[0][0]
        effect_number = block_list[0][1]

        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                         url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_vote_vote_double_cycle')

        # 在等待一定时间后再投票
        time.sleep(self.time_interval)

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        try:
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级投票成功'
        except:
            log.info('对升级提案进行投票请求失败-test_vote_vote_double_cycle')

        # 在等待一定时间后再投票
        time.sleep(self.time_interval)

        try:
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            assert result.get('Status') == False, '发起升级投票交易时，之前已经透过票，投票不成功'
        except:
            log.info('对升级提案进行投票请求失败-test_vote_vote_double_cycle')

    @allure.title('13-对升级提案进行投票-节点版本号的验证')
    def test_vote_vote_version_error(self):
        '''
        用例id 60
        对升级提案进行投票-节点版本号的验证
        '''

        # 投票前重新部署链
        # self.re_deploy()
        # time.sleep(120)

        rpc_link = self.no_link_1
        new_address = rpc_link.address
        node_id = self.nodeid_list2[0]

        # 获取质押节点信息
        result_list = rpc_link.getCandidateInfo(node_id)
        log.info('质押节点信息={}'.format(result_list))

        # 当前版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        # 发起质押
        if result_list['Status'] == False:
            log.info('钱包{}未质押过，需要进行质押'.format(new_address))
            log.info('质押开始：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))

            # 进行质押
            result = rpc_link.createStaking(0, new_address, node_id, externalId=self.rand_str,
                                            nodeName=self.rand_str,
                                            website=self.website, details=self.details,
                                            amount=self.staking_amount,
                                            programVersion=cur_version, gasPrice=self.base_gas_price,
                                            gas=self.staking_gas)

            log.info('质押结束：节点ID={}-钱包{}未质押过，需要进行质押'.format(node_id, new_address))
            log.info('质押后返回的结果为：{}'.format(result))
        else:
            log.info('钱包={}，已经质押过，不需要进行质押'.format(new_address))
            pass

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number_for_vote()

        end_number = block_list[0][0]
        effect_number = block_list[0][1]

        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 升级版本号
        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        try:
            # 发起升级提案 版本号=0.0.7 即为：1792->2048
            result = rpc_link.submitVersion(verifier=node_id, githubID=self.github_id, topic=self.topic, desc=self.desc,
                                         url=self.website, newVersion=new_version, endVotingBlock=end_number,
                                         activeBlock=effect_number, from_address=new_address)
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
        except:
            log.info('发起升级提案请求失败-test_vote_vote_version_error')

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link, flag=1)
        version2 = GovernUtil(rpc_link, flag=2)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,new_version))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2]

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        # 在等待一定时间后再投票
        time.sleep(self.time_interval)

        try:
            for version in version_list:
                if version==version_list[0]:
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=version)
                    assert result.get('Status') == False, '对升级提案进行投票时，节点版本号不等于提案升级版本号，投票不成功'
                elif version==version_list[1]:
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=version)
                    assert result.get('Status') == False, '对升级提案进行投票时，节点版本号不等于提案升级版本号，投票不成功'
                elif version==version_list[2]:
                    result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=version)
                    assert result.get('Status') == False, '对升级提案进行投票时，节点版本号不等于提案升级版本号，投票不成功'
                else:pass
        except:
            log.info('对升级提案进行投票请求失败-test_vote_vote_version_error')

    @allure.title('14-对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）')
    def test_vote_new_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）
        '''

        # 投票前重新部署链
        # self.re_deploy()

        rpc_link = self.no_link_1
        node_id = self.nodeid_list2[0]

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        log.info('当前生成的提案升级版本号为={}'.format(new_version))

        # 获取候选人的节点id
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        if set(self.nodeid_list2) < set(candidate_list):
            log.info('节点配置文件中的地址已全部质押,用例执行失败')
        else:
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    try:
                        result = rpc_link.vote(verifier=self.nodeid_list2[i], proposalID=proposal_id, option=option,programVersion=new_version)
                        assert result.get('Status') == False, '对升级提案进行投票时，该节点是候选人节点，而不是验证人节点，投票失败'
                    except:
                        log.info('对升级提案进行投票请求失败-test_vote_new_node_vote')
                    break

    @allure.title('14-对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）')
    def test_vote_candidate_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）
        '''
        rpc_link = self.no_link_1
        new_address = rpc_link.address

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        block_list = self.operate_block.get_all_legal_end_and_effect_block_number()

        # 版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()

        version = GovernUtil(rpc_link,flag=3)
        new_version = version.get_version()

        log.info('当前生成的提案升级版本号为={}'.format(new_version))

        opver = GovernUtil(rpc_link)
        n_list = opver.get_candidate_no_verify()

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
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
                        result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i], externalId=self.rand_str,
                                                        nodeName=self.rand_str,
                                                        website=self.website, details=self.details,
                                                        amount=self.staking_amount,
                                                        programVersion=cur_version, gasPrice=self.base_gas_price,
                                                        gas=self.staking_gas)
                        dv_nodeid = self.nodeid_list2[i]
                        assert result.get('Status') == True
                        assert result.get('ErrMsg') == 'ok'
                    except:
                        log.info('质押失败')
                    break

        # Yeas 0x01 支持
        # Nays 0x02 反对
        # Abstentions 0x03 弃权
        option = 'Yeas'
        proposal_id = 1091

        version = GovernUtil(rpc_link, flag=3)
        new_version = version.get_version()

        log.info('当前生成的提案升级版本号为={}'.format(new_version))

        try:
            result = rpc_link.vote(verifier=self.nodeid_list2[i], proposalID=proposal_id, option=option,
                                programVersion=new_version)
            assert result.get('Status') == False, '对升级提案进行投票时，该节点是候选人节点，而不是验证人节点，投票失败'
        except:
            log.info('发起升级提案请求失败-test_vote_candidate_node_vote')

    @allure.title('9-非质押钱包进行版本声明')
    def test_declare_version_nostaking_address(self):
        '''
        版本声明-非质押钱包进行版本声明
        '''
        rpc_link = self.no_link_2

        # 版本号
        version = GovernUtil(rpc_link)
        cur_version = version.get_version()
        log.info('当前版本号为：{}'.format(cur_version))

        try:
            result = rpc_link.declareVersion(self.nodeid_list[0], cur_version, self.address_list[1])
            assert result.get('Status') == False
            assert result.get('ErrMsg') == "Declare version error:tx sender should be node's staking address."
        except:
            log.info('进行版本声明-test_declare_version_nostaking_address-验证失败')

    @allure.title('10-无有效的升级提案，新节点进行版本声明')
    def test_declare_version_noproposal_newnode(self):
        '''
        版本声明-无有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link,flag=1)
        version2 = GovernUtil(rpc_link,flag=2)
        version3 = GovernUtil(rpc_link,flag=3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0,new_version1, new_version2,new_version3))

        # 版本号参数列表
        version_list=[new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info=rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list!='null':
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
                                    result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert result.get('Status') == False
                                elif version == version_list[1]:
                                    result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert result.get('Status') == False
                                elif version == version_list[2]:
                                    result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert result.get('Status') == False
                                elif version == version_list[3]:
                                    result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                                  Web3.toChecksumAddress(self.address_list[1]))
                                    assert result.get('Status') == False
                                else:
                                    pass
                        except:
                            log.info('进行版本声明-test_declare_version_noproposal_newnode-验证失败')
                        break

    @allure.title('11-存在有效的升级提案，新节点进行版本声明')
    def test_declare_version_hasproposal_newnode(self):
        '''
        版本声明-存在有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link, flag=1)
        version2 = GovernUtil(rpc_link, flag=2)
        version3 = GovernUtil(rpc_link, flag=3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('当前链上存在生效的升级提案，该用例执行失败')
            try:
                opver=GovernUtil(rpc_link)
                opver.submitversion()
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
                                result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert result.get('Status') == False
                            elif version == version_list[1]:
                                result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert result.get('Status') == False
                            elif version == version_list[2]:
                                result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert result.get('Status') == False
                            elif version == version_list[3]:
                                result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                              Web3.toChecksumAddress(self.address_list[1]))
                                assert result.get('Status') == False
                            else:
                                pass
                    except:
                        log.info('进行版本声明-test_declare_version_hasproposal_newnode-验证失败')
                    break

    @allure.title('12-不存在有效的升级提案，候选节点进行版本声明')
    def test_declare_version_noproposal_Candidate(self):
        '''
        版本声明-不存在有效的升级提案，候选节点进行版本声明
        '''

        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link, flag=1)
        version2 = GovernUtil(rpc_link, flag=2)
        version3 = GovernUtil(rpc_link, flag=3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        opver = GovernUtil(rpc_link)
        n_list = opver.get_candidate_no_verify()

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行版本声明，不存在就先进行质押
        if n_list:
            dv_nodeid= n_list[0]
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
                        result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i],
                                                        externalId=self.rand_str,
                                                        nodeName=self.rand_str,
                                                        website=self.website, details=self.details,
                                                        amount=self.staking_amount,
                                                        programVersion=new_version0, gasPrice=self.base_gas_price,
                                                        gas=self.staking_gas)
                        dv_nodeid = self.nodeid_list2[i]
                        assert result.get('Status') == True
                        assert result.get('ErrMsg') == 'ok'
                    except:
                        log.info('质押失败')
                    break
        try:
            for version in version_list:
                if version == version_list[0]:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False
                elif version == version_list[1]:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == True
                elif version == version_list[2]:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False
                elif version == version_list[3]:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False
                else:
                    pass
        except:
                log.info('进行版本声明-test_declare_version_noproposal_Candidate-验证失败')

    @allure.title('13-存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_propsal_verifier(self):
        '''
        版本声明-存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link, flag=1)
        version2 = GovernUtil(rpc_link, flag=2)
        version3 = GovernUtil(rpc_link, flag=3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            try:
                opver=GovernUtil(rpc_link)
                opver.submitversion()
            except:
                log.info('提交升级提案失败')

        # 获取验证人id列表
        revice = rpc_link.getVerifierList()
        node_info = revice.get('Data')
        verifier_list = []

        dv_nodeid = False
        for nodeid in node_info:
            verifier_list.append(nodeid.get('NodeId'))

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
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False
                    elif version == version_list[1]:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == True
                    elif version == version_list[2]:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False
                    elif version == version_list[3]:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                      Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False
                    else:
                        pass
            except:
                log.info('进行版本声明-test_declare_version_propsal_verifier-验证失败')

    @allure.title('14-不存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_nopropsal_verifier(self):
        '''
        版本声明-不存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = GovernUtil(rpc_link)
        version1 = GovernUtil(rpc_link, flag=1)
        version2 = GovernUtil(rpc_link, flag=2)
        version3 = GovernUtil(rpc_link, flag=3)

        new_version0 = version0.get_version()
        new_version1 = version1.get_version()
        new_version2 = version2.get_version()
        new_version3 = version3.get_version()

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('存在有效的升级提案，该用例执行失败')
        else:
            revice = rpc_link.getVerifierList()
            node_info = revice.get('Data')
            verifier_list = []
            dv_nodeid = False

            for nodeid in node_info:
                verifier_list.append(nodeid.get('NodeId'))

            for i in range(0, len(verifier_list)):
                if verifier_list[i] not in self.nodeid_list:
                    dv_nodeid = verifier_list[i]
                    break

            # 判断是否存在验证
            if dv_nodeid:
                try:
                    for version in version_list:
                        if version == version_list[0]:
                            result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == False
                        elif version == version_list[1]:
                            result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == True
                        elif version == version_list[2]:
                            result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == False
                        elif version == version_list[3]:
                            result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                          Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == False
                        else:
                            pass
                except:
                    log.info('进行版本声明-test_declare_version_nopropsal_verifier-验证失败')
            else:
                log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')

    @allure.title('20-查询节点链生效的版本')
    def test_get_active_version(self):
        '''
        查询节点链生效的版本
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        log.info('查询节点链生效的版本-test_get_active_version-={}'.format(rpc_link.getActiveVersion()))

    @allure.title('21-查询提案列表')
    def test_get_proposal_list(self):
        '''
        查询提案列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        result = rpc_link.listProposal()

        log.info('查询提案列表-test_get_proposal_list-={}'.format(result))

    @allure.title('22-查询节点列表')
    def test_get_node_list(self):
        '''
        查询节点列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        gas2 = self.base_gas + 6000 + 32000 + 12000

        gas_price2 =self.base_gas_price

        result = rpc_link.getTallyResult('111', self.address_list[1], gas_price2, gas2)

        log.info('查询节点列-test_get_node_list-={}'.format(result))


if  __name__ == '__main__':
    pytest.main(["-s", "test_govern.py"])
