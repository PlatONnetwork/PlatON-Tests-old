from common.load_file import LoadFile
from common.log import log
from client_sdk_python.eth import Eth
from hexbytes import HexBytes
import random


class Account:
    def __init__(self, accountFile, chainId):
        '''
        accounts 包含的属性: address,prikey,nonce,balance
        '''
        self.accounts = {}
        accounts = LoadFile(accountFile).get_data()
        log.info(accounts)
        self.chain_id = chainId
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
        return random.choice(self.accounts.values())

    def sendTransaction(self, connect, data, from_address, to_address, gasPrice, gas, value):
        account = self.accounts[from_address]
        transaction_dict = {
            "to": to_address,
            "gasPrice": gasPrice,
            "gas": gas,
            "nonce": account['nonce'],
            "data": data,
            "chainId": self.chain_id,
            "value": value
        }
        platon = Eth(connect)
        signedTransactionDict = platon.account.signTransaction(
            transaction_dict, account['prikey']
        )

        data = signedTransactionDict.rawTransaction
        result = HexBytes(platon.sendRawTransaction(data)).hex()
        res = platon.waitForTransactionReceipt(result)
        return res
