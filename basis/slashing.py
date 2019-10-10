import rlp
from basis.ppos import Ppos


class Slashing(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def ReportMutiSign(self, typ, data, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        举报双签
        :param data: string
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000004"

        data_ = rlp.encode([rlp.encode(int(3000)), rlp.encode(int(typ)), rlp.encode(data)])
        result = self.send_raw_transaction(data_, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def CheckMutiSign(self, typ, addr, blockNumber):
        '''
        查询节点是否已被举报过多签
        :param typ: uint8(1byte)
        :param addr: 20bytes
        :param blockNumber:
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000004"

        if addr[:2] == '0x':
            addr = addr[2:]

        data = rlp.encode([rlp.encode(int(3001)), rlp.encode(int(typ)),
                           rlp.encode(bytes.fromhex(addr)), rlp.encode(blockNumber)])
        recive = self.call_result(self.address, to_address, data, "ISO-8859-1")
        print(recive)
        return recive
