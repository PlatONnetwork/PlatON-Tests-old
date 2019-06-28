# -*- coding: UTF-8 -*-
"""
@author: DouYueWei
@time: 2019/1/7 11:02
@usage:
"""
import os
import sys
import json
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0][:-15]
sys.path.append(rootPath)
from utils.platon_lib.event import Event
from utils.platon_lib.contract import *
from utils.platon_lib import encoder

wasm_path = os.path.abspath('../data/contract/sum.wasm')
abi_path = os.path.abspath('../data/contract/sum.cpp.abi.json')


def contract_transaction(url):
    """初始化web3"""
    pt = PlatonContractTransaction(url)
    address = pt.w3.toChecksumAddress(pt.eth.coinbase)
    pt.w3.personal.unlockAccount(address, '88888888', 99999999)
    """部署合约"""
    resp = pt.contract_deploy(get_byte_code(
        wasm_path), get_abi_bytes(abi_path), address)
    result = pt.eth.waitForTransactionReceipt(resp)
    contract_address = result['contractAddress']
    """发送交易"""
    data_list = [encoder.encode_type(
        2), encoder.encode_string('set')]
    trans_resp = pt.contract_transaction(address, contract_address, data_list)
    result = pt.w3.eth.waitForTransactionReceipt(trans_resp)
    """查看eventData"""
    topics = result['logs'][0]['topics']
    data = result['logs'][0]['data']
    event = Event(json.load(open(abi_path)))
    event_data = event.event_data(topics, data)
    assert 'set success' in event_data['create'][0]
    """call方法查询交易"""
    call_data_list = [encoder.encode_type(
        2), encoder.encode_string('get')]
    receive = pt.contract_call(address, contract_address, call_data_list)
    receive = int.from_bytes(receive, 'big')
    assert receive == 11


if __name__ == '__main__':
    contract_transaction('http://192.168.9.164:6789')
