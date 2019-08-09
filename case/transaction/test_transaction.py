# -*- coding: utf-8 -*-
'''
@Author: wuyiqin
@Date: 2019-01-08 10:20:33
@LastEditors: wuyiqin
@LastEditTime: 2019-03-20 14:24:09
@Description: file content
'''
import time

from hexbytes import HexBytes
from client_sdk_python import Web3
from client_sdk_python.eth import Eth

from common.connect import connect_web3
from common.load_file import get_node_list, get_f
from conf import setting as conf
from utils.platon_lib.send_raw_transaction import send_raw_transaction

node_yml = conf.NODE_YML
collusion_list, nocollusion_list = get_node_list(node_yml)
f = get_f(collusion_list)
send_address = Web3.toChecksumAddress("0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79")
send_privatekey = "b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357"


def transaction(w3, from_address, to_address=None, value=1000000000000000000000, gas=91000000, gasPrice=9000000000):
    params = {
        'to': to_address,
        'from': from_address,
        'gas': gas,
        'gasPrice': gasPrice,
        'value': value
    }
    tx_hash = w3.eth.sendTransaction(params)
    return tx_hash


def test_singed_transaction():
    """
    测试签名转账交易
    """
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    eth = Eth(collusion_w3)
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    tx_hex = send_raw_transaction(from_account, conf.PRIVATE_KEY, send_address, collusion_w3,
                                  value=2000000000000000000000,
                                  data="test transaction,dsa，线程")
    eth.waitForTransactionReceipt(tx_hex)
    tx_hex = send_raw_transaction(send_address, send_privatekey, from_account, collusion_w3,
                                  value=1000000000000000000000,
                                  data="test transaction")
    eth.waitForTransactionReceipt(tx_hex)


def test_consensus_unlock_sendtransaction():
    '''
    共识节点unlock转账
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    nocollusion_w3 = connect_web3(nocollusion_list[0]["url"])
    eth = Eth(collusion_w3)
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    # 非共识节点新建一个钱包
    new_account = nocollusion_w3.personal.newAccount(conf.PASSWORD)
    time.sleep(2)
    to_account = collusion_w3.toChecksumAddress(new_account)
    before_value = eth.getBalance(to_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    # 共识节点转账给非共识节点新建的钱包
    tx_hash = transaction(collusion_w3, from_account, to_account)
    transaction_hash = HexBytes(tx_hash).hex()
    try:
        result = eth.waitForTransactionReceipt(transaction_hash)
    except:
        assert False, '等待超时，交易哈希：{}'.format(transaction_hash)
    after_value = eth.getBalance(to_account)
    assert result is not None, '交易在pending，未上链'
    assert after_value - before_value == 1000000000000000000000, '交易失败，转账金额未到账'


def test_non_consensus_unlock_sendtransaction():
    '''
    非共识节点unlock账号转账
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    nocollusion_w3 = connect_web3(nocollusion_list[0]["url"])
    eth = Eth(nocollusion_w3)
    # 共识节点新建钱包
    new_account = collusion_w3.personal.newAccount(conf.PASSWORD)
    to_account = collusion_w3.toChecksumAddress(new_account)
    before_value = eth.getBalance(to_account)
    from_count = nocollusion_w3.toChecksumAddress(conf.ADDRESS)
    nocollusion_w3.personal.unlockAccount(from_count, conf.PASSWORD, 666666)
    # 非共识节点转账给共识节点新建的钱包
    tx_hash = transaction(nocollusion_w3, from_count, to_account, value=100)
    transaction_hash = HexBytes(tx_hash).hex()
    try:
        result = eth.waitForTransactionReceipt(transaction_hash)
    except:
        assert False, '等待超时，交易哈希：{}--块高：{}'.format(transaction_hash, nocollusion_w3.eth.blockNumber)
    after_value = eth.getBalance(to_account)
    assert result is not None, '交易在pending，交易转发失败'
    assert after_value - before_value == 100, '交易失败，转账金额未到账'


def test_new_account_transaction():
    '''
    新建账号存在余额后转账给其他账号
    '''
    nocollusion_w3 = connect_web3(nocollusion_list[0]["url"])
    eth = Eth(nocollusion_w3)
    # 先给新账户存钱
    new_account = nocollusion_w3.toChecksumAddress(
        nocollusion_w3.personal.newAccount(conf.PASSWORD))
    from_account = nocollusion_w3.toChecksumAddress(
        conf.ADDRESS)
    nocollusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    trans_hex = transaction(nocollusion_w3, from_account, new_account)
    eth.waitForTransactionReceipt(HexBytes(trans_hex).hex())
    # 新账户把钱转给其他账户
    new_account2 = nocollusion_w3.toChecksumAddress(
        nocollusion_w3.personal.newAccount(conf.PASSWORD))
    before_value = eth.getBalance(new_account2)
    nocollusion_w3.personal.unlockAccount(new_account, conf.PASSWORD, 666666)
    trans_hex2 = transaction(
        nocollusion_w3, new_account, new_account2, value=100)
    eth.waitForTransactionReceipt(HexBytes(trans_hex2).hex())
    after_value = eth.getBalance(new_account2)
    assert after_value - before_value == 100, '交易失败，转账金额未到账'


def test_money_minus_transaction():
    '''
    转账金额为负数，交易预期失败
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    new_account = collusion_w3.personal.newAccount(conf.PASSWORD)
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    to_account = collusion_w3.toChecksumAddress(new_account)
    before_value = collusion_w3.eth.getBalance(to_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    status = 0
    try:
        transaction(collusion_w3, from_account, to_account, value=-100)
    except:
        status = 1
    assert status == 1, '转账金额为负数预期结果交易失败，实际结果出现异常'
    after_value = collusion_w3.eth.getBalance(to_account)
    assert after_value - before_value == 0, '转账金额为负数，预期结果交易失败未转账，实际结果异常'


def test_balance_empty_transaction():
    '''
    余额为0，转账失败
    :return:
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    new_account = collusion_w3.personal.newAccount(conf.PASSWORD)
    from_account = collusion_w3.toChecksumAddress(new_account)
    to_account = collusion_w3.toChecksumAddress(collusion_w3.eth.accounts[0])
    before_value = collusion_w3.eth.getBalance(to_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    status = 0
    try:
        transaction(collusion_w3, from_account, to_account)
    except:
        status = 1
    assert status == 1, '余额为0预期结果交易失败，实际结果出现异常'
    after_value = collusion_w3.eth.getBalance(to_account)
    assert after_value - before_value == 0, '余额为0，预期结果钱包未到账，实际结果异常'


def test_money_insufficient_transaction():
    '''
    余额不足，转账失败
    :return:
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    new_account = collusion_w3.personal.newAccount(conf.PASSWORD)
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    to_account = collusion_w3.toChecksumAddress(new_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    # 先给新建的钱包充钱1000000000000000000000
    transaction(collusion_w3, from_account, to_account)
    # 新建另一个钱包
    new_account_ = collusion_w3.toChecksumAddress(
        collusion_w3.personal.newAccount(conf.PASSWORD))
    before_value = collusion_w3.eth.getBalance(to_account)
    status = 0
    try:
        # 转账到新的钱包，金额大于余额，应报异常
        transaction(collusion_w3, to_account, new_account_,
                    value=9000000000000000000000000000)
    except:
        status = 1
    assert status == 1, '余额不足预期结果交易失败，实际结果出现异常'
    after_value = collusion_w3.eth.getBalance(to_account)
    assert after_value - before_value == 0, '余额不足，预期结果钱未转出去，实际结果异常'


def test_gas_insufficient_transaction():
    '''
    gas 值不足，转账失败
    :return:
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    new_account = collusion_w3.personal.newAccount(conf.PASSWORD)
    to_account = collusion_w3.toChecksumAddress(new_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    before_value = collusion_w3.eth.getBalance(to_account)
    status = 0
    try:
        transaction(collusion_w3, from_account, to_account, gas=100)
    except:
        status = 1
    assert status == 1, 'gas值不足预期交易失败，实际结果出现异常'
    after_value = collusion_w3.eth.getBalance(to_account)
    assert after_value - before_value == 0, 'gas值不足，预期结果钱未到账，实际结果异常'


def test_wallet_not_on_chain():
    ''''
    转账给不在一条链上的钱包，能转账成功
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    eth = Eth(collusion_w3)
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    to_account = collusion_w3.toChecksumAddress(
        '0x2fd96b410e4472a687fc1a872ef70abbb658bb9a')
    before_value = collusion_w3.eth.getBalance(to_account)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    tx_hash = transaction(collusion_w3, from_account, to_account)
    transaction_hash = HexBytes(tx_hash).hex()
    try:
        result = eth.waitForTransactionReceipt(transaction_hash)
    except:
        assert False, '等待超时，交易哈希：{}'.format(transaction_hash)
    after_value = eth.getBalance(to_account)
    assert result is not None, '交易在pending，未上链'
    assert after_value - before_value == 1000000000000000000000, '交易失败，转账金额未到账'


def test_to_account_is_empty():
    '''
    to账号为空，转账失败
    :return:
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
    status = 0
    try:
        transaction(collusion_w3, from_account)
    except:
        status = 1
    assert status == 1, 'to账号为空预期转账不成功，实际结果出现异常'


def test_illegal_account_transaction():
    '''
    to账号为非法
    :return:
    '''
    collusion_w3 = connect_web3(collusion_list[0]["url"])
    from_account = collusion_w3.toChecksumAddress(conf.ADDRESS)
    status = 0
    try:
        to_account = collusion_w3.toChecksumAddress(
            'efcdefcvcswavsddrvfvgewvge0544646464')
        collusion_w3.personal.unlockAccount(from_account, conf.PASSWORD, 666666)
        transaction(collusion_w3, from_account, to_account)
    except:
        status = 1
    assert status == 1, 'to账号为非法预期转账不成功，实际结果出现异常'

#
# def test_up_and_stop():
#     """
#     节点启停
#     :return:
#     """
#     auto = AutoDeployPlaton()
#     if len(collusion_list) > 7:
#         i = random.randrange(1, f - 2)
#         new_collusion = random.sample(collusion_list[10:], i)
#         auto.kill_of_list(new_collusion)
#         time.sleep(i * 10)
#         auto.start_of_list(collusion_list=new_collusion, nocollusion_list=None, is_need_init=False,
#                            clean=False)
