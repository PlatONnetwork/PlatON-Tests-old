# -*- coding: UTF-8 -*-
"""
@author: DouYueWei
@time: 2018/11/30 14:08
@usage:
"""
import json
import os
import time

import allure
import pytest
from hexbytes import HexBytes
from client_sdk_python import Web3

from common import log
from common.abspath import abspath
from conf import  setting as conf
from common.load_file import get_node_list
from utils.platon_lib import encoder
from utils.platon_lib.event import Event
from utils.platon_lib.contract import (PlatonContractTransaction,
                                       contract_call_result_decode,get_byte_code,get_abi_bytes)


def contract_deploy(pt, wasm_path, abi_path):
    '''
    部署wasm合约方法
    '''
    address = pt.eth.coinbase
    pt.personal.unlockAccount(address, '88888888', 999999)
    deploy_trans_hash = pt.contract_deploy(get_byte_code(wasm_path),
                                           get_abi_bytes(abi_path), address)
    try:
        result = pt.eth.waitForTransactionReceipt(deploy_trans_hash)
    except:
        assert False, "等待超时，交易哈希：{}".format(deploy_trans_hash)
    contract_address = result['contractAddress']
    log.info("合约地址:{}".format(contract_address))
    assert len(pt.eth.getCode(contract_address)
               ) > 3, '合约部署异常，getCode(contract_address)结果异常'
    return contract_address


class TestContract:
    node_yml = conf.NODE_YML
    collusion_list, nocollusion_list = get_node_list(node_yml)
    nocollusion_url = nocollusion_list[0]['url']
    collusion_url = collusion_list[0]['url']
    address = Web3.toChecksumAddress(conf.ADDRESS)
    private_key_hex = conf.PRIVATE_KEY
    private_key = HexBytes(private_key_hex)
    url_list = [nocollusion_url, collusion_url]
    param_list = [(abspath('./data/contract/Fibonacci.wasm'),
                   abspath('./data/contract/Fibonacci.cpp.abi.json'), 10, 143),
                  (abspath('./data/contract/matmul.wasm'),
                   abspath('./data/contract/matmul.cpp.abi.json'), 10, -183325)]

    @allure.title("非共识节点&共识节点 部署wasm合约测试")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_contract_deploy(self, pt1):
        '''
        非共识节点&共识节点 部署wasm合约测试
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/sum.wasm')
        abi_path = abspath('./data/contract/sum.cpp.abi.json')

        # 部署合约
        contract_address = contract_deploy(pt, wasm_path, abi_path)
        assert contract_address is not None, '合约部署失败，合约地址为空'
        contract_code = pt.eth.getCode(contract_address)
        assert len(contract_code) > 3, '合约部署异常，getCode(contract_address)结果异常'

    @allure.title("非共识节点&共识节点 wasm合约交易、event事件、call方法测试")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_contract_transaction(self, pt1):
        '''
        非共识节点&共识节点 wasm合约交易、event事件、call方法测试
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/sum.wasm')
        abi_path = abspath('./data/contract/sum.cpp.abi.json')
        address = pt.eth.coinbase
        contract_address = contract_deploy(pt, wasm_path, abi_path)

        # 发送合约交易
        data_list = [encoder.encode_type(
            2), encoder.encode_string('set')]
        trans_hex = pt.contract_transaction(
            address, contract_address, data_list)
        try:
            result = pt.eth.waitForTransactionReceipt(trans_hex)
        except:
            assert False, "等待超时，交易哈希：{}".format(trans_hex)
        # 解析event事件
        topics = result['logs'][0]['topics']
        data = result['logs'][0]['data']
        event = Event(json.load(open(abi_path)))
        event_data = event.event_data(topics, data)
        assert 'set success' in event_data['create'][0], '合约交易失败，event事件无"set success"'
        # call方法查询交易结果
        data_list_for_call = [encoder.encode_type(
            2), encoder.encode_string('get')]
        receive = pt.contract_call(
            address, contract_address, data_list_for_call)
        decoded_sum_result = int.from_bytes(receive, 'big')
        assert decoded_sum_result == 1, '自增失败，预期自增后结果为1，实际值为{}'.format(
            decoded_sum_result)

    @allure.title("非共识节点&共识节点 wasm合约输入、输出结果校验")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_contract_set_and_get_function(self, pt1):
        '''
        非共识节点&共识节点 wasm合约输入、输出结果校验
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/inputtest.wasm')
        abi_path = abspath(
            './data/contract/inputtest.cpp.abi.json')
        address = pt.eth.coinbase
        contract_address = contract_deploy(pt, wasm_path, abi_path)
        set_value = -100

        # 合约set方法存入int型数值
        data_list = [encoder.encode_type(2), encoder.encode_string('set'),
                     encoder.encode_int('int64', set_value)]
        trans_hex = pt.contract_transaction(
            address, contract_address, data_list)
        try:
            result = pt.eth.waitForTransactionReceipt(trans_hex)
        except:
            assert False, "等待超时，交易哈希：{}".format(trans_hex)
        # 合约get方法获取存入的数值校验是否一致
        data_list_for_call = [encoder.encode_type(
            2), encoder.encode_string('get')]
        receive = pt.contract_call(
            address, contract_address, data_list_for_call)
        get_value = contract_call_result_decode(receive)
        assert get_value == set_value, 'get结果异常，预期值：{}，实际结果：{}'.format(
            set_value, get_value)

    def _singed_contract_deploy(self, pt, wasm_path, abi_path):
        '''
        部署wasm签名合约方法
        '''
        deploy_trans_hash = pt.signed_contract_deploy(get_byte_code(wasm_path),
                                                      get_abi_bytes(
                                                          abi_path),
                                                      self.address, self.private_key)
        try:
            result = pt.eth.waitForTransactionReceipt(deploy_trans_hash)
        except:
            assert False, "等待超时，交易哈希：{}".format(deploy_trans_hash)
        contract_address = result['contractAddress']
        assert len(pt.eth.getCode(contract_address)
                   ) > 3, '合约部署异常，getCode(contract_address)结果异常'
        return contract_address

    @allure.title("非共识节点&共识节点 部署wasm签名合约测试")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_singed_contract_deploy(self, pt1):
        '''
        非共识节点&共识节点 部署wasm签名合约测试
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/sum.wasm')
        abi_path = abspath('./data/contract/sum.cpp.abi.json')

        # 部署合约
        contract_address = self._singed_contract_deploy(
            pt, wasm_path, abi_path)
        assert contract_address is not None, '合约部署失败，合约地址为空'
        contract_code = pt.eth.getCode(contract_address)
        assert len(contract_code) > 3, '合约部署异常，getCode(contract_address)结果异常'

    @allure.title("非共识节点&共识节点 wasm合约签名交易、event事件、call方法测试")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_singed_contract_transaction(self, pt1):
        '''
        非共识节点&共识节点 wasm合约签名交易、event事件、call方法测试
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/sum.wasm')
        abi_path = abspath('./data/contract/sum.cpp.abi.json')
        address = pt.eth.coinbase
        contract_address = self._singed_contract_deploy(
            pt, wasm_path, abi_path)

        # 发送合约交易
        data_list = [encoder.encode_type(
            2), encoder.encode_string('set')]
        trans_hex = pt.signed_contract_transaction(
            address, contract_address, data_list, self.private_key)
        try:
            result = pt.eth.waitForTransactionReceipt(trans_hex)
        except:
            assert False, "等待超时，交易哈希：{}".format(trans_hex)
        # 解析event事件
        topics = result['logs'][0]['topics']
        data = result['logs'][0]['data']
        event = Event(json.load(open(abi_path)))
        event_data = event.event_data(topics, data)
        assert 'set success' in event_data['create'][0], '合约交易失败，event事件无"set success"'
        # call方法查询交易结果
        data_list_for_call = [encoder.encode_type(
            2), encoder.encode_string('get')]
        receive = pt.contract_call(
            address, contract_address, data_list_for_call)
        decoded_sum_result = int.from_bytes(receive, 'big')
        assert decoded_sum_result == 1, '自增失败，预期自增后结果为1，实际值为{}'.format(
            decoded_sum_result)

    @allure.title("非共识节点&共识节点 wasm签名合约输入、输出结果校验")
    @pytest.mark.parametrize('pt1', url_list)
    def test_consensus_and_deconsensus_signed_contract_set_and_get_function(self, pt1):
        '''
        非共识节点&共识节点 wasm签名合约输入、输出结果校验
        '''
        pt = PlatonContractTransaction(pt1)
        wasm_path = abspath('./data/contract/inputtest.wasm')
        abi_path = abspath(
            './data/contract/inputtest.cpp.abi.json')
        address = pt.eth.coinbase
        contract_address = self._singed_contract_deploy(
            pt, wasm_path, abi_path)
        set_value = -100

        # 合约set方法存入int型数值
        data_list = [encoder.encode_type(2), encoder.encode_string('set'),
                     encoder.encode_int('int64', set_value)]
        trans_hex = pt.signed_contract_transaction(
            address, contract_address, data_list, self.private_key)
        result = ''
        for i in range(3):
            try:
                result = pt.eth.waitForTransactionReceipt(trans_hex)
            except:
                pt.reconnect()
        assert result != '', "等待超时，交易哈希：{}".format(trans_hex)

        # 合约get方法获取存入的数值校验是否一致
        data_list_for_call = [encoder.encode_type(
            2), encoder.encode_string('get')]
        receive = pt.contract_call(
            address, contract_address, data_list_for_call)
        get_value = contract_call_result_decode(receive)
        assert get_value == set_value, 'get结果异常，预期值：{}，实际结果：{}'.format(
            set_value, get_value)
        time.sleep(1)

    @allure.title("各算法合约计算结果测试")
    @pytest.mark.parametrize('wasm_path,abi_path,set_value,expect_value', param_list)
    def test_calc_contracts(self, wasm_path, abi_path, set_value, expect_value):
        '''
        各算法合约计算结果测试
        '''
        pt_one = PlatonContractTransaction(self.nocollusion_url)
        address = pt_one.eth.coinbase
        contract_address = contract_deploy(
            pt_one, wasm_path, abi_path)

        # 合约set方法存入int型数值
        data_list = [encoder.encode_type(2), encoder.encode_string('set'),
                     encoder.encode_int('int64', set_value)]
        trans_hex = pt_one.contract_transaction(
            address, contract_address, data_list)
        try:
            result = pt_one.eth.waitForTransactionReceipt(trans_hex)
        except:
            assert False, "等待超时，交易哈希：{}".format(trans_hex)
        # 合约get方法获取存入的数值校验是否一致
        data_list_for_call = [encoder.encode_type(
            2), encoder.encode_string('get')]
        receive = pt_one.contract_call(
            address, contract_address, data_list_for_call)
        get_value = contract_call_result_decode(receive)
        assert get_value == expect_value, 'get结果异常，预期值：{}，实际结果：{}'.format(
            expect_value, get_value)
