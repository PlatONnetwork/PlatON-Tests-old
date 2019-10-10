import rlp
import json
from basis.ppos import Ppos


class Delegate(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def delegate(self, typ, nodeId, amount, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        Description :发起委托
        :param typ: uint16(2bytes)
        :param nodeId: 64bytes
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
        data = rlp.encode([rlp.encode(int(1004)),
                           rlp.encode(int(typ)),
                           rlp.encode(bytes.fromhex(nodeId)),
                           rlp.encode(self.web3.toWei(amount, 'ether'))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def unDelegate(self, stakingBlockNum, nodeId, amount, privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        Description :减持/撤销委托(全部减持就是撤销)
        :param stakingBlockNum: uint64(8bytes)
        :param nodeId: 64bytes
        :param amount: *big.Int(bytes)
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000002"
        data = rlp.encode([rlp.encode(int(1005)), rlp.encode(int(stakingBlockNum)),
                           rlp.encode(bytes.fromhex(nodeId)), rlp.encode(self.web3.toWei(amount, 'ether'))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def getDelegateListByAddr(self, addr):
        '''
        @getDelegateListByAddr: 查询当前账户地址所委托的节点的NodeID和质押Id
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Addr: 验证人节点的地址
            NodeId: 验证人的节点Id
            StakingBlockNum: 发起质押时的区块高度
        '''
        if addr[:2] == '0x':
            addr = addr[2:]
        data = rlp.encode([rlp.encode(int(1103)), rlp.encode(bytes.fromhex(addr))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.call_array_result(self.address, to_address, data)
        print(recive)
        return recive

    def getDelegateInfo(self, stakingBlockNum, delAddr, nodeId):
        '''
        @getDelegateInfo: 查询当前单个委托信息
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Addr: 验证人节点的地址
            NodeId: 验证人的节点Id
            StakingBlockNum: 发起质押时的区块高度
            DelegateEpoch: 最近一次对该候选人发起的委托时的结算周期
            Released: 发起委托账户的自由金额的锁定期委托的von
            ReleasedHes: 发起委托账户的自由金额的犹豫期委托的von
            RestrictingPlan: 发起委托账户的锁仓金额的锁定期委托的von
            RestrictingPlanHes :发起委托账户的锁仓金额的犹豫期委托的von
        '''
        if delAddr[:2] == '0x':
            delAddr = delAddr[2:]
        data = rlp.encode([rlp.encode(int(1104)), rlp.encode(stakingBlockNum),
                           rlp.encode(bytes.fromhex(delAddr)), rlp.encode(bytes.fromhex(nodeId))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.call_result(self.address, to_address, data)
        data = recive["Data"]
        if data != "":
            data = json.loads(recive["Data"])
            data["Released"] = int(data["Released"], 16)
            data["ReleasedHes"] = int(data["ReleasedHes"], 16)
            data["RestrictingPlan"] = int(data["RestrictingPlan"], 16)
            data["RestrictingPlanHes"] = int(data["RestrictingPlanHes"], 16)
            data["Reduction"] = int(data["Reduction"], 16)
            recive["Data"] = data
        return recive
