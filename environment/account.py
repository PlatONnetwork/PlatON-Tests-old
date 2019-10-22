from common.load_file import LoadFile
from common.log import log
from client_sdk_python.eth import Eth
from client_sdk_python.personal import Personal
from hexbytes import HexBytes
import random
from client_sdk_python import (
    Web3
)


class Account:
    def __init__(self, accountFile, chainId):
        '''
           accounts 包含的属性: address,prikey,nonce,balance,node_id,passwd
        '''
        self.accounts = {}
        accounts = LoadFile(accountFile).get_data()
        log.info(accounts)
        self.chain_id = chainId
        self.account_with_money = accounts[0]
        for account in accounts:
            self.accounts[account['address']] = account

    def get_all_accounts(self):
        accounts = []
        for account in self.accounts.values():
            accounts.append(account)
        return accounts

    def get_rand_account(self):
        # todo 实现随机
        # for account in self.accounts.values():
        #     return account
        return random.choice(list(self.accounts.values()))

    def sendTransaction(self, connect, data, from_address, to_address, gasPrice, gas, value):
        account = self.accounts[from_address]
        tmp_to_address = Web3.toChecksumAddress(to_address)
        tmp_from_address = Web3.toChecksumAddress(from_address)
        transaction_dict = {
            "to": tmp_to_address,
            "gasPrice": gasPrice,
            "gas": gas,
            "nonce": account['nonce'],
            "data": data,
            "chainId": self.chain_id,
            "value": value,
            'from': tmp_from_address,
        }
        platon = Eth(connect)

        signedTransactionDict = platon.account.signTransaction(
            transaction_dict, account['prikey']
        )

        data = signedTransactionDict.rawTransaction
        result = HexBytes(platon.sendRawTransaction(data)).hex()
        res = platon.waitForTransactionReceipt(result)
        account['nonce'] = account['nonce'] + 1
        self.accounts[from_address] = account
        return res

    def generate_account_in_node(self, node, passwd, balance=0):
        personal = Personal(node.web3)
        address = personal.newAccount(passwd)
        log.info(address)
        if balance > 0:
            self.sendTransaction(node.web3, '', self.account_with_money['address'], address, 40000, 40000, balance)
        account = {
            "node_id": node.node_id,
            "address": address,
            "nonce": 0,
            "balance": balance,
            "prikey": '',
            'passwd': passwd
        }
        self.accounts[address] = account
        return address

    def unlock_account(self, node, address):
        account = self.accounts[address]
        personal = Personal(node.web3)
        personal.unlockAccount(account['address'], account['passwd'])

    def get_rand_account_in_node(self, node):
        for account in self.accounts.values():
            if account['node_id'] == node.id:
                return account
        self.generate_account_in_node(node, '123456')
