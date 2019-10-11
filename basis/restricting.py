import rlp
import json
from basis.ppos import Ppos


class Restricting(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def CreateRestrictingPlan(self, account, plan, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        创建锁仓计划
        :param account: 20bytes
        :param plan: []RestrictingPlan
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000001"
        if account[:2] == '0x':
            account = account[2:]
        plan_list = []
        for dict_ in plan:
            v = [dict_[k] for k in dict_]
            plan_list.append(v)
        rlp_list = rlp.encode(plan_list)
        data = rlp.encode([rlp.encode(int(4000)),
                           rlp.encode(bytes.fromhex(account)),
                           rlp_list])
        # print ("len:", len (data))
        # l = [hex (int (i)) for i in data]
        # print (" ".join (l))
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def GetRestrictingInfo(self, account):
        '''
        获取锁仓信息
        :param account: 20bytes
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if account[:2] == '0x':
            account = account[2:]
        data = rlp.encode([rlp.encode(int(4100)), rlp.encode(bytes.fromhex(account))])
        to_address = "0x1000000000000000000000000000000000000001"
        recive = self.call_result(self.address, to_address, data, "ISO-8859-1")
        data = (recive["Data"])
        if data != "":
            data = json.loads(data)
            data["balance"] = int(data["balance"], 16)
            data["Pledge"] = int(data["Pledge"], 16)
            data["debt"] = int(data["debt"], 16)
            if data["plans"]:
                for i in data["plans"]:
                    i["amount"] = int(i["amount"], 16)
            recive["Data"] = data
        print(recive)
        return recive
