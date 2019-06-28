# -*- coding: UTF-8 -*-
'''
@Author: wuyiqin
@Date: 2019-04-08 10:20:33
@LastEditors: wuyiqin
@LastEditTime: 2019-04-20 14:24:09
@Description: file content
'''
import json
import time

import allure
import pytest
from hexbytes import HexBytes

from common.abspath import abspath
from common.connect import connect_web3
from common.key import get_pub_key
from common.load_file import get_f, get_node_info, get_node_list
from common.log import log
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton
from utils.platon_lib.contract import (PlatonContractTransaction,
                                       get_abi_bytes,
                                       get_byte_code)


class TestConsensus:
    node_yml = conf.NODE_YML
    consensus_list, _ = get_node_list(node_yml)
    f = get_f(consensus_list)
    n = len(consensus_list)
    url_list, enode_list, nodeid_list, ip_list, _ = get_node_info(
        node_yml)["collusion"]
    genesis_path = conf.GENESIS_TMP
    auto = AutoDeployPlaton()
    cbft_path = conf.CBFT_TMP
    cbft_template = conf.CBFT_TEMPLATE

    def teardown_class(self):
        self.auto.start_all_node(self.node_yml)

    def get_cbft_json_data(self, period, duration):
        with open(self.cbft_template, 'r', encoding='utf-8') as f:
            res = json.loads(f.read())
            res['period'] = period
            res['duration'] = duration
        with open(self.cbft_path, 'w', encoding='utf-8') as b:
            cbft_json = json.dumps(res)
            b.write(cbft_json)

    @allure.title("每个节点在窗口期正常出块")
    def test_block_out_of_each_node_window(self):
        """
        用例id：73
        测试 N 个节点每个窗口期都在出块
        """
        log.info("更新cbft文件")
        self.get_cbft_json_data(period=1, duration=10)
        auto = AutoDeployPlaton(cbft=self.cbft_path)
        auto.start_all_node(self.node_yml)
        log.info("跟所有节点建立连接")
        w3_list = [connect_web3(url) for url in self.url_list]
        w3 = w3_list[0]
        start_block = w3.eth.blockNumber
        time.sleep(self.n * 10 + 5)
        block_number = w3.eth.blockNumber
        if block_number > 0:
            log.info("正在出块,块高:{}".format(block_number))
        node_id_dict = {}
        log.info("获取1至{}块的nodeID".format(block_number))
        for block in range(start_block, block_number + 1):
            node_id = get_pub_key(self.url_list[0], block)
            if node_id not in node_id_dict.keys():
                node_id_dict[node_id] = 1
            else:
                node_id_dict[node_id] += 1
        log.info("nodeID对应的出块数{}".format(node_id_dict))
        assert self.n == len(node_id_dict), "出块节点数少于共识节点数"
        for k, v in node_id_dict.items():
            assert 0 <= v <= 20, "节点{}出块周期约为10个块，实际为{}".format(k, v)

    @allure.title("cbft.json配置period{period}-{duration}")
    @pytest.mark.parametrize('period,duration', [(1, 10), (3, 30), (5, 50), (10, 100), (0, 10)])
    def test_block_time_period(self, period, duration):
        '''
        用例id 1,2,3,4,5
        测试period的不同值，观察查看时间
        根据5种场景，分别出块时间约为1,3,5,10,1s
        '''
        log.info("更新cbft.json")
        self.get_cbft_json_data(period, duration)
        auto = AutoDeployPlaton(cbft=self.cbft_path)
        auto.start_all_node(self.node_yml)
        time.sleep(duration+5)
        log.info("跟所有节点建立连接")
        w3_list = [connect_web3(url) for url in self.url_list]
        w3 = w3_list[0]
        block_number = w3.eth.blockNumber
        assert block_number > 1, "没有正常出块"
        log.info(block_number)
        start_time = w3.eth.getBlock(1).get("timestamp")
        end_time = w3.eth.getBlock(block_number).get("timestamp")
        use_time = end_time - start_time
        average_time = int(use_time/(block_number-1))
        log.info("平均出块时间{}".format(average_time))
        if period == 0:
            period = 1
        deviation = int(period * 1000 * 0.5)
        assert period * 1000 - deviation < average_time < period * \
            1000 + deviation, "出块间隔过大或过小"

    @allure.title("cbft.json配置period{period}-{duration}-{delay_time}--{number}")
    @pytest.mark.parametrize('period,duration,delay_time,number', [(1, 10, 50, 30), (1, 20, 90, 70), (1, 30, 130, 90),
                                                                   (1, 50, 180, 140), (1, 100, 350, 250)])
    def test_block_cycle_duration(self, period, duration, delay_time, number):
        '''
        用例id 6,7,8,9,10
        测试duration的不同值，观察出块周期
        根据5种场景，出块周期约为10,20,30,50,100
        '''
        self.get_cbft_json_data(period, duration)
        auto = AutoDeployPlaton(cbft=self.cbft_path)
        log.info("上传cbft文件成功")
        auto.start_all_node(self.node_yml)
        time.sleep(delay_time)
        log.info("跟所有节点建立连接")
        w3_list = [connect_web3(url) for url in self.url_list]
        w3 = w3_list[0]
        block_number = w3.eth.blockNumber
        if block_number > 0:
            log.info("正在出块,块高:{}".format(block_number))
        if block_number < number:
            raise Exception("出块很慢，没达到预期{}".format(number))
        node_id_dict = {}
        log.info("获取1至{}块的nodeID".format(number))
        for block in range(1, number):
            node_id = get_pub_key(self.url_list[0], block)
            if node_id not in node_id_dict.keys():
                node_id_dict[node_id] = [block]
            else:
                node_id_dict[node_id].append(block)
        log.info("获取到全部的nodeID对应的出块".format(node_id_dict))
        log.info("由于第一组nodeID收集数据不全，从第二组开始收集统计，删除第一组")
        node_id_list = []
        for node_id in node_id_dict.keys():
            node_id_list.append(node_id)
        node_id_dict.pop(node_id_list[0])
        log.info("统计出nodeID对应的出块ID{}".format(node_id_dict))
        print(node_id_dict)
        print(node_id_list)
        if duration == 10:
            block_cycle_a = node_id_dict.get(node_id_list[1])
            log.info("出块人A出块周期数:%s" % block_cycle_a)
            assert 7 <= len(block_cycle_a) <= 12, "出块周期预期在7到12，实际{}".format(
                len(block_cycle_a))
            block_cycle_b = node_id_dict.get(node_id_list[2])
            log.info("出块人B出块周期数:%s" % block_cycle_b)
            assert 7 <= len(block_cycle_b) <= 12, "出块周期预期在7到12，实际{}".format(
                len(block_cycle_b))
            times_tamp_a = w3.eth.getBlock(block_cycle_a[-1]).get("timestamp")
            times_tamp_b = w3.eth.getBlock(block_cycle_b[-1]).get("timestamp")
            log.info("获取出块人B的最后一个块的时间戳%s" % times_tamp_b)
            assert 8000 < times_tamp_b - \
                times_tamp_a < 12000, "预期出块周期为8到12s，实际为{}".format(
                    times_tamp_b - times_tamp_a)
            log.info(
                "出块人B最后一个块出块时间-出块人A最后一个块出块时间 = 出块周期时间{}".format(times_tamp_b - times_tamp_a))

        if duration == 20:
            block_cycle_a = node_id_dict.get(node_id_list[1])
            log.info("出块人A出块周期数:%s" % block_cycle_a)
            assert 16 <= len(block_cycle_a) <= 23, "出块周期预期在16到23，实际{}".format(
                len(block_cycle_a))
            block_cycle_b = node_id_dict.get(node_id_list[2])
            log.info("出块人B出块周期数:%s" % block_cycle_b)
            assert 16 <= len(block_cycle_b) <= 23, "出块周期预期在16到23，实际{}".format(
                len(block_cycle_b))
            times_tamp_a = w3.eth.getBlock(block_cycle_a[-1]).get("timestamp")
            times_tamp_b = w3.eth.getBlock(block_cycle_b[-1]).get("timestamp")
            log.info("获取出块人B的最后一个块的时间戳%s" % times_tamp_b)
            assert 16000 < times_tamp_b - times_tamp_a < 23000, "预期出块周期为16到23s，实际为{}".format(
                times_tamp_b - times_tamp_a)
            log.info(
                "出块人B最后一个块出块时间-出块人A最后一个块出块时间 = 出块周期时间{}".format(times_tamp_b - times_tamp_a))

        if duration == 30:
            block_cycle_a = node_id_dict.get(node_id_list[1])
            log.info("出块人A出块周期数:%s" % block_cycle_a)
            assert 26 <= len(block_cycle_a) <= 33, "出块周期预期在26到33，实际{}".format(
                len(block_cycle_a))
            block_cycle_b = node_id_dict.get(node_id_list[2])
            log.info("出块人B出块周期数:%s" % block_cycle_b)
            assert 26 <= len(block_cycle_b) <= 33, "出块周期预期在26到33，实际{}".format(
                len(block_cycle_b))
            times_tamp_a = w3.eth.getBlock(block_cycle_a[-1]).get("timestamp")
            times_tamp_b = w3.eth.getBlock(block_cycle_b[-1]).get("timestamp")
            log.info("获取出块人B的最后一个块的时间戳%s" % times_tamp_b)
            assert 26000 < times_tamp_b - times_tamp_a < 33000, "预期出块周期为26到30s，实际为{}".format(
                times_tamp_b - times_tamp_a)
            log.info(
                "出块人B最后一个块出块时间-出块人A最后一个块出块时间 = 出块周期时间{}".format(times_tamp_b - times_tamp_a))

        if duration == 50:
            block_cycle_a = node_id_dict.get(node_id_list[1])
            log.info("出块人A出块周期数:%s" % block_cycle_a)
            assert 40 <= len(block_cycle_a) <= 60, "出块周期预期在40到60，实际{}".format(
                len(block_cycle_a))
            block_cycle_b = node_id_dict.get(node_id_list[2])
            log.info("出块人B出块周期数:%s" % block_cycle_b)
            assert 40 <= len(block_cycle_b) <= 60, "出块周期预期在40到60，实际{}".format(
                len(block_cycle_b))
            times_tamp_a = w3.eth.getBlock(block_cycle_a[-1]).get("timestamp")
            times_tamp_b = w3.eth.getBlock(block_cycle_b[-1]).get("timestamp")
            log.info("获取出块人B的最后一个块的时间戳%s" % times_tamp_b)
            assert 4000 < times_tamp_b - times_tamp_a < 60000, "预期出块周期为40到60s，实际为{}".format(
                times_tamp_b - times_tamp_a)
            log.info(
                "出块人B最后一个块出块时间-出块人A最后一个块出块时间 = 出块周期时间{}".format(times_tamp_b - times_tamp_a))

        if duration == 100:
            block_cycle_a = node_id_dict.get(node_id_list[1])
            log.info("出块人A出块周期数:%s" % block_cycle_a)
            assert 90 <= len(block_cycle_a) <= 110, "出块周期预期在90到110，实际{}".format(
                len(block_cycle_a))
            block_cycle_b = node_id_dict.get(node_id_list[2])
            log.info("出块人B出块周期数:%s" % block_cycle_b)
            assert 90 <= len(block_cycle_b) <= 110, "出块周期预期在90到110，实际{}".format(
                len(block_cycle_b))
            times_tamp_a = w3.eth.getBlock(block_cycle_a[-1]).get("timestamp")
            times_tamp_b = w3.eth.getBlock(block_cycle_b[-1]).get("timestamp")
            log.info("获取出块人B的最后一个块的时间戳%s" % times_tamp_b)
            assert 90000 < times_tamp_b - times_tamp_a < 110000, "预期出块周期为99到110s，实际为{}".format(
                times_tamp_b - times_tamp_a)
            log.info(
                "出块人B最后一个块出块时间-出块人A最后一个块出块时间 = 出块周期时间{}".format(times_tamp_b - times_tamp_a))

    @allure.title("重启节点后查看旧块交易，钱包余额")
    def test_kill_process_observation_block_data(self):
        '''
       用例id 30,31,32,33
       测试kill进程后，重启查看块高持续增长
       测试kill进程后，重启查看旧块转账，合约信息不变
       测试kill进程后，钱包余额不变
        '''
        log.info("部署节点")
        self.auto.start_all_node(self.node_yml)
        log.info("启动会等待60s出块")
        time.sleep(10)
        log.info("跟所有节点建立连接")
        w3_list = [connect_web3(url) for url in self.url_list]
        w3 = w3_list[0]
        number_before = w3.eth.blockNumber
        if number_before == 0:
            raise Exception("起服务但未出块")
        log.info("块高为：{}".format(number_before))
        log.info("发起转账交易")
        t_hash = self.transaction(w3)
        result, number, result_block, hash_list = self.check_block_information(
            w3, t_hash)
        log.info("发起合约交易")
        contract_address, resp, contract_number = self.deploy_contract()
        log.info("kill 所有节点")
        self.auto.kill_of_yaml(self.node_yml)
        time.sleep(2)
        log.info("重启platon服务")
        self.auto.start_all_node(self.node_yml, is_need_init=False)
        log.info("重启25节点后，延迟30s")
        time.sleep(30)
        w3_list = [connect_web3(url) for url in self.url_list]
        w3 = w3_list[0]
        number_after = w3.eth.blockNumber
        assert number_after >= number_before, "块高未有增长"
        balance = w3.eth.getBalance(w3.eth.accounts[1])
        assert balance == 100000, "kill进程重启后余额发生变化，余额为：{}".format(balance)
        log.info("查看重启前的{}区块转账信息".format(number))
        t_hash_list = (w3.eth.getBlock(number).get("transactions"))
        log.info("查看重启前的{}区块合约信息".format(contract_number))
        c_hash_list = (w3.eth.getBlock(contract_number).get("transactions"))
        log.info("通过transactions字段得到的交易哈希列表：{}".format(hash_list))
        assert t_hash in t_hash_list, "kill进程重启后转账交易丢失"
        c_hash = HexBytes(resp)
        assert c_hash in c_hash_list, "kill进程重启后合约交易丢失"
        contract_address_after = w3.eth.waitForTransactionReceipt(
            resp).get('contractAddress')
        assert contract_address == contract_address_after, "kill进程后，合约地址发生改变"

    def check_block_information(self, w3, hash):
        transaction_hash = HexBytes(hash).hex()
        result = w3.eth.waitForTransactionReceipt(transaction_hash)
        number = result.get("blockNumber")
        result_block = w3.eth.getBlock(number)
        hash_list = result_block.get("transactions")
        return result, number, result_block, hash_list

    def transaction(self, w3, value=100000):
        from_address = w3.toChecksumAddress(w3.eth.accounts[0])
        to_address = w3.toChecksumAddress(w3.personal.newAccount('88888888'))
        log.info("解锁账号")
        w3.personal.unlockAccount(from_address, '88888888', 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': 91000000,
            'gasPrice': 9000000000,
            'value': value
        }
        t_hash = w3.eth.sendTransaction(params)
        return t_hash

    def deploy_contract(self):
        consensus_list, _ = get_node_list(self.node_yml)
        url = consensus_list[0]['url']
        wt = PlatonContractTransaction(url)
        addrress = wt.w3.toChecksumAddress(conf.ADDRESS)
        wt.w3.personal.unlockAccount(addrress, conf.PASSWORD, 99999999)
        log.info("部署合约")
        resp = wt.contract_deploy(get_byte_code(
            abspath('./data/contract/sum.wasm')),
            get_abi_bytes(
                abspath('./data/contract/sum.cpp.abi.json')),
            addrress)
        log.info("获取合约交易信息")
        result = wt.eth.waitForTransactionReceipt(resp)
        contract_address = result['contractAddress']
        contract_number = result['blockNumber']
        return contract_address, resp, contract_number
