import pytest
from client_sdk_python.eth import Eth

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

UNKNOWN_ADDRESS = '0xdEADBEeF00000000000000000000000000000000'


class TestPlaton():

    @pytest.mark.P0
    def test_getbalance(self, global_test_env):
        env = global_test_env
        platon = Eth(env.get_rand_node().connect_node())
        account = env.account.get_rand_account()
        balance = platon.getBalance(account['address'])
        assert balance == account.balance, '账户余额相等'
        with pytest.raises(InvalidAddress):
            platon.getBalance(env.Accounts.generateAccount().address)

    def test_BlockNumber(self, global_test_env):
        """
        测试platon.getBlockNumber()
        """
        env = global_test_env
        platon = Eth(env.get_rand_node().connect_node())
        block_number = platon.blockNumber()
        assert is_integer(block_number)
        assert block_number >= 0

    def test_ProtocolVersion(self, global_test_env):
        env = global_test_env
        platon = Eth(env.get_rand_node().connect_node())
        protocol_version = platon.protocolVersion()
        assert is_string(protocol_version)
        assert protocol_version.isdigit()

    def test_syncing(self, global_test_env):
        env = global_test_env
        platon = Eth(env.get_rand_node().connect_node())
        syncing = platon.syncing()
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

    def test_gasPrice(self, global_test_env):
        env = global_test_env
        platon = Eth(env.get_rand_node().connect_node())
        gas_price = platon.gasPrice()
        assert is_integer(gas_price)
        assert gas_price > 0

    def test_accounts(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())

        accounts_before = platon.accounts()
        node.aacount.generateAccount(node, 10)
        accounts_after = platon.accounts()

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

        account = env.aacount.generateAccount()
        platon = Eth(node.connect_node())

        storage = platon.getStorageAt(account, 0)
        assert isinstance(storage, HexBytes)

    def test_getStorageAt_invalid_address(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        with pytest.raises(InvalidAddress):
            platon.getStorageAt(UNKNOWN_ADDRESS.lower(), 0)

    def test_getTransactionCount(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        transaction_count = platon.getTransactionCount(env.account.get_rand_account())
        assert is_integer(transaction_count)
        assert transaction_count >= 0

    def test_getTransactionCount_invalid_address(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        with pytest.raises(InvalidAddress):
            platon.getTransactionCount(UNKNOWN_ADDRESS.lower())

    def test_getBlockTransactionCountByHash_empty_block(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        address = env.aacount.get_rand_account().address

        transaction_count = platon.getBlockTransactionCount(address)
        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_eth_getBlockTransactionCountByNumber_empty_block(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        number = env.aacount.get_rand_account().number
        transaction_count = platon.getBlockTransactionCount(number)
        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_eth_getBlockTransactionCountByHash_block_with_txn(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        aa = {}
        for account in env.aacount.get_accounts():
            if account.nonce > 0:
                aa = account
        transaction_count = platon.getBlockTransactionCount(aa.address)
        assert is_integer(transaction_count)
        assert transaction_count >= 1

    def test_eth_getBlockTransactionCountByNumber_block_with_txn(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        aa = {}
        for account in env.aacount.get_accounts():
            if account.nonce > 0:
                aa = account
        transaction_count = platon.getBlockTransactionCount(aa.address)
        assert is_integer(transaction_count)
        assert transaction_count >= 1

    # def test_eth_getCode(self, global_test_env):
    #     env = global_test_env
    #     node = env.get_rand_node()
    #     platon = Eth(node.connect_node())
    #
    #     account = env.aacount.get_rand_account()
    #
    #     code = platon.getCode(math_contract_address)
    #     assert isinstance(code, HexBytes)
    #     assert len(code) > 0

    def test_eth_getCode_invalid_address(self, global_test_env):
        env = global_test_env
        node = env.get_rand_node()
        platon = Eth(node.connect_node())
        with pytest.raises(InvalidAddress):
            platon.getCode(UNKNOWN_ADDRESS)

    # def test_eth_getCode_with_block_identifier(self, global_test_env):
    #     #code = web3.eth.getCode(emitter_contract.address, block_identifier=web3.eth.blockNumber)
    #     assert isinstance(code, HexBytes)
    #     assert len(code) > 0
    #
    # def test_eth_sign(self, global_test_env):
    #     env = global_test_env
    #     node = env.get_rand_node()
    #     platon = Eth(node.connect_node())
    #
    #
    #     account = env.account.generate_account()
    #
    #     env.send
    #
    #     signature = platon.sign(
    #         unlocked_account_dual_type, text='Message tö sign. Longer than hash!'
    #     )
    #     assert is_bytes(signature)
    #     assert len(signature) == 32 + 32 + 1
    #
    #     # test other formats
    #     hexsign = web3.eth.sign(
    #         unlocked_account_dual_type,
    #         hexstr='0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821'
    #     )
    #     assert hexsign == signature
    #
    #     intsign = web3.eth.sign(
    #         unlocked_account_dual_type,
    #         0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821
    #     )
    #     assert intsign == signature
    #
    #     bytessign = web3.eth.sign(
    #         unlocked_account_dual_type, b'Message t\xc3\xb6 sign. Longer than hash!'
    #     )
    #     assert bytessign == signature
    #
    #     new_signature = web3.eth.sign(
    #         unlocked_account_dual_type, text='different message is different'
    #     )
    #     assert new_signature != signature







