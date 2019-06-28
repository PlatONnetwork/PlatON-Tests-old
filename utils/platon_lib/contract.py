# -*- coding: UTF-8 -*-
import json
import struct
import time

import eth_keyfile
import rlp
from hexbytes import HexBytes
from web3.eth import Eth
from web3.personal import Personal

from common.connect import connect_web3
from utils.platon_lib import encoder
from utils.platon_lib.event import Event


def get_private_key(keystorePtah, password):
    """
    获取私钥
    :param keystorePtah: keystore钱包json文件路径
    :param password: 钱包密码
    :return:钱包私钥
    """
    privateKey = eth_keyfile.decode_keyfile_json(json.load(open(keystorePtah)), password)
    return privateKey.hex()


def get_byte_code(binFilePath):
    with open(binFilePath, "rb") as f:
        bytecode = bytearray(f.read())
        return bytecode


def get_abi_bytes(abiPath):
    with open(abiPath, "r") as a:
        abi = a.read()
        abi = abi.replace("\r\n", "")
        abi = abi.replace("\n", "")
    return bytearray(abi, encoding="utf-8")


def contract_call_result_decode(receive: bytes):
    if receive[:1] == int(255).to_bytes(1, 'big'):
        decoded_item = struct.unpack('iiiiiiii', receive[::-1])[0]
    else:
        decoded_item = int.from_bytes(receive, 'big')
    return decoded_item


class PlatonContractTransaction:
    """
    合约创建参数list结构：[txType,byteCode,abi]
    合约调用参数list结构：[txType,funcName,params01,params02,...]
    """

    def __init__(self, URL):
        self.URL = URL
        self.w3 = connect_web3(URL)
        self.eth = Eth(self.w3)
        self.personal = Personal(self.w3)
        for i in range(5):
            if self.w3.isConnected():
                break
            else:
                self.w3 = connect_web3(URL)
            time.sleep(1)
        else:
            raise Exception("节点连接失败")

    def reconnect(self):
        self.w3 = connect_web3(self.URL)
        self.eth = Eth(self.w3)
        self.personal = Personal(self.w3)

    def get_signed_data(self, fromAddress, toAddress, dataList, privateKey):
        myNonce = self.eth.getTransactionCount(fromAddress)
        data = rlp.encode(dataList)
        transactionDict = {
            "from": fromAddress,
            "to": toAddress,
            "gasPrice": "0x8250de00",
            "gas": "0x6fffffff",  # rule of thumb / guess work
            "nonce": myNonce,
            "data": data,
        }
        signedTransactionDict = self.eth.account.signTransaction(
            transactionDict, privateKey
        )
        return signedTransactionDict.rawTransaction

    def contract_deploy(self, bytecode, abi, fromAddress):
        """
        非签名合约部署
        :param txType:取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
        :param bytecode:合约bin(wasm文件)，二进制数组
        :param abi:abi(json文件)，二进制数组
        :param fromAddress:钱包地址
        :return:合约部署transactionHash
        """
        txType = encoder.encode_type(1)
        bytecode = bytecode
        abi = abi
        rlpList = [txType, bytecode, abi]
        data = rlp.encode(rlpList)
        transactionHash = self.eth.sendTransaction(
            {
                "from": fromAddress,
                "gas": "0x6fffffff",
                "gasPrice": "0x8250de00",
                "data": data,
            }
        )
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def contract_transaction(self, fromAddress, contractAddress, dataList):
        """
        非签名合约交易
        :param fromAddress: 钱包地址
        :param contractAddress: 合约地址
        :param dataList: 参数list
        :return:合约交易transactionHash
        """
        data = rlp.encode(dataList)
        transactionHash = self.eth.sendTransaction(
            {
                "from": fromAddress,
                "to": contractAddress,
                "gas": "0x6fffffff",
                "gasPrice": "0x8250de00",
                "data": data,
            }
        )
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def contract_call(self, fromAddress, contractAddress, dataList):
        """
        合约查询交易
        :param fromAddress:钱包地址
        :param contractAddress:合约地址
        :param dataList:参数list
        :return:
        """
        data = rlp.encode(dataList)
        recive = self.eth.call(
            {"from": fromAddress, "to": contractAddress, "data": data}
        )
        return recive

    def signed_contract_deploy(self, bytecode, abi, fromAddress, privateKey):
        """
        签名部署合约
        :param txType:取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
        :param bytecode:bytecode，二进制数组
        :param abi:abi，二进制数组
        :param fromAddress:钱包地址
        :param privateKey:钱包私钥
        :return:transactionHash
        """
        txType = encoder.encode_type(1)
        bytecode = bytecode
        abi = abi
        rlpList = [txType, bytecode, abi]
        signedData = self.get_signed_data(fromAddress, "", rlpList, privateKey)
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def signed_contract_transaction(
            self, fromAddress, contractAddress, dataList, privateKey
    ):
        """
        签名合约交易
        :param fromAddress:钱包地址
        :param contractAddress:合约地址
        :param dataList:参数list
        :param privateKey:钱包私钥
        :return:transactionHash
        """
        signedData = self.get_signed_data(
            fromAddress, contractAddress, dataList, privateKey
        )
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def contract_call_string(self, fromAddress, contractAddress, dataList):
        result = self.contract_call(fromAddress, contractAddress, dataList)
        length = int(result[66:130], 16)*2
        data = result[130:130+length]
        ret = HexBytes(data).decode()
        return ret.lower()

if __name__ == "__main__":
    """初始化web3"""
    wt = PlatonContractTransaction('http://192.168.9.175:6789')
    # wt = PlatonContractTransaction('http://10.10.8.20:8545')
    # wt = PlatonContractTransaction('http://10.10.8.170:6789')
    addrress = wt.w3.toChecksumAddress('0x493301712671ada506ba6ca7891f436d29185821')
    wt.w3.personal.unlockAccount(addrress, '88888888', 99999999)
    """部署合约"""
    resp = wt.contract_deploy(1,
                              get_byte_code(r'D:\workspace\CTest\Platon-contract\build\user\inputtest\inputtest.wasm'),
                              get_abi_bytes(
                                  r'D:\workspace\CTest\Platon-contract\build\user\inputtest\inputtest.cpp.abi.json'),
                              addrress)
    result = wt.eth.waitForTransactionReceipt(resp)
    contractAddress = result['contractAddress']
    print(contractAddress)
    """发送交易"""
    # contractAddress = '0x6c54DD7c43bc1EC156b6aA684A61610a9ec967A9'
    dataList = [encoder.encode_type(2), encoder.encode_string('set'),
                encoder.encode_int('int64', 100)]
    transResp = wt.contract_transaction(addrress, contractAddress, dataList)
    result = wt.w3.eth.waitForTransactionReceipt(transResp)
    print(result)
    """查看eventData"""
    topics = result['logs'][0]['topics']
    print(topics)
    data = result['logs'][0]['data']
    print(data)
    event = Event(json.load(open(r'D:\workspace\CTest\Platon-contract\build\user\inputtest\inputtest.cpp.abi.json')))
    eventData = event.event_data(topics, data)
    print(eventData)
    """call方法查询交易"""
    # contractAddress = '0x43355C787c50b647C425f594b441D4BD751951C1'
    dataList = [encoder.encode_type(2), encoder.encode_string('get')]
    recive = wt.contract_call(addrress, contractAddress, dataList)
    print(int.from_bytes(recive, 'big'))
