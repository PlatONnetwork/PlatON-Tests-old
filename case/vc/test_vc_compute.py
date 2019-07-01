# -*- coding: utf-8 -*-
'''
@Author: wuyiqin
@Date: 2019-01-08 10:20:33
@LastEditors: wuyiqin
@LastEditTime: 2019-03-20 14:24:09
@Description: file content
'''
import time

import requests

from common import log
from common.abspath import abspath
from common.connect import connect_linux, connect_web3, run_ssh
from common.load_file import get_node_list
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton
from utils.platon_lib.contract import (PlatonContractTransaction,
                                       get_abi_bytes,
                                       get_byte_code)

class TestVC:
    node_yml = abspath("deploy/node/vc_node.yml")
    auto = AutoDeployPlaton()

    def setup_class(self):
        self.auto.start_all_node(self.node_yml, genesis_file=conf.GENESIS_TMP, static_node_file=conf.STATIC_NODE_FILE)
        # 等一下，同步块高
        collusion, _ = get_node_list(conf.NODE_YML)
        collusion_w3 = connect_web3(collusion[0]["url"])
        collusion_block = collusion_w3.eth.blockNumber
        _, nocollusion = get_node_list(self.node_yml)
        self.url = nocollusion[0]['url']
        self.ip = nocollusion[0]["host"]
        self.wt = PlatonContractTransaction(self.url)
        self.password = conf.PASSWORD
        nocollusion_block = self.wt.eth.blockNumber
        if collusion_block - nocollusion_block >= 100:
            time.sleep(20)
        elif 100 > collusion_block - nocollusion_block >= 50:
            time.sleep(10)
        else:
            time.sleep(5)
        addrress = self.wt.w3.toChecksumAddress(conf.ADDRESS)
        self.wt.w3.personal.unlockAccount(addrress, self.password, 999999)
        """部署合约"""
        resp = self.wt.contract_deploy(get_byte_code(
            abspath('./data/contract/vccMain.wasm')),
            get_abi_bytes(abspath(r'./data/contract/vccMain.cpp.abi.json')),
            addrress)
        result = self.wt.eth.waitForTransactionReceipt(resp)
        self.contract_address = result['contractAddress']
        log.info(self.contract_address)
        if len(self.wt.eth.getCode(self.contract_address)) < 10:
            raise Exception("合约部署失败")
        node = nocollusion[0]
        ssh, sftp, t = connect_linux(node['host'], username=node['username'], password=node['password'])
        pwd_list = run_ssh(ssh, "pwd")
        pwd = pwd_list[0].strip("\r\n")
        account = 'UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821'
        self.wallet_path = '{}/{}/data16789/keystore/{}'.format(pwd, conf.DEPLOY_PATH, account)
        cmd = '''nohup java -jar ./vc_tool/vctool-1.0.jar  > ./vc_tool/nohup.out 2>&1 &'''
        run_ssh(ssh, cmd)
        self.get_url = 'http://{}:8112/test/getResult'.format(self.ip)

    def tearDown(self):
        self.auto.kill_of_yaml(self.node_yml)

    def get_transaction_hash(self, value, gas, gasPrice):
        '''
        :return:交易hash
        '''
        url = 'http://{}:8112/test/startVC'.format(self.ip)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'input': '20#30',
            'value': value,
            'gas': gas,
            'gasPrice': gasPrice
        }

        ret = requests.post(url=url, data=data)
        hash = ret.text
        assert hash is not None, '哈希预期返回成功{}，实际失败'.format(hash)
        return hash

    def get_vc_taskid(self, value=4300000, gas=4300000, gasPrice=22000000000):
        '''
        :return:taskid vc任务号
        '''
        hash = self.get_transaction_hash(value, gas, gasPrice)
        url = 'http://{}:8112/test/getTaskIdForHash'.format(self.ip)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'hash': hash}
        ret = requests.post(url=url, data=data)
        taskid = ret.text
        assert taskid is not None, 'taskid预期返回成功{}，实际失败'.format(taskid)
        return taskid

    def test_vc_result_add(self):
        '''
        获取VC合约add的值
        :return:
        '''
        taskid = self.get_vc_taskid()
        time.sleep(30)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'taskId': taskid}
        ret = requests.post(url=self.get_url, data=data)
        result = int(ret.text)
        assert result == 50, '预期结果为50，实际结果为{}'.format(result)
        assert ret.status_code == 200, '预期返回响应码为200，实际为{}'.format(str(ret.status_code))

    def test_value_outsize(self):
        '''
        value过大
        :return:
        '''
        taskid = self.get_vc_taskid(value=100000000000000000000000000)
        time.sleep(30)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'taskId': taskid}
        ret = requests.post(url=self.get_url, data=data)
        result = int(ret.text)
        assert result == 0, '预期结果为0，实际结果为{}'.format(result)

    def test_value_insuff(self):
        '''
        value为0
        :return:
        '''
        taskid = self.get_vc_taskid(value=0)
        time.sleep(30)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'taskId': taskid}
        ret = requests.post(url=self.get_url, data=data)
        result = int(ret.text)
        assert result == 50, '预期结果为50，实际结果为{}'.format(result)

    def test_gas_outsize(self):
        '''
        gas值超过范围内
        :return:
        '''
        taskid = self.get_vc_taskid(gas=1000000000000000000)
        time.sleep(30)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'taskId': taskid}

        status = 0
        try:
            ret = requests.post(url=self.get_url, data=data)
            assert ret.status_code != 200, '预期返回响应失败，实际为{}'.format(str(ret.status_code))
        except:
            status = 1
        assert status == 1, '预期gas过大，返回异常，实际返回成功'

    def test_gas_insuff(self):
        '''
        gas值过小
        :return:
        '''
        taskid = self.get_vc_taskid(gas=10)
        time.sleep(30)
        data = {
            'walletPath': self.wallet_path,
            'walletPass': self.password,
            'contractAddress': self.contract_address,
            'taskId': taskid}

        status = 0
        try:
            ret = requests.post(url=self.get_url, data=data)
            assert ret.status_code != 200, '预期返回响应失败，实际为{}'.format(str(ret.status_code))
        except:
            status = 1
        assert status == 1, '预期gas过小，返回异常，实际返回成功'
