import time
import rlp
from common.log import log
from tests.lib import get_the_dynamic_parameter_gas_fee


def test_1769_call_return_32000(client_consensus):
    client = client_consensus
    address = client.economic.account.account_with_money['address']
    for i in range(1000):
        nonce = client.node.eth.getTransactionCount(address)
        log.info(f'nonce: {nonce}')
        assert type(nonce) is int

    for i in range(1000):
        balance = client.node.eth.getBalance(address)
        log.info(f'balance: {balance}')
        assert type(balance) is int


def test_1758_estimate_pip_without_gas_price(client_consensus):
    client = client_consensus
    pip = client.pip
    pip_id = str(time.time())
    data = rlp.encode([rlp.encode(int(2000)), rlp.encode(bytes.fromhex(pip.node.node_id)), rlp.encode(pip_id)])
    expect_gas = 350000 + get_the_dynamic_parameter_gas_fee(data)
    log.info(f'expect_gas is: {expect_gas}')
    # 使用处于门槛金额的地址去预估gas
    txn = {"to": client.pip.pip.pipAddress, "data": data}
    estimated_gas = client.node.eth.estimateGas(txn)
    log.info(f'estimated_gas is: {estimated_gas}')
    assert expect_gas == estimated_gas
