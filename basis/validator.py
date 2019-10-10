import rlp
from basis.ppos import Ppos


class Validator(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def getVerifierList(self):
        '''
        @GetVerifierList: 查询当前结算周期的验证人队列
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'NodeId': 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenefitAddress: 用于接受出块奖励和质押奖励的收益账户
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
        recive = self.call_array_result(self.address, to_address, data)
        # print(recive)
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
            BenefitAddress: 用于接受出块奖励和质押奖励的收益账户
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
        recive = self.call_array_result(self.address, to_address, data)
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
            BenefitAddress: 用于接受出块奖励和质押奖励的收益账户
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
        recive = self.call_array_result(self.address, to_address, data)
        for i in recive['Data']:
            i["Shares"] = int(i["Shares"], 16)
            i["Released"] = int(i["Released"], 16)
            i["ReleasedHes"] = int(i["ReleasedHes"], 16)
            i["RestrictingPlan"] = int(i["RestrictingPlan"], 16)
            i["RestrictingPlanHes"] = int(i["RestrictingPlanHes"], 16)
        return recive

    def getCandidateInfo(self, nodeId):
        '''
        @getCandidateInfo: 查询当前节点的质押信息
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            NodeId: 被质押的节点Id(也叫候选人的节点Id)
            StakingAddress: 发起质押时使用的账户(后续操作质押信息只能用这个账户，撤销质押时，von会被退回该账户或者该账户的锁仓信息中)
            BenefitAddress: 用于接受出块奖励和质押奖励的收益账户
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
        data = rlp.encode([rlp.encode(int(1105)), rlp.encode(bytes.fromhex(nodeId))])
        to_address = "0x1000000000000000000000000000000000000002"
        recive = self.call_object_result(self.address, to_address, data)
        # print(recive)
        if recive["Data"] != "":
            recive["Data"]["Shares"] = int(recive["Data"]["Shares"], 16)
            recive["Data"]["Released"] = int(recive["Data"]["Released"], 16)
            recive["Data"]["ReleasedHes"] = int(recive["Data"]["ReleasedHes"], 16)
            recive["Data"]["RestrictingPlan"] = int(recive["Data"]["RestrictingPlan"], 16)
            recive["Data"]["RestrictingPlanHes"] = int(recive["Data"]["RestrictingPlanHes"], 16)
        return recive
