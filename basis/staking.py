import rlp
from hexbytes import HexBytes
from basis.ppos import Ppos


class Staking(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def createStaking(self, typ, benifitAddress, nodeId, externalId, nodeName, website, details, amount, programVersion,
                      programVersionSign, blsPubKey, blsProof, privatekey=None, from_address=None, gasPrice=None,
                      gas=None):
        '''
        createStaking ：发起质押
        :param typ:  uint16(2bytes)
        :param benifitAddress:  20bytes
        :param nodeId: 64bytes
        :param externalId:  string
        :param nodeName: string
        :param website: string
        :param details: string
        :param amount: *big.Int(bytes)
        :param programVersion: uint32
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
            Ret: bool
            data:[]
            ErrMsg: string
        '''
        to_address = "0x1000000000000000000000000000000000000002"
        if benifitAddress[:2] == '0x':
            benifitAddress = benifitAddress[2:]
        if programVersionSign[:2] == '0x':
            programVersionSign = programVersionSign[2:]
            data = HexBytes(rlp.encode([rlp.encode(int(1000)),
                                        rlp.encode(int(typ)),
                                        rlp.encode(bytes.fromhex(benifitAddress)),
                                        rlp.encode(bytes.fromhex(nodeId)),
                                        rlp.encode(externalId), rlp.encode(nodeName), rlp.encode(website),
                                        rlp.encode(details), rlp.encode(self.web3.toWei(amount, 'ether')),
                                        rlp.encode(programVersion),
                                        rlp.encode(bytes.fromhex(programVersionSign)),
                                        rlp.encode(bytes.fromhex(blsPubKey)),
                                        rlp.encode(bytes.fromhex(blsProof))])).hex()
            result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
            return self.get_result(result)

    def updateStakingInfo(self, benifitAddress, nodeId, externalId, nodeName, website, details, privatekey=None,
                          from_address=None, gasPrice=None, gas=None):
        '''
        Description : 修改质押信息
        :param benifitAddress: 20bytes
        :param nodeId:  64bytes
        :param externalId:  string
        :param nodeName:  string
        :param website: string
        :param details: string
        :param from_address: string
        :param gasPrice:
        :param gas:
        :return:
            Ret: bool
            data:[]
            ErrMsg: string

        '''
        to_address = "0x1000000000000000000000000000000000000002"
        if benifitAddress[:2] == '0x':
            benifitAddress = benifitAddress[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1001)),
                                    rlp.encode(bytes.fromhex(benifitAddress)),
                                    rlp.encode(bytes.fromhex(nodeId)),
                                    rlp.encode(externalId), rlp.encode(nodeName), rlp.encode(website),
                                    rlp.encode(details)])).hex()

        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def addStaking(self, nodeId, typ, amount, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        Description : 增持质押
        :param nodeId: 64bytes
        :param typ: uint16(2bytes)
        :param amount:  *big.Int(bytes)
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
            Ret: bool
            data:[]
            ErrMsg: string
        '''
        to_address = "0x1000000000000000000000000000000000000002"
        data = HexBytes(rlp.encode([rlp.encode(int(1002)),
                                    rlp.encode(bytes.fromhex(nodeId)),
                                    rlp.encode(int(typ)),
                                    rlp.encode(self.web3.toWei(amount, 'ether'))])).hex()
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def unStaking(self, nodeId, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        Description : 撤销质押
        :param nodeId: 64bytes
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
            Ret: bool
            data:[]
            ErrMsg: string
        '''
        to_address = "0x1000000000000000000000000000000000000002"
        data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(nodeId))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)
