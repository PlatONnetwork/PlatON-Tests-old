# -*- coding: utf-8 -*-
'''
@Author: wuyiqin
@Date: 2019-01-08 10:20:33
@LastEditors: wuyiqin
@LastEditTime: 2019-03-20 14:24:09
@Description: file content
'''
import os
import queue
import time
from threading import Thread

import requests
from web3.admin import Admin

from deploy.deploy import AutoDeployPlaton
from common.connect import connect_linux, connect_web3,run_ssh
from common.load_file import LoadFile
from utils.platon_lib.contract import (PlatonContractTransaction,
                                       get_abi_bytes,
                                       get_byte_code)

q = queue.Queue()


def stop_java(ssh):
    _, alice_out, _ = ssh.exec_command("ps -ef|grep java")
    out_list = alice_out.readlines()
    if out_list:
        for p in out_list:
            if "java" in p:
                p_id = [i for i in p.split(" ") if i][1]
                ssh.exec_command('kill -9 {}'.format(p_id))
                time.sleep(0.5)


def deploy_contract():
    url = LoadFile('./conf/node.yml').get_data()['node1']["url"]
    wt = PlatonContractTransaction(url)
    addrress = wt.w3.toChecksumAddress(
        '0x493301712671ada506ba6ca7891f436d29185821')
    wt.w3.personal.unlockAccount(addrress, '88888888', 99999999)
    """部署合约"""
    resp = wt.contract_deploy(get_byte_code(
        r'./data/contract/mpc.wasm'),
        get_abi_bytes(
        r'./data/contract/mpc.cpp.abi.json'),
        addrress)
    result = wt.eth.waitForTransactionReceipt(resp)
    contract_address = result['contractAddress']
    return contract_address


class TestMpc:
    url = LoadFile('./conf/node.yml').get_data()['node1']["url"]
    config_alice = LoadFile(os.path.abspath('./conf/alice.yml'))
    dict_alice = config_alice.get_data()
    config_bob = LoadFile(os.path.abspath('./conf/bob.yml'))
    dict_bob = config_bob.get_data()
    config = LoadFile(os.path.abspath('./conf/node.yml'))
    node_dicts = config.get_data()
    # 上传文件本地和远程路径
    a_local_con = os.path.abspath(
        './data/rely/Alice/cfg.server1.conf')
    a_local_json = os.path.abspath(
        './data/rely/Alice/mpcc.cpp.abi.json')
    a_server_con = r'/home/juzhen/rely/conf/cfg.server1.conf'
    a_server_json = r'/home/juzhen/rely/conf/mpcc.cpp.abi.json'
    b_local_con = os.path.abspath('./data/rely/Bob/cfg.server2.conf')
    b_local_json = os.path.abspath('./data/rely/Bob/mpcc.cpp.abi.json')
    b_server_con = r'/home/juzhen/rely/conf/cfg.server2.conf'
    b_server_json = r'/home/juzhen/rely/conf/mpcc.cpp.abi.json'
    keystore = os.path.abspath(
        './data/keystore/UTC--2018-12-13T11-22-51.760472747Z--2fd96b410e4472a687fc1a872ef70abbb658bb9a')
    keystore_ser = r'/home/juzhen/rely/data16789/keystore/UTC--2018-12-13T11-22-51.760472747Z--2fd96b410e4472a687fc1a872ef70abbb658bb9a'

    ssh_alice, sftp_alice, t_alice = connect_linux(dict_alice['host'],
                                                   username=dict_alice['username'],
                                                   password=dict_alice['password'])
    ssh_bob, sftp_bob, t_bob = connect_linux(dict_bob['host'],
                                             username=dict_bob['username'],
                                             password=dict_bob['password'])
    stop_java(ssh_alice)
    stop_java(ssh_bob)

    def start_mpc_platon_node(self):
        '''

        :return:
        '''
        genesis_path = './data/genesis/interface_genesis/genesis.json'
        auto = AutoDeployPlaton()
        # rpc_url, enode_list, nodeid_list = auto.start_multi_node(
        #     './conf/mpc_node.yml', genesis_path=genesis_path)
        lf = LoadFile('./conf/node.yml').get_data()
        enode_list = []
        for k in lf.keys():
            if 'node' in k:
                enode_list.append(
                    "enode://"+lf[k]['id']+'@'+lf[k]['host']+':'+str(lf[k]['port']))
        auto.start_one_node('./conf/alice.yml',
                            genesis_file=os.path.abspath(genesis_path))
        auto.start_one_node('./conf/bob.yml',
                            genesis_file=os.path.abspath(genesis_path))
        time.sleep(2)
        # 上传依赖的文件
        self.upload_files()
        # 关闭进程
        auto.stop_platon(self.ssh_alice, rpcport=6789)
        auto.stop_platon(self.ssh_bob, rpcport=6789)
        time.sleep(3)
        # Alice和Bob开启进程
        cmd = '''nohup ./rely/rely --identity rely --rpc --datadir ./rely/data16789 --port 16789 --rpcport 6789 --rpcapi db,eth,net,web3,miner,admin,personal --rpcaddr 0.0.0.0 --nodiscover --mpc --mpc.actor 493301712671ada506ba6ca7891f436d29185821 --mpc.ice ./rely/conf/cfg.server1.conf > ./rely/nohup.out 2>&1 &'''
        self.ssh_alice.exec_command("source /etc/profile;%s" % cmd)
        cmd = '''nohup ./rely/rely --identity rely --rpc --datadir ./rely/data16789 --port 16789 --rpcport 6789 --rpcapi db,eth,net,web3,miner,admin,personal --rpcaddr 0.0.0.0 --nodiscover --mpc --mpc.actor ed9e836858feb6f26a01fcd951b2038d8c9c1ab9 --mpc.ice ./rely/conf/cfg.server2.conf > ./rely/nohup.out 2>&1 &'''
        self.ssh_bob.exec_command("source /etc/profile;%s" % cmd)
        time.sleep(5)
        self.w3_alice = connect_web3(self.dict_alice.get('url'))
        self.w3_bob = connect_web3(self.dict_bob.get('url'))
        # # 加入节点
        admin_alice = Admin(self.w3_alice)
        admin_alice.addPeer(enode_list[0])
        admin_bob = Admin(self.w3_bob)
        admin_bob.addPeer(enode_list[0])
        time.sleep(5)
        assert self.w3_alice.net.peerCount == 1, "alice加入节点失败"
        assert self.w3_bob.net.peerCount == 1, "bob加入节点失败"
        # 启动mpc服务
        time.sleep(2)
        # 开启mpc服务进程
        self.start_mpc()

    def upload_files(self):
        # 上传文件
        self.ssh_alice.exec_command('mkdir ./rely/conf')
        time.sleep(1)
        self.sftp_alice.put(self.a_local_con, self.a_server_con)
        self.sftp_alice.put(self.a_local_json, self.a_server_json)
        self.ssh_bob.exec_command('mkdir ./rely/conf')
        time.sleep(1)
        self.sftp_bob.put(self.b_local_con, self.b_server_con)
        self.sftp_bob.put(self.b_local_json, self.b_server_json)
        self.sftp_bob.put(self.keystore, self.keystore_ser)

    def transaction(self):
        # 参与计算的钱包地址需要解锁和有钱
        account = self.w3_alice.toChecksumAddress(
            self.w3_alice.eth.accounts[0])
        self.w3_alice.personal.unlockAccount(account, '88888888', 6666666)
        to_bob_account = self.w3_bob.toChecksumAddress(
            self.w3_bob.eth.accounts[1])
        self.w3_bob.personal.unlockAccount(to_bob_account, '88888888', 6666666)
        params = {
            'to': to_bob_account,
            'from': account,
            'gas': 90000,
            'gasPrice': 9000000000,
            'value': 1000000000000000000000
        }
        hx = self.w3_alice.eth.sendTransaction(params)
        self.w3_bob.eth.waitForTransactionReceipt(hx, timeout=15)

    def start_mpc(self):
        cmd = '''java -jar ./private-contract-sdk/samples/mpc-data-sdk-client1/target/mpc-data-sdk-client1-1.0-SNAPSHOT.jar -iceCfgFile=./private-contract-sdk/samples/conf/cfg.client1.linux.conf -walletPath=./private-contract-sdk/samples/conf/UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821 -walletPass=88888888'''
        self.ssh_alice.exec_command("source /etc/profile;%s" % cmd)
        cmd = '''java -jar ./private-contract-sdk/samples/mpc-data-sdk-client2/target/mpc-data-sdk-client2-1.0-SNAPSHOT.jar -iceCfgFile=./private-contract-sdk/samples/conf/cfg.client2.linux.conf -walletPath=./private-contract-sdk/samples/conf/UTC--2018-12-13T11-22-51.760472747Z--2fd96b410e4472a687fc1a872ef70abbb658bb9a -walletPass=88888888'''
        self.ssh_bob.exec_command("source /etc/profile;%s" % cmd)

    def send_calculation(self, method='0xdb880000000000000005875465737441646489657874726164617461'):
        '''
        :param method: 算法的data
        :return:交易hash

        '''
        contract_address = deploy_contract()
        data = {
            "jsonrpc": "2.0",
            "method": "eth_sendTransaction",
            "params": [{
                "from": "0x493301712671ada506ba6ca7891f436d29185821",
                "to": contract_address,
                "gas": "0x127eed",
                "gasPrice": "0x8250de00",
                "value": "0x2540BE401",
                "data": method
            }
            ],
            "id": 1
        }
        ret = requests.post(url=self.dict_alice['url'], json=data)
        dic = ret.json()
        transaction_hash = dic['result']
        return transaction_hash, contract_address

    def test_check_result_alicedd(self):
        self.start_mpc_platon_node()
        time.sleep(5)
        self.transaction()
        transaction_hash, contract_address = self.send_calculation()
        self.w3_alice.eth.waitForTransactionReceipt(transaction_hash)
        time.sleep(20)
        # status = 0
        account = 'UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821'
        cmd = 'java -jar ./private-contract-sdk/samples/mpc-proxy-sdk-tool/target/mpc-proxy-sdk-tool-1.0-SNAPSHOT.jar' \
              ' --walletPath="./private-contract-sdk/samples/conf/' \
              '{}" --walletPass=88888888 ' \
              '--url="http://192.168.9.177:6789" --contractAddress="{}"  ' \
              '--api="getResultByTransactionHash({})" ' \
              '--method=TestSub'.format(account,
                                        contract_address, transaction_hash)
        # stdin, stdout, stderr = self.ssh_alice.exec_command(
        #     "source /etc/profile;%s" % cmd)
        # result = stdout.readlines()
        # for i in result:
        #     if 'int: 6912' in i:
        #         status = 1
        # assert status
        t1 = Thread(target=start, args=(self.ssh_alice, cmd,))
        t1.setDaemon(True)
        t1.start()
        times = 180
        for i in range(times):
            if not q.empty():
                assert q.get()
                break
            if i == (times-1) and q.empty():
                assert False, "没有结果返回"
            time.sleep(1)


def start(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command("source /etc/profile;%s" % cmd)
    result = stdout.readlines()
    print(result)
    for i in result:
        if 'int: 6912' in i:
            q.put(1)
