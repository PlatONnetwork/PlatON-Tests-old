import pytest
from client_sdk_python.eth import Eth
from client_sdk_python.main import Web3

from client_sdk_python.personal import Personal

from eth_utils import (
    is_boolean,
    is_bytes,
    is_checksum_address,
    is_dict,
    is_integer,
    is_list_like,
    is_same_address,
    is_string,
)
from hexbytes import HexBytes
from client_sdk_python.exceptions import (
    InvalidAddress,
)

from common.log import log


UNKNOWN_ADDRESS = '0xdEADBEeF00000000000000000000000000000000'
UNKNOWN_HASH = '0xdeadbeef00000000000000000000000000000000000000000000000000000000'




@pytest.fixture(scope="class")
def unlocked_account(global_test_env):
    env = global_test_env
    node = env.get_rand_node()
    address = env.account.generate_account_in_node(node, '123456', 10000)
    env.account.unlock_account(node, address)
    return {
        'address': address,
        'node': node
    }

@pytest.fixture(scope="class")
def platon_connect(global_test_env):
    env = global_test_env
    node = env.get_rand_node()
    return node.eth

@pytest.fixture(scope="class")
def block_with_txn(global_test_env):
    env = global_test_env
    node = env.get_rand_node()
    account = env.account.account_with_money
    res = env.account.sendTransaction(node.web3,'',account['address'],account['address'],21000,21000,10000)
    platon = Eth(node.web3)
    return platon.getBlock(res['blockNumber'])

@pytest.fixture(scope="class")
def empty_block(platon_connect):
    return platon_connect.getBlock(2)


# return block  with contract_address
@pytest.fixture(scope="class")
def block_with_txn_with_log(global_test_env):
    return

class TestPlaton():

    @pytest.mark.P0
    def test_getbalance(self, global_test_env,platon_connect):
        env = global_test_env
        account = env.account.get_rand_account()
        balance = platon_connect.getBalance(account['address'])
        assert balance == account['balance'], '账户余额相等'

    def test_BlockNumber(self, platon_connect):
        """
        测试platon.getBlockNumber()
        """
        block_number = platon_connect.blockNumber
        assert is_integer(block_number)
        assert block_number >= 0

    def test_ProtocolVersion(self, platon_connect):
        protocol_version = platon_connect.protocolVersion
        assert is_string(protocol_version)
        assert protocol_version.isdigit()

    def test_syncing(self, platon_connect):
        syncing = platon_connect.syncing
        assert is_boolean(syncing) or is_dict(syncing)
        if is_boolean(syncing):
            assert syncing is False
        elif is_dict(syncing):
            assert 'startingBlock' in syncing
            assert 'currentBlock' in syncing
            assert 'highestBlock' in syncing

            assert is_integer(syncing['startingBlock'])
            assert is_integer(syncing['currentBlock'])
            assert is_integer(syncing['highestBlock'])

    def test_gasPrice(self, platon_connect):
        gas_price = platon_connect.gasPrice
        assert is_integer(gas_price)
        assert gas_price > 0

    def test_accounts(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()

        platon = Eth(node.web3)

        accounts_before = platon.accounts
        i = 0
        while i<10:
            env.account.generate_account_in_node(node, '123456')
            i+=1
        accounts_after = platon.accounts

        assert is_list_like(accounts_after)
        assert len(accounts_after) == len(accounts_before)+10
        assert all((
            is_checksum_address(account)
            for account
            in accounts_after
        ))

    def test_getStorageAt(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        account = env.account.get_rand_account()
        platon = Eth(node.web3)

        storage = platon.getStorageAt(account['address'], 0)
        assert isinstance(storage, HexBytes)

    def test_getStorageAt_invalid_address(self, platon_connect):
        with pytest.raises(InvalidAddress):
            platon_connect.getStorageAt(UNKNOWN_ADDRESS.lower(), 0)

    def test_getTransactionCount(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.web3)
        transaction_count = platon.getTransactionCount(env.account.get_rand_account()['address'])
        assert is_integer(transaction_count)
        assert transaction_count >= 0

    def test_getTransactionCount_invalid_address(self, platon_connect):
        with pytest.raises(InvalidAddress):
            platon_connect.getTransactionCount(UNKNOWN_ADDRESS.lower())

    def test_getBlockTransactionCountByHash_empty_block(self, platon_connect,empty_block):
        transaction_count = platon_connect.getBlockTransactionCount(empty_block['hash'])
        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_platon_getBlockTransactionCountByNumber_empty_block(self, platon_connect,empty_block):
        transaction_count = platon_connect.getBlockTransactionCount(empty_block['number'])
        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_platon_getBlockTransactionCountByHash_block_with_txn(self, platon_connect, block_with_txn):
        transaction_count = platon_connect.getBlockTransactionCount(block_with_txn['hash'])
        assert is_integer(transaction_count)
        assert transaction_count >= 1

    def test_platon_getBlockTransactionCountByNumber_block_with_txn(self, platon_connect,block_with_txn):
        transaction_count = platon_connect.getBlockTransactionCount(block_with_txn['number'])
        assert is_integer(transaction_count)
        assert transaction_count >= 1

    # def test_eth_getCode(self, global_test_env):
    #     #todo 怎么创建合约
    #     env = global_test_env
    #     node = env.get_rand_node()
    #     platon = Eth(node.connect_node())
    #
    #     account = env.aacount.get_rand_account()
    #
    #     code = platon.getCode(account)
    #     assert isinstance(code, HexBytes)
    #     assert len(code) > 0
    #
    # def test_eth_getCode_invalid_address(self, global_test_env):
    #     env = global_test_env
    #     node = env.get_rand_node()
    #     platon = Eth(node.connect_node())
    #     with pytest.raises(InvalidAddress):
    #         platon.getCode(UNKNOWN_ADDRESS)

    # def test_eth_getCode_with_block_identifier(self, global_test_env):
    #     #code = web3.eth.getCode(emitter_contract.address, block_identifier=web3.eth.blockNumber)
    #     assert isinstance(code, HexBytes)
    #     assert len(code) > 0
    #
    def test_platon_sign(self, unlocked_account):

        platon = Eth(unlocked_account['node'].web3)

        signature = platon.sign(
            unlocked_account['address'], text='Message tö sign. Longer than hash!'
        )
        assert is_bytes(signature)
        assert len(signature) == 32 + 32 + 1

        # test other formats
        hexsign = platon.sign(
            unlocked_account['address'],
            hexstr='0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821'
        )
        assert hexsign == signature

        intsign = platon.sign(
            unlocked_account['address'],
            0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821
        )
        assert intsign == signature

        bytessign = platon.sign(
            unlocked_account['address'], b'Message t\xc3\xb6 sign. Longer than hash!'
        )
        assert bytessign == signature

        new_signature =platon.sign(
            unlocked_account['address'], text='different message is different'
        )
        assert new_signature != signature

    def test_platon_sendTransaction_addr_checksum_required(self, unlocked_account):

        platon = Eth(unlocked_account['node'].web3)


        address = unlocked_account['address'].lower()
        txn_params = {
            'from': address,
            'to': address,
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        with pytest.raises(InvalidAddress):
            invalid_params = dict(txn_params, **{'from':UNKNOWN_ADDRESS})
            platon.sendTransaction(invalid_params)

        with pytest.raises(InvalidAddress):
            invalid_params = dict(txn_params, **{'to': UNKNOWN_ADDRESS})
            platon.sendTransaction(invalid_params)

    def test_platon_sendTransaction(self, unlocked_account):

        platon = Eth(unlocked_account['node'].web3)

        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        txn_hash = platon.sendTransaction(txn_params)
        txn = platon.getTransaction(txn_hash)

        assert is_same_address(txn['from'], txn_params['from'])
        assert is_same_address(txn['to'], txn_params['to'])
        assert txn['value'] == 1
        assert txn['gas'] == 21000
        assert txn['gasPrice'] == txn_params['gasPrice']

    def test_platon_sendTransaction_with_nonce(self, unlocked_account):

        platon = Eth(unlocked_account['node'].web3)
        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            # Increased gas price to ensure transaction hash different from other tests
            'gasPrice': platon.gasPrice * 2,
            'nonce': platon.getTransactionCount(unlocked_account['address']),
        }
        txn_hash = platon.sendTransaction(txn_params)
        txn = platon.getTransaction(txn_hash)

        assert is_same_address(txn['from'], txn_params['from'])
        assert is_same_address(txn['to'], txn_params['to'])
        assert txn['value'] == 1
        assert txn['gas'] == 21000
        assert txn['gasPrice'] == txn_params['gasPrice']
        assert txn['nonce'] == txn_params['nonce']

    def test_platon_replaceTransaction(self, unlocked_account):

        platon = Eth(unlocked_account['node'].web3)

        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        txn_hash = platon.sendTransaction(txn_params)
        txn_params['gasPrice'] = platon.gasPrice * 2
        replace_txn_hash = platon.replaceTransaction(txn_hash, txn_params)
        replace_txn = platon.getTransaction(replace_txn_hash)

        assert is_same_address(replace_txn['from'], txn_params['from'])
        assert is_same_address(replace_txn['to'], txn_params['to'])
        assert replace_txn['value'] == 1
        assert replace_txn['gas'] == 21000
        assert replace_txn['gasPrice'] == txn_params['gasPrice']

    def test_platon_replaceTransaction_non_existing_transaction(self, unlocked_account):
        platon = Eth(unlocked_account['node'].web3)

        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        with pytest.raises(ValueError):
            platon.replaceTransaction(
                '0x98e8cc09b311583c5079fa600f6c2a3bea8611af168c52e4b60b5b243a441997',
                txn_params
            )

    # auto mine is enabled for this test
    def test_platon_replaceTransaction_already_mined(self, unlocked_account):

        platon = Eth(unlocked_account['mode'].web3)
        address = unlocked_account['address']

        txn_params = {
            'from': address,
            'to': address,
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        txn_hash = platon.sendTransaction(txn_params)

        txn_params['gasPrice'] = platon.gasPrice * 2
        with pytest.raises(ValueError):
            platon.replaceTransaction(txn_hash, txn_params)

    def test_platon_replaceTransaction_incorrect_nonce(self, unlocked_account):
        platon = Eth(unlocked_account['mode'].web3)
        address = unlocked_account['address']
        txn_params = {
            'from': address,
            'to': address,
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        txn_hash =platon.sendTransaction(txn_params)
        txn = platon.getTransaction(txn_hash)

        txn_params['gasPrice'] =platon.gasPrice * 2
        txn_params['nonce'] = txn['nonce'] + 1
        with pytest.raises(ValueError):
            platon.replaceTransaction(txn_hash, txn_params)

    def test_platon_replaceTransaction_gas_price_too_low(self, unlocked_account):
        platon = Eth(unlocked_account['mode'].web3)
        address = unlocked_account['address']
        txn_params = {
            'from': address,
            'to': address,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = platon.sendTransaction(txn_params)

        txn_params['gasPrice'] = 9
        with pytest.raises(ValueError):
            platon.replaceTransaction(txn_hash, txn_params)

    def test_platon_replaceTransaction_gas_price_defaulting_minimum(self, unlocked_account):
        platon = Eth(unlocked_account['mode'].web3)
        address = unlocked_account['address']
        txn_params = {
            'from': address,
            'to': address,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = platon.sendTransaction(txn_params)

        txn_params.pop('gasPrice')
        replace_txn_hash = platon.replaceTransaction(txn_hash, txn_params)
        replace_txn = platon.getTransaction(replace_txn_hash)

        # todo minimum gas price is what
        assert replace_txn['gasPrice'] == 11

    def test_platon_replaceTransaction_gas_price_defaulting_strategy_higher(self,unlocked_account):
        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        node = unlocked_account['node']
        platon = Eth(node.web3)

        txn_hash = platon.sendTransaction(txn_params)

        def higher_gas_price_strategy(web3, txn):
            return 20

        platon.setGasPriceStrategy(higher_gas_price_strategy)

        txn_params.pop('gasPrice')
        replace_txn_hash = platon.replaceTransaction(txn_hash, txn_params)
        replace_txn = platon.getTransaction(replace_txn_hash)
        assert replace_txn['gasPrice'] == 20  # Strategy provides higher gas price

    def test_platon_replaceTransaction_gas_price_defaulting_strategy_lower(self, unlocked_account):
        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        node = unlocked_account['node']
        platon = Eth(node.web3)
        txn_hash = platon.sendTransaction(txn_params)

        def lower_gas_price_strategy(web3, txn):
            return 5

        platon.setGasPriceStrategy(lower_gas_price_strategy)

        txn_params.pop('gasPrice')
        replace_txn_hash = platon.replaceTransaction(txn_hash, txn_params)
        replace_txn = platon.getTransaction(replace_txn_hash)
        # Strategy provices lower gas price - minimum preferred
        assert replace_txn['gasPrice'] == 11

    def test_platon_modifyTransaction(self,  unlocked_account):
        node = unlocked_account['node']
        platon = Eth(node.web3)
        txn_params = {
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        }
        txn_hash = platon.sendTransaction(txn_params)

        modified_txn_hash =platon.modifyTransaction(
            txn_hash, gasPrice=(txn_params['gasPrice'] * 2), value=2
        )
        modified_txn = platon.getTransaction(modified_txn_hash)

        assert is_same_address(modified_txn['from'], txn_params['from'])
        assert is_same_address(modified_txn['to'], txn_params['to'])
        assert modified_txn['value'] == 2
        assert modified_txn['gas'] == 21000
        assert modified_txn['gasPrice'] == txn_params['gasPrice'] * 2

    def test_platon_sendRawTransaction(self,global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        account = env.account.get_rand_account()
        transaction_dict = {
            "to": account['address'],
            "gasPrice": 2100,
            "gas": 100,
            "nonce": account['nonce'],
            "data": '',
            "chainId": global_test_env.account.chain_id,
            "value": 1
        }
        platon = Eth(node.web3)
        signedTransactionDict = platon.account.signTransaction(
            transaction_dict, account['prikey']
        )

        data = signedTransactionDict.rawTransaction


        txn_hash = platon.sendRawTransaction(data)

        web = Web3()

        assert txn_hash == web.toBytes(hexstr=signedTransactionDict.hash)

    # todo 合约调用
    # def test_platon_call(self, web3, math_contract):
    #     coinbase = web3.eth.coinbase
    #     txn_params = math_contract._prepare_transaction(
    #         fn_name='add',
    #         fn_args=(7, 11),
    #         transaction={'from': coinbase, 'to': math_contract.address},
    #     )
    #     call_result = web3.eth.call(txn_params)
    #     assert is_string(call_result)
    #     result = decode_single('uint256', call_result)
    #     assert result == 18

    # def test_eth_call_with_0_result(self, web3, math_contract):
    #     coinbase = web3.eth.coinbase
    #     txn_params = math_contract._prepare_transaction(
    #         fn_name='add',
    #         fn_args=(0, 0),
    #         transaction={'from': coinbase, 'to': math_contract.address},
    #     )
    #     call_result = web3.eth.call(txn_params)
    #     assert is_string(call_result)
    #     result = decode_single('uint256', call_result)
    #     assert result == 0

    def test_platon_estimateGas(self, unlocked_account):
        node = unlocked_account['node']
        platon = Eth(node.web3)

        gas_estimate = platon.estimateGas({
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
        })
        assert is_integer(gas_estimate)
        assert gas_estimate > 0

    def test_platon_getBlockByHash(self, platon_connect):
        empty_block = platon_connect.getBlock(1)

        block = platon_connect.getBlock(empty_block['hash'])
        assert block['hash'] == empty_block['hash']

    def test_platon_getBlockByHash_not_found(self, platon_connect):
        block =platon_connect.getBlock(UNKNOWN_HASH)
        assert block is None

    def test_platon_getBlockByNumber_with_integer(self, platon_connect):
        block = platon_connect.getBlock(1)
        assert block['number'] == 1

    def test_platon_getBlockByNumber_latest(self, platon_connect):
        block = platon_connect.getBlock('latest')
        assert block['number'] > 0

    def test_platon_getBlockByNumber_not_found(self, platon_connect):
        block = platon_connect.getBlock(123456789)
        assert block is None

    def test_platon_getBlockByNumber_pending(self, platon_connect):
        block = platon_connect.getBlock('pending')
        latest = platon_connect.getBlock('latest')

        assert block['number'] == latest['number'] + 1

    def test_platon_getBlockByNumber_earliest(self, platon_connect):
        genesis_block = platon_connect.getBlock(0)
        block = platon_connect.getBlock('earliest')
        assert block['number'] == 0
        assert block['hash'] == genesis_block['hash']

    # def test_platon_getBlockByNumber_full_transactions(self, platon_connect):
    #     block = platon_connect.getBlock(block_with_txn['number'], True)
    #     transaction = block['transactions'][0]
    #     assert transaction['hash'] == block_with_txn['transactions'][0]

    def test_platon_getTransactionByHash(self, global_test_env,platon_connect):
        account = global_test_env.account.get_rand_account()
        res = global_test_env.account.sendTransaction(platon_connect,'',account['address'],account['address'],21000,21000,1)

        transaction = platon_connect.getTransaction(res['hash'])
        assert is_dict(transaction)
        assert transaction['hash'] == res['hash']

    # def test_platon_getTransactionByHash_contract_creation(self,
    #                                                     web3,
    #                                                     math_contract_deploy_txn_hash):
    #     transaction = web3.eth.getTransaction(math_contract_deploy_txn_hash)
    #     assert is_dict(transaction)
    #     assert transaction['to'] is None, "to field is %r" % transaction['to']

    def test_platon_getTransactionFromBlockHashAndIndex(self, platon_connect):

        block = platon_connect.getBlock(1)

        transaction =platon_connect.getTransactionFromBlock(block['hash'], 0)
        assert is_dict(transaction)
        assert transaction['hash'] == HexBytes(block['hash'])

    def test_platon_getTransactionFromBlockNumberAndIndex(self,platon_connect):
        block = platon_connect.getBlock(1)
        transaction = platon_connect.getTransactionFromBlock(block['number'], 0)
        assert is_dict(transaction)
        assert transaction['hash'] == HexBytes(block['hash'])

    def test_platon_getTransactionReceipt_mined(self, platon_connect, block_with_txn):
        receipt = platon_connect.getTransactionReceipt(block_with_txn['hash'])
        assert is_dict(receipt)
        assert receipt['blockNumber'] == block_with_txn['number']
        assert receipt['blockHash'] == block_with_txn['hash']
        assert receipt['transactionIndex'] == 0
        assert receipt['transactionHash'] == HexBytes(block_with_txn['hash'])

    def test_platon_getTransactionReceipt_unmined(self, unlocked_account):

        platon = Eth(unlocked_account['node'].connect_node())

        txn_hash = platon.sendTransaction({
            'from': unlocked_account['address'],
            'to': unlocked_account['address'],
            'value': 1,
            'gas': 21000,
            'gasPrice': platon.gasPrice,
        })
        receipt = platon.getTransactionReceipt(txn_hash)
        assert receipt is None

    def test_eth_getTransactionReceipt_with_log_entry(self, platon_connect, block_with_txn_with_log):
        receipt = platon_connect.getTransactionReceipt(block_with_txn_with_log['hash'])
        assert is_dict(receipt)
        assert receipt['blockNumber'] == block_with_txn_with_log['number']
        assert receipt['blockHash'] == block_with_txn_with_log['hash']
        assert receipt['transactionIndex'] == 0
        assert receipt['transactionHash'] == HexBytes(block_with_txn_with_log['receiptsRoot'])

        assert len(receipt['logs']) == 1
        log_entry = receipt['logs'][0]

        assert log_entry['blockNumber'] == block_with_txn_with_log['number']
        assert log_entry['blockHash'] == block_with_txn_with_log['hash']
        assert log_entry['logIndex'] == 0
        assert is_same_address(log_entry['address'],  block_with_txn_with_log['contract_address'])
        assert log_entry['transactionIndex'] == 0
        assert log_entry['transactionHash'] == HexBytes(block_with_txn_with_log['transactionsRoot'])

















