# -*- coding: utf-8 -*-

import json
import re
import math
import rlp
from hexbytes import HexBytes
from client_sdk_python.eth import Eth
from conf import setting as conf
from common.connect import connect_web3
from client_sdk_python import (
    Web3,
)

def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number
    else:
        return total_time - number + i

class Ppos:
    def __init__(self, url, address, password,
                 privatekey=conf.PRIVATE_KEY):
        self.web3 = connect_web3(url)
        if not self.web3.isConnected():
            raise Exception("node connection failed")
        self.eth = Eth(self.web3)
        self.address = Web3.toChecksumAddress(address)
        self.privatekey = privatekey
        self.gasPrice = "0x8250de00"
        self.gas = "0x6fffffff"

    def get_result(self, tx_hash, func_name):
        result = self.eth.waitForTransactionReceipt(tx_hash)
        print(result)
        """查看eventData"""
        data = result['logs'][0]['data']
        if data[:2] == '0x':
            data = data[2:]
        # print(data)
        data_bytes = rlp.decode(bytes.fromhex(data))[0]
        event_data = (bytes.decode(data_bytes))
        return func_name ,event_data

    def send_raw_transaction(self, data, from_address, to_address, gasPrice, gas,value):
        nonce = self.eth.getTransactionCount(from_address)
        if value > 0:
            transaction_dict = {
                "to": to_address,
                "gasPrice": gasPrice,
                "gas": gas,
                "nonce": nonce,
                "data": data,
                "chainId": 102,
                "value": self.web3.toWei(value, "ether"),
            }
        else:
            transaction_dict = {
                "to": to_address,
                "gasPrice": gasPrice,
                "gas": gas,
                "nonce": nonce,
                "data": data,
                "chainId": 102
            }
        signedTransactionDict = self.eth.account.signTransaction(
            transaction_dict, self.privatekey
        )
        data = signedTransactionDict.rawTransaction
        result = HexBytes(self.eth.sendRawTransaction(data)).hex()
        return result

    def staking(self, typ, benifitAddress, nodeId,externalId, nodeName, website, details, amount,processVersion,
                from_address=None, gasPrice=None , gas=None):
        '''
        Description ：发起质押
        :param typ:  uint16(2bytes)
        :param benifitAddress:  20bytes
        :param nodeId: 64bytes
        :param externalId:  string
        :param nodeName: string
        :param website: string
        :param details: string
        :param amount: *big.Int(bytes)
        :param processVersion: uint32
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
            Ret: bool
            data:[]
            ErrMsg: string
        '''
        if benifitAddress[:2] == '0x':
            benifitAddress = benifitAddress[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1000)),
                                    rlp.encode(int(typ)),
                                    rlp.encode(bytes.fromhex(benifitAddress)),
                                    rlp.encode(bytes.fromhex(nodeId)),
                                    rlp.encode(externalId), rlp.encode(nodeName), rlp.encode(website),
                                    rlp.encode(details),rlp.encode(self.web3.toWei(amount, 'ether')),
                                    rlp.encode(processVersion)])).hex()
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice,gas,amount)
        print(result)
        return self.get_result(result, self.staking.__name__)

    def updateStakingInfo(self, benifitAddress, nodeId,externalId, nodeName, website, details,
                from_address=None, gasPrice=None , gas=None):
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
        if benifitAddress[:2] == '0x':
            benifitAddress = benifitAddress[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1001)),
                                    rlp.encode(bytes.fromhex(benifitAddress)),
                                    rlp.encode(bytes.fromhex(nodeId)),
                                    rlp.encode(externalId), rlp.encode(nodeName), rlp.encode(website),
                                    rlp.encode(details)])).hex()
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice,gas,value=0)
        return self.get_result(result, self.updateStakingInfo.__name__)

    def addStaking(self,nodeId,typ,amount,from_address=None, gasPrice=None , gas=None):
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
        data = HexBytes(rlp.encode([rlp.encode(int(1002)),
                                    rlp.encode(bytes.fromhex(nodeId)),
                                    rlp.encode(int(typ)),
                                    rlp.encode(self.web3.toWei(amount, 'ether'))])).hex()
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address,gasPrice, gas,value=0)
        return self.get_result(result, self.addStaking.__name__)

    def unStaking(self,nodeId,from_address=None, gasPrice=None , gas=None):
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
        data = rlp.encode([rlp.encode(int(1003)),rlp.encode(bytes.fromhex(nodeId))])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address,gasPrice, gas,value=0)
        return self.get_result(result, self.unStaking.__name__)

    def delegate(self,typ,nodeId,amount,from_address=None, gasPrice=None , gas=None):
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
        data = rlp.encode([rlp.encode(int(1004)),
                           rlp.encode(int(typ)),
                           rlp.encode(bytes.fromhex(nodeId)),
                           rlp.encode(self.web3.toWei(amount, 'ether'))])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address,gasPrice, gas,value=0)
        return self.get_result(result, self.delegate.__name__)

    def unDelegate(self,stakingBlockNum,nodeId,amount,from_address=None, gasPrice=None , gas=None):
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
        data = rlp.encode([rlp.encode(int(1005)),rlp.encode(int(stakingBlockNum)),
                           rlp.encode(bytes.fromhex(nodeId)),rlp.encode(self.web3.toWei(amount, 'ether'))])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000002"
        result = self.send_raw_transaction(data, from_address, to_address,gasPrice, gas,value=0)
        return self.get_result(result, self.unDelegate.__name__)

    def getVerifierList(self):
        '''
        @GetVerifierList: 查询当前结算周期的验证人队列
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'NodeId': 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenifitAddress: 用于接受出块奖励和质押奖励的收益账户
            StakingTxIndex: 发起质押时的交易索引
            ProcessVersion: 被质押节点的PlatON进程的真实版本号(获取版本号的接口由治理提供)
            StakingBlockNum: 发起质押时的区块高度
            Shares: 当前候选人总共质押加被委托的von数目
            ExternalId: 外部Id(有长度限制，给第三方拉取节点描述的Id)
            NodeName: 被质押节点的名称(有长度限制，表示该节点的名称)
            Website: 节点的第三方主页(有长度限制，表示该节点的主页)
            Details: 节点的描述(有长度限制，表示该节点的描述)
            ValidatorTerm: 验证人的任期(在结算周期的101个验证人快照中永远是0，只有备选为下一共识轮验证人时才会被变更，刚被选出来时也是0，继续留任时则+1)
        '''
        data = rlp.encode([rlp.encode(int(1100))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = (self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        }))
        recive = str(recive,encoding="utf8")
        print(recive)
        # p = re.compile(r'{.*}')
        # recive = re.findall(p, recive)[0]
        # recive = re.sub("{{", "{", recive)
        # recive = json.loads(recive)
        return recive

    def getValidatorList(self):
        '''
           @GetVerifierList: 查询当前共识周期的验证人列表
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'NodeId': 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenifitAddress: 用于接受出块奖励和质押奖励的收益账户
            StakingTxIndex: 发起质押时的交易索引
            ProcessVersion: 被质押节点的PlatON进程的真实版本号(获取版本号的接口由治理提供)
            StakingBlockNum: 发起质押时的区块高度
            Shares: 当前候选人总共质押加被委托的von数目
            ExternalId: 外部Id(有长度限制，给第三方拉取节点描述的Id)
            NodeName: 被质押节点的名称(有长度限制，表示该节点的名称)
            Website: 节点的第三方主页(有长度限制，表示该节点的主页)
            Details: 节点的描述(有长度限制，表示该节点的描述)
            ValidatorTerm: 验证人的任期(在结算周期的101个验证人快照中永远是0，只有备选为下一共识轮验证人时才会被变更，刚被选出来时也是0，继续留任时则+1)
        '''
        data = rlp.encode([rlp.encode(int(1101))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        print(recive)
        return recive

    def getCandidateList(self):
        '''
        @GetVerifierList: 查询所有实时的候选人列表
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'NodeId': 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenifitAddress: 用于接受出块奖励和质押奖励的收益账户
            StakingTxIndex: 发起质押时的交易索引
            ProcessVersion: 被质押节点的PlatON进程的真实版本号(获取版本号的接口由治理提供)
            Status: 候选人的状态(0: 节点可用； 1: 节点不可用； 2： 节点出块率低； 4： 节点的von不足最低质押门槛； 8：节点被举报双签)
            StakingEpoch: 当前变更质押金额时的结算周期
            StakingBlockNum: 发起质押时的区块高度
            Shares: 当前候选人总共质押加被委托的von数目
            Released: 发起质押账户的自由金额的锁定期质押的von
            ReleasedHes: 发起质押账户的自由金额的犹豫期质押的von
            RestrictingPlan: 发起质押账户的锁仓金额的锁定期质押的von
            RestrictingPlanHes: 发起质押账户的锁仓金额的犹豫期质押的von
            ExternalId: 外部Id(有长度限制，给第三方拉取节点描述的Id)
            NodeName: 被质押节点的名称(有长度限制，表示该节点的名称)
            Website: 节点的第三方主页(有长度限制，表示该节点的主页)
            Details: 节点的描述(有长度限制，表示该节点的描述)
        '''
        data = rlp.encode([rlp.encode(int(1102))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        print(recive)
        return recive

    def getDelegateListByAddr(self,addr):
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
        data = rlp.encode([rlp.encode(int(1103)),rlp.encode(bytes.fromhex(addr))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        print(recive)
        return recive

    def getDelegateInfo(self,stakingBlockNum,delAddr,nodeId):
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
        data = rlp.encode([rlp.encode(int(1104)),rlp.encode(stakingBlockNum),
                           rlp.encode(bytes.fromhex(delAddr)),rlp.encode(bytes.fromhex(nodeId))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        # print(recive)
        recive = str(recive, encoding="utf8")
        print(recive)
        return recive

    def getCandidateInfo(self,nodeId):
        '''
        @getDelegateInfo: 查询当前节点的质押信息
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            NodeId: 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenifitAddress: 用于接受出块奖励和质押奖励的收益账户
            StakingTxIndex: 发起质押时的交易索引
            ProcessVersion: 被质押节点的PlatON进程的真实版本号(获取版本号的接口由治理提供)
            Status: 候选人的状态(0: 节点可用； 1: 节点不可用； 2： 节点出块率低； 4： 节点的von不足最低质押门槛； 8：节点被举报双签)
            StakingEpoch :发起委托账户的锁仓金额的犹豫期委托的von
            StakingBlockNum :发起质押时的区块高度
            Shares: 当前候选人总共质押加被委托的von数目
            Released: 发起质押账户的自由金额的锁定期质押的von
            ReleasedHes: 发起质押账户的自由金额的犹豫期质押的von
            RestrictingPlan: 发起质押账户的锁仓金额的锁定期质押的von
            RestrictingPlanHes: 发起质押账户的锁仓金额的犹豫期质押的von
            ExternalId: 外部Id(有长度限制，给第三方拉取节点描述的Id)
            NodeName: 被质押节点的名称(有长度限制，表示该节点的名称)
            Website: 节点的第三方主页(有长度限制，表示该节点的主页)
            Details: 节点的描述(有长度限制，表示该节点的描述)
        '''
        data = rlp.encode(rlp.encode([int(1105),rlp.encode(bytes.fromhex(nodeId))]))
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        print(recive)
        return recive

#################################治理###############################
    def submitText(self,verifier,githubID,topic,desc,url,endVotingBlock,from_address=None, gasPrice=None , gas=None):
        '''
        提交文本提案
        :param verifier: 64bytes
        :param githubID: string
        :param topic: string
        :param desc: string
        :param url: string
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2000)),rlp.encode(bytes.fromhex(verifier)),
                                    rlp.encode(githubID),rlp.encode(topic),
                                    rlp.encode(desc), rlp.encode(url),rlp.encode(endVotingBlock)])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice,gas,value=0)
        return self.get_result(result, self.submitText.__name__)

    def submitVersion(self,verifier,githubID,topic,desc,url,newVersion,endVotingBlock,activeBlock,
                      from_address=None, gasPrice=None , gas=None):
        '''
        提交升级提案
        :param verifier: 64bytes
        :param githubID: string
        :param topic: string
        :param desc: string
        :param url: string
        :param newVersion: uint
        :param endVotingBlock: uint64
        :param activeBlock: uint64
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2001)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(githubID), rlp.encode(topic),rlp.encode(desc),
                           rlp.encode(url),rlp.encode(int(newVersion)),rlp.encode(int(endVotingBlock)),
                           rlp.encode(int(activeBlock))])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice,gas,value=0)
        return self.get_result(result, self.submitVersion.__name__)

    def submitParam(self,verifier,githubID,topic,desc,url,endVotingBlock,currentValue,newValue,
                    from_address=None, gasPrice=None , gas=None):
        '''
        提交参数提案
        :param verifier: 64bytes
        :param githubID: string
        :param topic: string
        :param desc: string
        :param url: string
        :param endVotingBlock: uint64
        :param paramName:string
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2002)),rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(githubID),rlp.encode(topic),
                           rlp.encode(desc),rlp.encode(url),rlp.encode(int(endVotingBlock)),
                           rlp.encode(currentValue),rlp.encode(newValue)])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.submitParam.__name__)

    def vote(self,verifier,proposalID,option,from_address=None, gasPrice=None , gas=None):
        '''
        给提案投票
        :param verifier: 64bytes
        :param proposalID: common.Hash
        :param option: VoteOption
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2003)),rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(proposalID),rlp.encode(option)])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.vote.__name__)

    def declareVersion(self,activeNode,version,from_address=None, gasPrice=None , gas=None):
        '''
        版本声明
        :param activeNode: 64bytes
        :param version: uint
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2004)), rlp.encode(bytes.fromhex(activeNode)),
                           rlp.encode(int(version))])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.declareVersion.__name__)

    def getProposal(self,proposalID,from_address=None, gasPrice=None , gas=None):
        '''
        查询提案
        :param proposalID: common.Hash
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2100)),rlp.encode(proposalID)])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        # print(result)
        return self.get_result(result, self.getProposal.__name__)

    def getTallyResult(self,proposalID,from_address=None, gasPrice=None , gas=None):
        '''
        查询提案结果
        :param proposalID: common.Hash
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2101)),rlp.encode(str(proposalID))])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        print(result)
        return self.get_result(result, self.getTallyResult.__name__)

    def listProposal(self,from_address=None, gasPrice=None , gas=None):
        '''
        查询提案列表
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2102))])
        if not from_address:
            from_address = self.address
        if not gasPrice :
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.listProposal.__name__)

############################举报惩罚###############################################################
    def ReportMutiSign(self,data,from_address=None, gasPrice=None , gas=None):
        '''
        举报双签
        :param data: string
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        data_ = rlp.encode([rlp.encode(data)])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000004"
        result = self.send_raw_transaction(data_, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.ReportMutiSign.__name__)

    def CheckMutiSign(self,typ,addr,blockNumber,from_address=None, gasPrice=None , gas=None):
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
        if addr[:2] == '0x':
            addr = addr[2:]
        data = rlp.encode([rlp.encode(int(3001)),rlp.encode(int(typ)),
                            rlp.encode(str(addr)),rlp.encode(blockNumber)])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000004"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.CheckMutiSign.__name__)
#######################################锁仓###############################################

    def CreateRestrictingPlan(self,account,plan,from_address=None, gasPrice=None , gas=None):
        '''
        创建锁仓计划
        :param account: 20bytes
        :param plan: []RestrictingPlan
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if account[:2] == '0x':
            account = account[2:]
        plan_list = []
        for dict_ in plan:
            v = [rlp.encode(dict_[k]) for k in dict_]
            # print(v)
            plan_list.append(v)
        # print(rlp.encode(plan_list))
        data = rlp.encode([rlp.encode(int(4000)),
                           rlp.encode(bytes.fromhex(account)),
                           rlp.encode(plan_list)])
        if not from_address:
            from_address = self.address
        if not gasPrice:
            gasPrice = self.gasPrice
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000001"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, value=0)
        return self.get_result(result, self.CreateRestrictingPlan.__name__)

    def GetRestrictingInfo(self,account):
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
        data = rlp.encode([rlp.encode(int(4100)),rlp.encode(bytes.fromhex(account))])
        to_address = "0x1000000000000000000000000000000000000001"
        recive = self.eth.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        print(recive)
        return recive



if __name__ == '__main__':
    address = '0x493301712671Ada506ba6Ca7891F436D29185821'
    p = Ppos( 'http://10.10.8.157:6789',address ,'88888888')
    typ= 0
    benifitAddress = '0x493301712671Ada506ba6Ca7891F436D29185821'
    nodeId = 'f71e1bc638456363a66c4769284290ef3ccff03aba4a22fb60ffaed60b77f614bfd173532c3575abe254c366df6f4d6248b929cb9398aaac00cbcc959f7b2b7c'
    externalId = 'sfsf'
    nodeName ='ffswfv'
    website='ffaf'
    details = 'effs'
    amount= 180
    processVersion=30
    stakingBlockNum = 66
    # p.addStaking(nodeId,typ,amount)
    # p.GetRestrictingInfo(benifitAddress)
    # p.updateStakingInfo(benifitAddress, nodeId,externalId, nodeName, website, details)
    # p.staking(typ, benifitAddress, nodeId,externalId, nodeName, website, details, amount,processVersion)
    p.getVerifierList()
    p.getValidatorList()
    p.getCandidateList()
    p.getDelegateListByAddr(address)
    p.getDelegateInfo(stakingBlockNum,benifitAddress,nodeId)
    p.getCandidateInfo(nodeId)
    p.GetRestrictingInfo(address)
    # proposalID = 66666666666666666666666666666666
    # p.getTallyResult(proposalID)
    # web3 = Web3(Web3.HTTPProvider('http://10.10.8.157:6789'))
    # v1 = web3.toWei(80, 'ether')
    # v2 = web3.toWei(66, 'ether')
    # p.addStaking(nodeId,typ,amount)
    # p.getVerifierList()
    # p.getDelegateInfo()
    verifier = 'f71e1bc638456363a66c4769284290ef3ccff03aba4a22fb60ffaed60b77f614bfd173532c3575abe254c366df6f4d6248b929cb9398aaac00cbcc959f7b2b7c'
    githubID='66'
    topic = '888gergregreggregergregweferfwregweagf'
    desc = 'helloeferfgwrgrgwrgregregregregw'
    url = 'baidu.com'
    newVersion = 1354354
    endVotingBlock = 550
    activeBlock = 66
    currentValue= 66
    newValue = 11
    activeNode = verifier
    version = 88
    # p.getDelegateListByAddr()
    # p.submitText(verifier,githubID,topic,desc,url,endVotingBlock)
    proposalID = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    # p.getProposal(proposalID)
    plan =  [{"epoch": 12, "amount": 45}, {"epoch": 24, "amount": 90}]
    # p.CreateRestrictingPlan(benifitAddress,plan)







