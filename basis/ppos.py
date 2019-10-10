import json
import rlp
from common import log
from hexbytes import HexBytes
from client_sdk_python.eth import Eth
from client_sdk_python import (
    Web3,
)


class Ppos:
    def __init__(self, web3, address, chain_id, private_key, gas, gas_price):
        self.web3 = web3
        self.eth = Eth(self.web3)
        self.address = Web3.toChecksumAddress(address)
        if chain_id is not None:
            self.chain_id = chain_id
        else:
            # 默认链ID
            self.chain_id = conf.CHAIN_ID
        if private_key is not None:
            self.private_key = private_key
        else:
            # 默认私钥
            self.private_key = conf.PRIVATE_KEY
        if gas is not None:
            self.gas = gas
        else:
            # 默认gas数量
            self.gas = conf.GAS
        if gas_price is not None:
            self.gas_price = gas_price
        else:
            # 默认gas_price
            self.gas_price = conf.GAS_PRICE

    def get_result(self, tx_hash):
        log.info('交易hash为{}'.format(tx_hash))
        result = self.eth.waitForTransactionReceipt(tx_hash)
        """查看eventData"""
        data = result['logs'][0]['data']
        if data[:2] == '0x':
            data = data[2:]
        data_bytes = rlp.decode(bytes.fromhex(data))[0]
        event_data = bytes.decode(data_bytes)
        event_data = json.loads(event_data)
        print(event_data)
        return event_data

    def call(self, from_address, to_address, data):
        result = self.eth.call({
            "from": from_address,
            "to": to_address,
            "data": data
        })
        return result

    def call_result(self, from_address, to_address, data, encoding="utf8"):
        result = str(self.call(from_address, to_address, data), encoding)
        result = json.loads(result)
        return result

    def call_array_result(self, from_address, to_address, data, encoding="utf8"):
        result = str(self.call(from_address, to_address, data), encoding)
        result = result.replace('\\', '').replace('"[', '[').replace(']"', ']')
        result = json.loads(result)
        return result

    def call_object_result(self, from_address, to_address, data, encoding="utf8"):
        result = str(self.call(from_address, to_address, data), encoding)
        result = result.replace('\\', '').replace('"{', '{').replace('}"', '}')
        result = json.loads(result)
        return result

    def send_raw_transaction(self, data, from_address, to_address, gas_price=None, gas=None, value=0, private_key=None):
        if not from_address:
            from_address = self.address
        if not private_key:
            private_key = self.private_key
        if not gas_price:
            gas_price = self.gas_price
            log.info("gas价格:{}".format(gas_price))
        if not gas:
            transaction_dict = {"to": to_address, "data": data}
            gas = self.eth.estimateGas(transaction_dict)
            log.info("发起交易的gas费用：{}".format(gas))
        nonce = self.eth.getTransactionCount(from_address)
        transaction_dict = {
            "to": to_address,
            "gasPrice": gas_price,
            "gas": gas,
            "nonce": nonce,
            "data": data,
            "chainId": self.chain_id
        }
        if value > 0:
            transaction_dict["value"] = self.web3.toWei(value, "ether")
        signed_transaction_dict = self.eth.account.signTransaction(
            transaction_dict, private_key
        )
        data = signed_transaction_dict.rawTransaction
        return HexBytes(self.eth.sendRawTransaction(data)).hex()
