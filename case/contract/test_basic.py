import json

import allure
import pytest
from hexbytes import HexBytes
from client_sdk_python import Web3

from common import log
from common.abspath import abspath
from common.handle_param import handle, handle_param
from common.load_file import get_node_list
from conf import setting as conf
from data import basic as config_data
from utils.platon_lib import contract
from utils.platon_lib.contract import (PlatonContractTransaction,
                                       contract_call_result_decode)
from utils.platon_lib.contract import encoder
from utils.platon_lib.event import Event
from utils.platon_lib.send_raw_transaction import send_raw_transaction

collusion_list, _ = get_node_list(conf.NODE_YML)
node_url = collusion_list[0]['url']
address = Web3.toChecksumAddress(
    '493301712671ada506ba6ca7891f436d29185821')

send_address = Web3.toChecksumAddress("0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79")
send_privatekey = "b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357"


def contract_deploy(pt, wasm_path, abi_path):
    '''
    部署wasm合约方法
    '''
    address = pt.eth.coinbase
    pt.personal.unlockAccount(address, '88888888', 999999)
    deploy_trans_hash = pt.contract_deploy(contract.get_byte_code(wasm_path),
                                           contract.get_abi_bytes(abi_path), address)
    try:
        result = pt.eth.waitForTransactionReceipt(deploy_trans_hash)
    except:
        assert False, "等待超时，交易哈希：{}".format(deploy_trans_hash)
    contract_address = result['contractAddress']
    log.info("合约地址:{}".format(contract_address))
    assert len(pt.eth.getCode(contract_address)
               ) > 3, '合约部署异常，getCode(contract_address)结果异常'
    return contract_address


def setup_module():
    pt_multi = PlatonContractTransaction(node_url)
    for k, w in config_data.wasm.items():
        contract_address = contract_deploy(pt_multi, abspath(w),
                                           abspath(config_data.abi[k]))
        config_data.contract_address[k] = contract_address
    handle(config_data.contract_address)
    send_data = {
        "to": send_address,
        "from": address,
        "gas": '9000',
        "gasPrice": '1000000000',
        "value": Web3.toWei(200, 'ether'),
    }
    tx_hash = pt_multi.eth.sendTransaction(send_data)
    pt_multi.eth.waitForTransactionReceipt(tx_hash)


def teardown_module():
    log.info("结束了")


@allure.title("测试basic合约,方法{casedata[func]}，name：{casedata[name]}")
@pytest.mark.parametrize('casedata', config_data.func["basic"])
def test_contract(casedata):
    """
    用例主要测试基础数据类型,方法{}，name：{}
    """.format(casedata["func"], casedata["name"])
    log.info("方法{}，name：{}".format(casedata["func"], casedata["name"]))
    pt_multi = PlatonContractTransaction(node_url)
    encode_param = handle_param(casedata["param"])
    data_list = [encoder.encode_type(
        2), encoder.encode_string(casedata["func"])] + encode_param
    trans_hex = send_raw_transaction(send_address, send_privatekey, casedata["contract_address"], pt_multi.w3, 0,
                                     data_list)
    # trans_hex = pt_multi.contract_transaction(
    #     address, casedata["contract_address"], data_list)
    try:
        result = pt_multi.eth.waitForTransactionReceipt(trans_hex)
    except:
        assert False, "等待超时，交易哈希：{}".format(trans_hex)
    log.info("transaction hex:{}".format(trans_hex))
    if casedata.get("event"):
        event_data = ex_event(result, casedata)
        log.info(event_data)
        assert casedata["event"] in event_data['notify'][1], '合约交易失败，event事件无{}'.format(
            casedata["event"])
    if casedata.get("notevent"):
        a = 0
        try:
            event_data = ex_event(result, casedata)
            log.info("event data:{}".format(event_data))
            call_value = call(casedata, pt_multi)
            log.info("call:{}".format(call_value))
            a = 1
        except:
            log.info("没有event")
        finally:
            assert a == 0, "有执行event"
    if casedata.get("expect"):
        get_value = call(casedata, pt_multi)
        log.info("call value:{}".format(get_value))
        assert get_value == casedata["expect"], 'get结果异常，预期值：{}，实际结果：{}'.format(
            casedata["expect_value"], get_value)


def call(casedata, pt_multi):
    data_list_for_call = [encoder.encode_type(
        2), encoder.encode_string(casedata["call_func"])]
    receive = pt_multi.contract_call(
        address, casedata["contract_address"], data_list_for_call)
    if casedata.get("expect_type") == "str":
        value = contract_call_string(receive)
    else:
        value = contract_call_result_decode(receive)
    return value


def ex_event(result, casedata):
    topics = result['logs'][0]['topics']
    d = result['logs'][0]['data']
    event = Event(
        json.load(open(abspath(config_data.abi[casedata["contract_name"]]))))
    event_data = event.event_data(topics, d)
    return event_data


def contract_call_string(call_result):
    length = int(call_result[66:130], 16) * 2
    data = call_result[130:130 + length]
    ret = HexBytes(data).decode()
    return ret.lower()
