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
from conf import setting as conf
from utils.platon_lib.ppos import Ppos
from utils.platon_lib.govern_util import *

from common.load_file import get_node_info
from common.connect import connect_web3
from deploy.deploy import AutoDeployPlaton
from hexbytes import HexBytes
from client_sdk_python.personal import (
    Personal,
)

class TestGovern:
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.GOVERN_NODE_YML

    log.info(node_yml_path)

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
    address_list = ["0x2b9CA6c401e96A7Ca3ce5e2E5f02a665E4f1631B", "0xdd3aA6f0B04A01a418b07F3dE41D4307A03E1016",
                    "0xb2fC346DF94cBE871AF2ea56B9E56E477569FcDb"]

    # 没有绑定节点的钱包私钥
    private_key_list = ["5cd4c60a74e69d35ed766bae72e32ded93cbd10eb545a558120d82f29f205823",
                       "e11e8dd946380db75036e4ac341d4eb24cfac01d637f01088658b9838639b8f6",
                       "0aea84e2169919c796b4983b130bf31ac152f78319f91f56563bd75cf842314c"]

    # 一个共识周期数包含的区块数
    block_count=50

    # 截止块高在某个共识周期的第(block_count-block_interval)个块高
    block_interval=10

    # 提案截止块高中，设置截止块高在第几个共识周期中
    conse_index=1

    # 提案截止块高中，设置截止块高在最大的共识周期中
    conse_border=3

    # 时间间隔-秒
    time_interval = 2

    # 随机字符个数
    length=6

    # 节点的第三方主页
    website = 'https://www.platon.network/#/'

    # 节点的描述
    details = '发起升级提案'

    # 提案在github上的id
    github_id = '101'

    # 基本的gas
    base_gas = 21000

    # 基本的gasprice
    base_gas_price=60000000000000

    # 每次转账的金额
    trans_amount=100000000000000000000000000

    # 进行质押的gas
    staking_gas = base_gas + 32000 + 6000 + 100000

    # 撤销质押的gas
    unstaking_gas = base_gas + 20000 + 6000 + 100000

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
        log.info('setup_class-开始')

        log.info('开始重新部署链')
        self.auto = AutoDeployPlaton()
        self.auto.start_all_node(self.node_yml_path)
        log.info('结束重新部署链')

        # 默认初始化后，给所有钱包进行转账处理
        self.w3_list = [connect_web3(url) for url in self.rpc_list]

        self.link_1 = Ppos(self.rpc_list[0], self.address)
        self.link_2 = Ppos(self.rpc_list[1], self.address)

        # 新钱包地址和私钥
        self.no_link_1 = Ppos(self.rpc_list[2], self.address_list[0], privatekey= self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[2], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[2], self.address_list[2], privatekey=self.private_key_list[2])

        log.info('获取随机生成字符的对象 随机设置主题和说明')
        # 获取随机生成字符的对象 随机设置主题和说明
        self.rand_str = gen_random_string(self.length)
        self.external_id='id_'.join(self.rand_str)
        self.node_name='name_'.join(self.rand_str)
        self.topic = 'topic_'.join(self.rand_str)
        self.desc = 'desc_'.join(self.rand_str)

        log.info('setup_class-结束')

    # 重新部署链
    def re_deploy(self):
        log.info('re_deploy-开始')

        log.info('开始重新部署链')
        self.auto = AutoDeployPlaton()
        self.auto.start_all_node(self.node_yml_path)
        log.info('结束重新部署链')

        # 默认初始化后，给所有钱包进行转账处理
        self.w3_list = [connect_web3(url) for url in self.rpc_list]

        self.link_1 = Ppos(self.rpc_list[0], self.address)
        self.link_2 = Ppos(self.rpc_list[1], self.address)

        # 新钱包地址和私钥
        self.no_link_1 = Ppos(self.rpc_list[2], self.address_list[0], privatekey=self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[2], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[2], self.address_list[2], privatekey=self.private_key_list[2])

        log.info('获取随机生成字符的对象 随机设置主题和说明')
        # 获取随机生成字符的对象 随机设置主题和说明
        self.rand_str = gen_random_string(self.length)
        self.external_id = 'id_'.join(self.rand_str)
        self.node_name = 'name_'.join(self.rand_str)
        self.topic = 'topic_'.join(self.rand_str)
        self.desc = 'desc_'.join(self.rand_str)

        log.info('re_deploy-结束')

    # 默认初始化后，给所有钱包进行转账处理
    def transaction(self, w3, from_address, to_address=None):
        """"
        转账公共方法
        """
        personal = Personal(w3)
        personal.unlockAccount(from_address, self.pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': self.base_gas,
            'gasPrice': self.base_gas_price,
            'value': self.trans_amount
        }
        tx_hash = w3.eth.sendTransaction(params)
        result = w3.eth.waitForTransactionReceipt(HexBytes(tx_hash).hex())
        return result

    def submit_version(self,flag=None):
        '''
        提交升级提案
        :param new_version,flag=0、1、2、3 获取特定截止和生效块高
        :return: list
        '''
        rpc_link=self.link_1

        while 1:
            # 获取验证人节点ID列表
            nodeid_list=get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id=nodeid_list[0]
        address=get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id,address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        new_version = get_version(rpc_link, 3)
        log.info('升级提案版本号={}'.format(new_version))

        if not flag:
            end_number,effect_number=get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)
        elif flag==0:
            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_number_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                                   self.block_interval,
                                                                                   self.conse_index, self.conse_border)
            end_number,effect_number = block_number_list[flag][0],block_number_list[flag][1]
        elif flag==1:
            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_number_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                                   self.block_interval,
                                                                                   self.conse_index, self.conse_border)
            end_number,effect_number = block_number_list[flag][0],block_number_list[flag][1]
        elif flag==2:
            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_number_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                                   self.block_interval,
                                                                                   self.conse_index, self.conse_border)
            end_number,effect_number = block_number_list[flag][0],block_number_list[flag][1]
        elif flag==3:
            # 获取指定结算算周期的截止区块、生效区块块高
            block_number_list = get_cross_sellte_cycle_legal_end_and_effect_block_number(rpc_link, self.block_count,
                                                                                         self.block_interval,
                                                                                         self.conse_border)

            end_number = block_number_list[0][0]
            effect_number = block_number_list[0][1]
        else:
            pass

        log.info('升级提案的截止块高={},生效块高={}'.format(end_number, effect_number))

        # 发起升级提案
        result = rpc_link.submitVersion(node_id, self.website, new_version, end_number, effect_number,from_address=address, privatekey=private_key)
        log.info('升级提案后的结果为={}'.format(result))
        return result

    @allure.title('1-发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证')
    def test_submit_version_version_not_empty(self):
        '''
        用例id 9,12,19~22
        发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证
        '''

        # 链上是否有未生效的升级提案，为True则有
        flag=is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link=self.link_1

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('node_id={},address={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 获取单个合理的截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number=get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 版本号
        cur_version= get_version(rpc_link)
        new_version1 = get_version(rpc_link,flag=1)
        new_version2 = get_version(rpc_link,flag=2)

        log.info('当前版本号={}'.format(cur_version))

        # 版本号参数列表
        version_list = [new_version1,new_version2]

        log.info('没有有效的升级提案，可以发起升级提案')
        log.info('1-test_submit_version_version_not_empty-内置验证人节点发起升级提案')
        for new_version in version_list:
            if new_version == version_list[0]:
                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                log.info('提案结果={}'.format(result))

                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('should larger than current version', 0, len(
                    info)) > 0, '提交升级提案参数中升级目的版本号不正确（升级目的版本号<=链上当前版本号），发起升级提案失败'
            elif new_version == version_list[1]:
                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                log.info('提案结果={}'.format(result))

                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('should larger than current version', 0, len(
                    info)) > 0, '提交升级提案参数中升级目的版本号不正确（升级目标版本的大版本号等于链上当前版本号，升级目的版本号为小版本号大于链上链上当前小版本号），发起升级提案失败'
            else:
                pass
        log.info('1-test_submit_version_version_not_empty-发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证-结束')

    @allure.title('2-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性')
    def test_submit_version_end_block_number(self):
        '''
        用例id 10,24~28,32~34
        发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('node_id={},address={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 获取各类不合理的截止块高 在第几个共识周期 共识周期最大边界
        block_number_list = get_all_invalid_end_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index,self.conse_border)

        # 升级版本号
        new_version = get_version(rpc_link, flag=3)
        log.info('升级提案版本号={}'.format(new_version))

        log.info('2-test_submit_version_end_block_number-内置验证人节点发起升级提案')
        for count in range(len(block_number_list)):
            if count == 0:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不能等于当前块高，发起升级提案失败'
            elif count == 1:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
            elif count == 2:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
            elif count == 3:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info=result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info))>0, '截止区块块高不正确，为N+1周期的第230块块高，发起升级提案失败'
            else:
                pass
        log.info('2-test_submit_version_end_block_number-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性-结束')

    @allure.title('3-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性')
    def test_submit_version_effect_block_number(self):
        '''
        用例id 11,38~43
        发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('node_id={},address={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 获取各类不合理的生效块高 在第几个共识周期 共识周期最大边界
        block_number_list = get_all_invalid_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)

        # 升级版本号
        new_version = get_version(rpc_link, flag=3)
        log.info('升级提案版本号={}'.format(new_version))

        log.info('3-test_submit_version_effect_block_number-内置验证人节点发起升级提案')
        for count in range(len(block_number_list)):
            if count == 0:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，生效块高设置为=当前块高，发起升级提案失败'
            elif count == 1:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，生效块高设置为=截止块高，发起升级提案失败'
            elif count == 2:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 4)个共识周期的第230块块高，发起升级提案失败'
            elif count == 3:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第229块块高，发起升级提案失败'
            elif count == 4:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第231块块高，发起升级提案失败'
            elif count == 5:
                end_number = block_number_list[count][0]
                effect_number = block_number_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，为第(N + 11)个共识周期的第250块块高，发起升级提案失败'
            else:
                pass
        log.info('3-test_submit_version_effect_block_number-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性-结束')

    @allure.title('4-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案')
    def test_submit_version_on_newnode(self):
        '''
        用例id 14
        发起升级提案-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        # 升级版本号
        new_version = get_version(self.link_1,3)
        log.info('当前生成的提案升级版本号={}'.format(new_version))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

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
                    log.info('test_submit_version_on_newnode-新节点发起升级提案')
                    result = rpc_link.submitVersion(verifier=self.nodeid_list2[i], url=self.website,newVersion=new_version,
                                                          endVotingBlock=end_number, activeBlock=effect_number)
                    log.info('新用户节点发起提案失败')
                    info = result.get('ErrMsg')
                    assert result.get('Status') == False
                    assert info.find('not a verifier', 0,
                                     len(info)) > 0, '发起升级提案失败-发起升级提案时，该节点是新人节点，而不是验证人节点'
                    break
        log.info('4-test_submit_version_on_newnode-发起升级提案-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案-结束')

    @allure.title('5-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案')
    def test_submit_version_on_candidatenode(self):
        '''
        用例id 13
        发起升级提案-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        # 当前版本号
        cur_version = get_version(rpc_link)
        log.info('当前版本号={}'.format(cur_version))

        # 升级版本号
        new_version = get_version(rpc_link,3)
        log.info('当前生成的提案升级版本号={}'.format(new_version))

        log.info('没有有效的升级提案，可以发起升级提案')
        not_verify_list = get_current_settle_account_candidate_list(rpc_link)

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
        if not_verify_list:
            node_id = not_verify_list[0]
            log.info('存在候选人节点，取第一个候选人节点={}'.format(node_id))
        else:
            # 获取候选人节点id列表
            receive = rpc_link.getCandidateList()
            node_info = receive.get('Data')
            candidate_list = []

            rpc_link = self.no_link_1

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    self.transaction(self.w3_list[0], self.address, to_address=self.address_list[0])
                    result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i], externalId=self.external_id,nodeName=self.node_name,
                                                    website=self.website, details=self.details,amount=self.staking_amount,
                                                    programVersion=cur_version,  from_address=self.address_list[0],
                                                    gasPrice=self.base_gas_price,gas=self.staking_gas)
                    node_id = self.nodeid_list2[i]
                    log.info('不存在候选人节点，质押后的候选人节点={}'.format(node_id))
                    log.info('候选人节点质押成功')
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                break

        log.info('候选人节点质押完成')
        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                        endVotingBlock=end_number, activeBlock=effect_number)
        log.info('候选人节点发起提案失败')
        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('not a verifier', 0,
                         len(info)) > 0, '发起升级提案失败-发起升级提案时，该节点是候选人节点，而不是验证人节点'
        log.info('5-test_submit_version_on_candidatenode-发起升级提案-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案-结束')

    # @allure.title('6-发起升级提案-交易手续费的验证-提案人账号的手续费不足')
    # def test_submit_version_charge_not_enough(self):
    #     '''
    #     用例id 23
    #     发起升级提案-交易手续费的验证-提案人账号的手续费不足
    #     '''
    #     # 链上是否有未生效的升级提案，为True则有
    #     flag = is_exist_ineffective_proposal_info(self.link_1)
    #
    #     # 存在有效的升级提案，需要重新部署链
    #     if flag:
    #         log.info('存在有效的升级提案，需要重新部署链')
    #
    #         # 重新部署链
    #         log.info('重新部署链开始-re_deploy')
    #         self.re_deploy()
    #         log.info('重新部署链结束-re_deploy')
    #
    #         log.info('等待一段时间={}秒'.format(self.time_interval))
    #         time.sleep(self.time_interval)
    #
    #     log.info('没有有效的升级提案，可以发起升级提案')
    #     rpc_link = self.link_1
    #
    #     # 升级版本号
    #     new_version = get_version(rpc_link, 3)
    #
    #     # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
    #     end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,self.block_interval,
    #                                                                              self.conse_index)
    #     log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))
    #
    #     # 获取验证人id列表
    #     revice = rpc_link.getVerifierList()
    #     node_info = revice.get('Data')
    #     verifier_list = []
    #
    #     dv_nodeid = False
    #
    #     for nodeid in node_info:
    #         verifier_list.append(nodeid.get('NodeId'))
    #
    #     for i in range(0, len(verifier_list)):
    #         if verifier_list[i] not in self.nodeid_list:
    #             dv_nodeid = verifier_list[i]
    #             break
    #
    #     if dv_nodeid:
    #         result = rpc_link.submitVersion(verifier=dv_nodeid, url=self.website, newVersion=new_version,
    #                                         endVotingBlock=end_number, activeBlock=effect_number)
    #         log.info('result='.format(result))
    #         assert result.get('Status') == False
    #         # assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
    #         log.info('发起升级提案失败')
    #     else:
    #         log.info('发起升级提案-当前结算周期不存在可用验证人（创始验证人节点），该用例验证失败')
    #
    #     log.info('6-test_submit_version_charge_not_enough-发起升级提案-交易手续费的验证-提案人账号的手续费不足-结束')

    @allure.title('7-发起升级提案-升级提案成功的验证')
    def test_submit_version_success(self):
        '''
        用例id 15,18   正确的截止块高29~31,35~37,正确的生效块高44~46,47
        发起升级提案-升级提案成功的验证
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('node_id={},address={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 升级版本号
        new_version =get_version(rpc_link,3)

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.block_interval,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                        endVotingBlock=end_number, activeBlock=effect_number)
        log.info('result='.format(result))
        assert result.get('Status') == True, '发起升级提案成功'
        log.info('7-test_submit_version_success-发起升级提案-升级提案成功的验证-结束')

    @allure.title('8-发起升级提案-未生效的升级提案的验证')
    def test_submit_ineffective_verify(self):
        '''
        用例id 16,17
        发起升级提案-未生效的升级提案的验证
        '''
        rpc_link=self.link_1

        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(rpc_link)

        # 存在未生效的升级提案
        if flag:
            log.info('存在未生效的升级提案，发起升级提案失败')

            result = self.submit_version()

            log.info('升级提案后的结果='.format(result))
            info = result.get('ErrMsg')

            assert result.get('Status') == False
            assert info.find('existing a version proposal', 0,
                             len(info)) > 0, '有未生效的升级提案，发起升级提案失败'
        else:
            log.info('不存在有效的升级提案，需先发起一个升级提案，再继续升级提案')

            result = self.submit_version()
            log.info('升级提案后的结果='.format(result))

            assert result.get('Status') == True, '没有未生效的升级提案，发起升级提案成功'

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

            result = self.submit_version()
            log.info('升级提案后的结果='.format(result))
            info = result.get('ErrMsg')

            assert result.get('Status') == False
            assert info.find('existing a version proposal', 0,
                             len(info)) > 0, '有未生效的升级提案，发起升级提案失败'
        log.info('8-test_submit_ineffective_verify-发起升级提案-未生效的升级提案的验证-结束')

    @allure.title('9-对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）')
    def test_vote_vote_trans(self):
        '''
        用例id 48~50,60
        对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）
        '''
        rpc_link=self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案，然后再进行投票
        flag=is_exist_ineffective_proposal_info_for_vote(rpc_link)
        log.info('flag={}'.format(flag))

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        # 设置获取版本号的对象
        little_version = get_version(rpc_link, 1)
        cur_version = get_version(rpc_link)

        # 升级版本号
        new_version = get_version(rpc_link, flag=3)
        log.info('升级提案版本号={}'.format(new_version))

        log.info('当前生成的小版本号为：{}-当前版本号为：{}'.format(little_version, cur_version))
        version_list = [little_version, cur_version]

        # 投赞成票
        option=1

        # 投票
        for node_version in version_list:
            if node_version == little_version:
                result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('not upgraded to a new version', 0,
                                 len(info)) > 0, '发起升级投票交易时节点版本号不正确（小于提案升级版本号）'
            elif node_version == cur_version:
                result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('not upgraded to a new version', 0,
                                 len(info)) > 0, '发起升级投票交易时节点版本号不正确（等于链上当前版本号）'
            else:
                pass
        log.info('9-test_vote_vote_trans-对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）-结束')

    @allure.title('10-对升级提案进行投票-是否在投票周期内的验证 block_count * conse_index - 20')
    def test_vote_notin_vote_cycle_a(self):
        '''
        用例id 51,54
        对升级提案进行投票-是否在投票周期内的验证 block_count * conse_index - 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 block_count * conse_index - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1

        log.info('先发起一个升级提案成功后，再投票')

        # 发起升级提案
        self.submit_version(flag=0)

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        option = 1

        block_number = rpc_link.eth.blockNumber
        log.info('开始投票前,当前块高={}'.format(block_number))
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,
                               programVersion=new_version)
        assert result.get('Status') == False,'发起升级投票交易时，不在投票周期，投票不成功'

        block_number = rpc_link.eth.blockNumber
        log.info('完成投票后,当前块高={}'.format(block_number))
        log.info('10-test_vote_notin_vote_cycle_a-对升级提案进行投票-是否在投票周期内的验证 block_count * conse_border - 20-结束')

    @allure.title('11-对升级提案进行投票-是否在投票周期内的验证 block_count * (conse_border-1) - 20')
    def test_vote_notin_vote_cycle_b(self):
        '''
        用例id 52,55
        对升级提案进行投票-是否在投票周期内的验证 block_count * (conse_border-1) - 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 block_count * (conse_border-1)  - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1

        log.info('先发起一个升级提案成功后，再投票')

        # 发起升级提案
        self.submit_version(flag=1)

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        option = 1

        block_number = rpc_link.eth.blockNumber
        log.info('开始投票前,当前块高={}'.format(block_number))
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,
                               programVersion=new_version)
        assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'

        block_number = rpc_link.eth.blockNumber
        log.info('完成投票后,当前块高={}'.format(block_number))
        log.info('11-test_vote_notin_vote_cycle_b-对升级提案进行投票-是否在投票周期内的验证 block_count * (conse_border-1) - 20-结束')

    @allure.title('12-对升级提案进行投票-是否在投票周期内的验证 block_count * conse_border- 20')
    def test_vote_notin_vote_cycle_c(self):
        '''
        用例id 53,56
        对升级提案进行投票-是否在投票周期内的验证 block_count * conse_border- 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 block_count * (conse_border)  - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1

        log.info('先发起一个升级提案成功后，再投票')

        # 发起升级提案
        self.submit_version(flag=2)

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        option = 1

        block_number = rpc_link.eth.blockNumber
        log.info('开始投票前,当前块高={}'.format(block_number))
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,
                               programVersion=new_version)
        assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'

        block_number = rpc_link.eth.blockNumber
        log.info('完成投票后,当前块高={}'.format(block_number))
        log.info('12-test_vote_notin_vote_cycle_c-对升级提案进行投票-是否在投票周期内的验证 block_count * conse_border- 20-结束')

    @allure.title('13-对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）')
    def test_vote_new_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）
        '''
        rpc_link = self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        option = 1

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
                    log.info('test_vote_new_node_vote-新用户节点进行投票')

                    result = rpc_link.vote(verifier=self.nodeid_list2[i], proposalID=proposal_id, option=option,programVersion=new_version)

                    log.info('新用户节点进行投票，投票失败')
                    info = result.get('ErrMsg')
                    assert result.get('Status') == False
                    assert info.find('not a verifier', 0,
                                     len(info)) > 0, '发起升级投票交易时，该节点是新人节点，而不是验证人节点，投票失败'
                    break
        log.info('13-test_vote_new_node_vote-对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）-结束')

    @allure.title('14-对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）')
    def test_vote_candidate_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）
        '''
        rpc_link = self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        # 当前版本号
        cur_version = get_version(rpc_link)
        log.info('当前链上版本号={}'.format(cur_version))

        # 获取当前结算周期非验证人的候选人列表
        not_verify_list = get_current_settle_account_candidate_list(rpc_link)

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
        if not_verify_list:
            node_id = not_verify_list[0]
            log.info('存在候选人节点，取第一个候选人节点={}'.format(node_id))
        else:
            # 获取候选人节点id列表
            receive = rpc_link.getCandidateList()
            node_info = receive.get('Data')
            candidate_list = []

            rpc_link = self.no_link_2

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    self.transaction(self.w3_list[0], self.address, to_address=self.address_list[1])
                    result = rpc_link.createStaking(0, self.address_list[1], self.nodeid_list2[i],
                                                    externalId=self.external_id, nodeName=self.node_name,
                                                    website=self.website, details=self.details,
                                                    amount=self.staking_amount,
                                                    programVersion=cur_version, from_address=self.address_list[1],
                                                    gasPrice=self.base_gas_price, gas=self.staking_gas)
                    node_id = self.nodeid_list2[i]
                    log.info('不存在候选人节点，质押后的候选人节点={}'.format(node_id))
                    log.info('候选人节点质押成功')
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                break

        log.info('候选人节点质押完成')
        log.info('test_vote_candidate_node_vote-候选人节点进行投票')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        option=1

        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)

        log.info('候选人节点进行投票，投票失败')
        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('not a verifier', 0,
                         len(info)) > 0, '发起升级投票交易时，该节点是候选人节点，而不是验证人节点，投票失败'
        log.info('14-test_vote_candidate_node_vote-对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）-结束')

    @allure.title('15-对升级提案进行投票-升级投票通过（验证人节点发起升级投票）')
    def test_vote_vote_success(self):
        '''
        用例id 59,64
        对升级提案进行投票-升级投票通过（验证人节点发起升级投票）
        '''
        rpc_link = self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒后，进行首次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        option=1

        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)
        assert result.get('Status') == True, '对升级提案进行投票时，升级投票通过（验证人节点发起升级投票），投票成功'
        log.info('15-test_vote_vote_success-对升级提案进行投票-升级投票通过（验证人节点发起升级投票）-结束')

    @allure.title('16-对升级提案进行投票-是否已经投票过的验证')
    def test_vote_vote_double_cycle(self):
        '''
        用例id 59
        对升级提案进行投票-是否已经投票过的验证
        '''
        rpc_link = self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒后，进行首次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))
        option=1

        log.info('开始首次投票')
        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)
        log.info('结束首次投票')

        assert result.get('Status') == True, '对升级提案进行投票时，升级投票通过（验证人节点发起升级投票），投票成功'

        # 在等待一定时间后，再次进行投票
        log.info('等待一段时间={}秒后，再次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        log.info('开始第2次投票')
        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        log.info('结束第2次投票')

        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('node has voted this proposal', 0,
                         len(info)) > 0, '对升级提案进行投票时，是否已经投票过的验证，已经进行投票后，不能再次重复投票，投票失败'
        log.info('16-test_vote_vote_double_cycle-对升级提案进行投票-是否已经投票过的验证，已经进行投票后，不能再次重复投票-结束')

    @allure.title('17-对升级提案进行投票-候选人在投票周期成为验证人后发起投票')
    def test_vote_candidate_to_verifier(self):
        '''
        用例id 57
        对升级提案进行投票-候选人在投票周期成为验证人后发起投票
        '''
        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1

        log.info('先发起一个升级提案成功后，再投票')
        # 发起升级提案
        self.submit_version(flag=3)

        # 版本号
        cur_version = get_version(rpc_link)
        log.info('当前版本号={}'.format(cur_version))

        # 获取当前结算周期非验证人的候选人列表
        not_verify_list = get_current_settle_account_candidate_list(rpc_link)

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
        if not_verify_list:
            node_id = not_verify_list[0]
            log.info('存在候选人节点，取第一个候选人节点={}'.format(node_id))
        else:
            log.info('不存在候选人节点，需要获取验证人去投票')
            # 获取候选人节点id列表
            receive = rpc_link.getCandidateList()
            node_info = receive.get('Data')
            candidate_list = []

            rpc_link = self.no_link_3

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    self.transaction(self.w3_list[0], self.address, to_address=self.address_list[2])
                    result = rpc_link.createStaking(0, self.address_list[2], self.nodeid_list2[i],
                                                    externalId=self.external_id, nodeName=self.node_name,
                                                    website=self.website, details=self.details,
                                                    amount=self.staking_amount,
                                                    programVersion=cur_version, from_address=self.address_list[2],
                                                    gasPrice=self.base_gas_price, gas=self.staking_gas)
                    node_id = self.nodeid_list2[i]
                    log.info('不存在候选人节点，质押后的候选人节点={}'.format(node_id))
                    log.info('候选人节点质押成功')
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                break

        log.info('候选人节点质押完成')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))
        border_number=end_block_number-self.block_count

        # 等待下一个结算周期后,再进行投票
        is_cur_block_number_big_than_end_block_number(rpc_link,border_number)
        option=1

        log.info('开始投票')
        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        log.info('结束投票')

        assert result.get('Status') == True, '对升级提案进行投票-候选人在投票周期成内为验证人后发起投票，投票成功'
        log.info('17-test_vote_candidate_to_verifier-对升级提案进行投票-候选人在投票周期内成为验证人后发起投票-结束')

    @allure.title('18-对升级提案进行投票-节点是否处于退出状态的验证-发起升级投票申请前已经退出节点')
    def test_vote_verifier_withdraw(self):
        '''
        用例id 57
        对升级提案进行投票-节点是否处于退出状态的验证-发起升级投票申请前已经退出节点
        '''
        rpc_link = self.link_1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 发起升级提案
            self.submit_version()

        log.info('有可投票的升级提案，直接进行投票')

        log.info('先获取一个验证人,然后进行撤销质押操作,之后再进行投票')
        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        node_id = nodeid_list[0]
        log.info('获取到了验证人节点ID={}'.format(node_id))

        address = get_stakingaddree(rpc_link, nodeid_list[0])
        log.info('节点ID={},钱包地址={}'.format(node_id, address))

        # 获取验证人的质押钱包地址和私钥
        check_address = Web3.toChecksumAddress(address)
        private_key = get_privatekey(check_address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], check_address, chainid=101, privatekey=private_key)

        log.info('撤销质押开始')
        # 验证人撤销质押
        rpc_link.unStaking(node_id,privatekey=private_key,from_address=address,gasPrice=self.base_gas_price,gas=self.unstaking_gas)
        log.info('撤销质押结束')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={},升级版本号={},截止块高={}'.format(proposal_id, new_version, end_block_number))

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒后，进行进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)
        option=1

        log.info('开始投票')
        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        log.info('结束投票')

        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('verifier\'s status is invalid', 0,len(info)) > 0, '对升级提案进行投票-节点是否处于退出状态的验证-发起升级投票申请前已经退出节点，不能进行投票，投票失败'
        log.info('18-test_vote_verifier_withdraw-对升级提案进行投票-节点是否处于退出状态的验证-发起升级投票申请前已经退出节点-结束')

    @allure.title('19-实施升级-发起提案及投票成功后,到达生效块高,且验证人符合要求,则开始升级')
    def test_implementing_upgrade_a(self):
        '''
        用例id
        发起升级提案-升级提案成功的验证
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        log.info('进入发起升级提案的处理过程')
        self.submit_version()

        rpc_link = self.link_1
        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        log.info('进入投票处理过程')

        while 1:
            # 获取验证人节点ID列表
            nodeid_list = get_current_verifier(rpc_link)
            if nodeid_list:
                break

        option = 1

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)
        log.info('提案ID={}，升级版本号={}，截止块高={}'.format(proposal_id, new_version, end_block_number))

        ver_len=len(nodeid_list)

        for index in range(ver_len):
            node_id=self.nodeid_list[index]
            log.info('第{}个节点={}'.format(index+1,node_id))

            log.info('等待一段时间={}秒,再投票'.format(self.time_interval))
            time.sleep(self.time_interval)

            # 进行投票操作
            result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
            # assert result.get('Status') == True, '对升级提案进行投票时，升级投票通过（验证人节点发起升级投票），投票成功'

            block_number = rpc_link.eth.blockNumber
            log.info('每次完成投票后,当前块高={}'.format(block_number))

            if (index+1) / ver_len> 0.6:
                break

        block_number=rpc_link.eth.blockNumber
        log.info('完成所有投票后,当前块高={}'.format(block_number))

        log.info('19-test_implementing_upgrade_a-实施升级-发起提案及投票成功后,到达生效块高,且验证人符合要求,则开始升级-结束')


    @allure.title('16-非质押钱包进行版本声明')
    def test_declare_version_nostaking_address(self):
        '''
        版本声明-非质押钱包进行版本声明
        '''
        rpc_link = self.no_link_2

        # 版本号
        cur_version = get_version(rpc_link)
        log.info('当前版本号为：{}'.format(cur_version))

        result = rpc_link.declareVersion(self.nodeid_list[0], cur_version, self.address_list[1])
        assert result.get('Status') == False
        assert result.get('ErrMsg') == "Declare version error:tx sender should be node's staking address."

    @allure.title('17-无有效的升级提案，新节点进行版本声明')
    def test_declare_version_noproposal_newnode(self):
        '''
        版本声明-不存在有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,
                                                                        version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('当前链上存在生效的升级提案，该用例执行失败,请重新配置数据')
        else:
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            # 判断配置文件中的节点是否都已质押
            if set(self.nodeid_list2) < set(candidate_list):
                log.info('节点配置文件中的地址已全部质押，该用例执行失败，请重新配置数据')
            else:
                for i in range(0, len(self.nodeid_list2)):
                    if self.nodeid_list2[i] not in candidate_list:

                        for version in version_list:
                            result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                             Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == False
                        break

    @allure.title('18-不存在有效的升级提案，候选节点进行版本声明')
    def test_declare_version_noproposal_Candidate(self):
        '''
        版本声明-不存在有效的升级提案，候选节点进行版本声明
        '''

        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,
                                                                        version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('当前链上存在生效的升级提案，该用例执行失败,请重新配置数据')
        else:
            n_list = get_current_settle_account_candidate_list(rpc_link)

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
                        result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i],
                                                        externalId=self.rand_str,
                                                        nodeName=self.rand_str,
                                                        website=self.website, details=self.details,
                                                        amount=self.staking_amount,
                                                        programVersion=version0, gasPrice=self.base_gas_price,
                                                        gas=self.staking_gas)
                        dv_nodeid = self.nodeid_list2[i]
                        assert result.get('Status') == True
                        assert result.get('ErrMsg') == 'ok'
                        break

            for version in version_list:
                if version == version_list[0] or version == version_list[2]:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == True
                else:
                    result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False

    @allure.title('19-不存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_nopropsal_verifier_1(self):
        '''
        版本声明-不存在有效的升级提案，验证人(非创始验证人)进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,
                                                                        version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('存在有效的升级提案，该用例执行失败，请重新配置数据')
        else:

            verifier_list = get_current_verifier(rpc_link)
            dv_nodeid = False

            for i in range(0, len(verifier_list)):
                if verifier_list[i] not in self.nodeid_list:
                    dv_nodeid = verifier_list[i]
                    break

            # 判断是否存在验证
            if dv_nodeid:
                staking_address = get_stakingaddree(rpc_link, verifier_list[0])
                privatekey = Web3.toChecksumAddress(get_privatekey(staking_address))
                rpc_link = Ppos(self.rpc_list[2], staking_address, chainid=101, privatekey=privatekey)
                for version in version_list:
                    if version == version_list[0] or version == version_list[1]:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == True
                    else:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False

            else:
                log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')

    @allure.title('20-不存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_nopropsal_verifier_2(self):
        '''
        版本声明-不存在有效的升级提案，创始验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address, chainid=101, privatekey=self.private_key)

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('存在有效的升级提案，该用例执行失败，请重新配置数据')
        else:

            verifier_list = get_current_verifier(rpc_link)
            dv_nodeid = False

            for i in range(0, len(verifier_list)):
                if verifier_list[i] in self.nodeid_list:
                    dv_nodeid = verifier_list[i]
                    break

            # 判断是否存在验证
            if dv_nodeid:
                for version in version_list:
                    if version == version_list[0] or version == version_list[2]:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                         Web3.toChecksumAddress(self.address))
                        assert result.get('Status') == True
                    else:
                        result = rpc_link.declareVersion(dv_nodeid, version,
                                                         Web3.toChecksumAddress(self.address))
                        assert result.get('Status') == False

            else:
                log.info('当前结算周期不存在可用验证人（创始验证人节点），该用例验证失败')

    @allure.title('21-存在有效的升级提案，新节点进行版本声明')
    def test_declare_version_hasproposal_newnode(self):
        '''
        版本声明-存在有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,
                                                                        version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list == 'null':
            log.info('当前链上不存在生效的升级提案，进行发布升级提案')
            self.submit_version()

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
                    for version in version_list:
                        result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False

                    break

    @allure.title('22-存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_propsal_verifier(self):
        '''
        版本声明-存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        version0 = get_version(rpc_link)
        version1 = get_version(rpc_link, flag=1)
        version2 = get_version(rpc_link, flag=2)
        version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(version0, version1, version2,
                                                                        version3))

        # 版本号参数列表
        version_list = [version0, version1, version2, version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list == 'null':
            self.submit_version()

        # 获取验证人id列表
        verifier_list = get_current_verifier(rpc_link)

        for i in range(0, len(verifier_list)):
            if verifier_list[i] not in self.nodeid_list:
                dv_nodeid = verifier_list[i]
                break

        if not dv_nodeid:
            log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败,请重新配置数据')
        else:
            for version in version_list:
                if version == version_list[1]:
                    result = rpc_link.declareVersion(dv_nodeid, version,
                                                     Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False
                else:
                    result = rpc_link.declareVersion(dv_nodeid, version,
                                                     Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == True

    @allure.title('23-投票统计验证')
    def test_voting_statistics(self):
        '''
        投票统计
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address, chainid=101, privatekey=self.private_key)
        if not is_exist_ineffective_proposal_info(rpc_link):
            self.submit_version()

        proposalid = get_effect_proposal_id(rpc_link)
        endvotingblock = get_proposal_vote_end_block_number(rpc_link)
        waite_to_settle_account_cycle_block_number(rpc_link, block_count=250, end_block=endvotingblock)
        num = get_rate_of_voting(rpc_link, proposalid)
        time.sleep(10)
        # 判断投票率是否大于85%
        if num <= 0.85:
            result = rpc_link.getTallyResult(proposalid)
            resultinfo = result.get('Data')
            assert resultinfo
            status = resultinfo.get('status')
            assert status == 3
        else:
            result = rpc_link.getTallyResult(proposalid)
            resultinfo = result.get('Data')
            assert resultinfo
            status = resultinfo.get('status')
            assert status == 4

    @allure.title('24-查询提案结果接口功能验证-accuVerifiers正确性验证')
    def test_accuVerifiers_count(self, consize=250, num=86):
        '''
        验证getTallyResult接口查询的数据accuVerifiers正确性
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address, chainid=101, privatekey=self.private_key)
        if not is_exist_ineffective_proposal_info(rpc_link):
            self.submit_version()
            proposalid = get_effect_proposal_id(rpc_link)
            endvotingblock = get_proposal_vote_end_block_number(rpc_link)
            block_number = rpc_link.eth.blockNumber
            verifier_list = []
            verifier_list.append(get_current_verifier(rpc_link))

            assert get_accuVerifiers_of_proposal(rpc_link, proposalid) == len(verifier_list)
            while block_number < endvotingblock:
                waite_to_settle_account_cycle_block_number(rpc_link, block_count=consize,
                                                           end_block=block_number + consize * num)
                print(block_number)
                verifier_list.append(get_current_verifier(rpc_link))
                # 发起升级提案所在结算周期的验证人列表以及验证人数
                ver_list = verifier_list[0]
                verifier_count = len(verifier_list[0])

                for i in range(1, len(verifier_list)):
                    ver_list = list(set(ver_list).intersection(set(verifier_list[i])))
                    verifier_count = verifier_count + len(verifier_list[i])

                assert get_accuVerifiers_of_proposal(rpc_link, proposalid) == len(ver_list) + verifier_count

        else:
            log.info('当前链上存在有效的升级提案，请重新构造数据测试')

    @allure.title('25-查询提案结果接口功能验证-yeas正确性验证')
    def test_yeast_count(self):
        '''
        验证getTallyResult接口查询的数据yeas正确性
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address, chainid=101, privatekey=self.private_key)
        if not is_exist_ineffective_proposal_info(rpc_link):
            self.submit_version()

        option = 1
        proposalid, version = get_effect_proposal_id_and_version(rpc_link)
        verifier_list = get_current_verifier(rpc_link)
        address = get_stakingaddree(rpc_link, verifier_list[0])
        privatekey = get_privatekey(address)

        yeas = get_yeas_of_proposal(rpc_link, proposalid)
        # 进行提案投票操作

        result = rpc_link.vote(verifier_list[0], proposalid, option, version, from_address=address,
                               privatekey=privatekey)
        assert result.get('Data') == True
        assert get_yeas_of_proposal(rpc_link, proposalid) == yeas + 1

    @allure.title('26-查询提案结果接口功能验证-yeas正确性验证--验证人退出')
    def test_yeast_count(self):
        '''
        验证getTallyResult接口查询的数据yeas正确性-退出验证人，投票仍统计
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address, chainid=101, privatekey=self.private_key)
        if not is_exist_ineffective_proposal_info(rpc_link):
            self.submit_version()

        option = 1
        proposalid, version = get_effect_proposal_id_and_version(rpc_link)
        verifier_list = get_current_verifier(rpc_link)
        address = get_stakingaddree(rpc_link, verifier_list[0])
        privatekey = get_privatekey(address)

        yeas = get_yeas_of_proposal(rpc_link, proposalid)
        # 进行提案投票操作
        result = rpc_link.vote(verifier_list[0], proposalid, option, version, from_address=address,
                               privatekey=privatekey)
        assert result.get('Data') == True
        assert get_yeas_of_proposal(rpc_link, proposalid) == yeas + 1
        # 验证人退质押
        result = rpc_link.unStaking(verifier_list[0], from_address=address, privatekey=privatekey)

        assert result.get('Data') == True
        assert get_yeas_of_proposal(rpc_link, proposalid) == yeas + 1

    @allure.title('27-查询节点链生效的版本')
    def test_get_active_version(self):
        '''
        查询节点链生效的版本
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        log.info('查询节点链生效的版本-test_get_active_version-={}'.format(rpc_link.getActiveVersion()))

    @allure.title('28-查询提案列表')
    def test_get_proposal_list(self):
        '''
        查询提案列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        result = rpc_link.listProposal()
        assert result.get('Data') == True

    @allure.title('29-验证查询提案接口')
    def test_getProposal(self):
        '''
        验证查询提案接口
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[0], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        proposalid = get_effect_proposal_id(rpc_link)
        if not proposalid:
            log.info('链上不存在升级提案')
        else:
            result = rpc_link.getProposal(proposalid)
            assert result.get('Status') == True

    @allure.title('30-验证查询提案结果接口')
    def test_get_tallyresult(self):
        '''
        验证查询提案结果接口
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[0], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        proposalid = get_effect_proposal_id(rpc_link)
        if not proposalid:
            log.info('链上不存在升级提案')
        else:
            result = rpc_link.getTallyResult(proposalid)
            assert result.get('Status') == True

    def test(self):
        rpc_link = Ppos(self.rpc_list[0], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        flag = get_effect_proposal_id(rpc_link)
        print(flag)

    def test(self):
        rpc_link = Ppos(self.rpc_list[0], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        result = rpc_link.getProgramVersion()
        print(result)


if  __name__ == '__main__':
    pytest.main(["-s", "test_govern.py"])
