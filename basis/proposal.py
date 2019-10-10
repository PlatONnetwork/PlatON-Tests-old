import rlp
from basis.ppos import Ppos


class Proposal(Ppos):
    def __init__(self, web3, address, chain_id=None, private_key=None, gas=None, gas_price=None):
        super().__init__(web3, address, chain_id, private_key, gas, gas_price)

    def submitText(self, verifier, pIDID, privatekey=None, from_address=None, gasPrice=None, gas=None):
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
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2000)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pIDID)])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def submitVersion(self, verifier, pIDID, newVersion, endVotingRounds, privatekey=None,
                      from_address=None, gasPrice=None, gas=None):
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
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2001)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pIDID), rlp.encode(int(newVersion)), rlp.encode(int(endVotingRounds))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def submitParam(self, verifier, url, endVotingBlock, paramName, currentValue, newValue,
                    privatekey=None, from_address=None, gasPrice=None, gas=None):
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
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2002)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(url), rlp.encode(int(endVotingBlock)),
                           rlp.encode(paramName), rlp.encode(str(currentValue)), rlp.encode(str(newValue))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def vote(self, verifier, proposalID, option, programVersion, versionSign, from_address=None, gasPrice=None,
             gas=None, privatekey=None):
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
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        if versionSign[:2] == '0x':
            versionSign = versionSign[2:]
        data = rlp.encode([rlp.encode(int(2003)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(bytes.fromhex(proposalID)), rlp.encode(option), rlp.encode(int(programVersion)),
                           rlp.encode(bytes.fromhex(versionSign))])
        if not gas:
            gas = self.gas
        to_address = "0x1000000000000000000000000000000000000005"
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    def declareVersion(self, activeNode, version, versionSign, privatekey=None, from_address=None, gasPrice=None,
                       gas=None):
        '''
        版本声明
        :param activeNode: 64bytes
        :param version: uint
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000005"
        if versionSign[0:2] == '0x':
            versionSign = versionSign[2:]
        data = rlp.encode([rlp.encode(int(2004)), rlp.encode(bytes.fromhex(activeNode)),
                           rlp.encode(int(version)), rlp.encode(bytes.fromhex(versionSign))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)

    # def getProposal(self,proposalID,privatekey=None,from_address=None, gasPrice=None , gas=None):
    #     '''
    #     查询提案
    #     :param proposalID: common.Hash
    #     :return:
    #     '''
    #     to_address = "0x1000000000000000000000000000000000000005"
    #
    #     data = rlp.encode([rlp.encode(int(2100)),rlp.encode(proposalID)])
    #     if not privatekey:
    #         privatekey = self.privatekey
    #     if not from_address:
    #         from_address = self.address
    #     if not gasPrice :
    #         gasPrice = self.gasPrice
    #     if not gas:
    #         transactiondict = {"to": to_address, "data": data}
    #         gas = self.eth.estimateGas (transactiondict)
    #     result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0,privatekey)
    #     # print(result)
    #     return self.get_result(result)

    # def getTallyResult(self,proposalID,privatekey=None,from_address=None, gasPrice=None , gas=None):
    #     '''
    #     查询提案结果
    #     :param proposalID: common.Hash
    #     :param from_address:
    #     :param gasPrice:
    #     :param gas:
    #     :return:
    #     '''
    #     to_address = "0x1000000000000000000000000000000000000005"
    #
    #     data = rlp.encode([rlp.encode(int(2101)),rlp.encode(str(proposalID))])
    #     if not privatekey:
    #         privatekey = self.privatekey
    #     if not from_address:
    #         from_address = self.address
    #     if not gasPrice :
    #         gasPrice = self.gasPrice
    #     if not gas:
    #         transactiondict = {"to": to_address, "data": data}
    #         gas = self.eth.estimateGas (transactiondict)
    #     result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0,privatekey)
    #     return self.get_result(result)

    def getProposal(self, proposalID):
        '''
        查询提案
        :param proposalID: common.Hash
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2100)), rlp.encode(bytes.fromhex(proposalID))])
        recive = self.call_result(self.address, to_address, data)
        return recive

    def getTallyResult(self, proposalID):
        '''
        查询提案结果
        :param proposalID: common.Hash
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        data = rlp.encode([rlp.encode(int(2101)), rlp.encode(bytes.fromhex(proposalID))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        return recive

    def getAccuVerifiersCount(self, proposalID, blockHash):
        '''
        查询提案的累积可投票人数
        :param proposalID: common.Hash
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        if blockHash[:2] == '0x':
            blockHash = blockHash[2:]
        data = rlp.encode(
            [rlp.encode(int(2105)), rlp.encode(bytes.fromhex(proposalID)), rlp.encode(bytes.fromhex(blockHash))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        return recive

    def listProposal(self):
        '''
        查询提案列表
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2102))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        return recive

    def getActiveVersion(self):
        """
        查询节点的链生效版本
        """
        data = rlp.encode([rlp.encode(int(2103))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        # print(recive)
        return recive

    def getProgramVersion(self):
        """
        查询节点代码版本
        """
        data = rlp.encode([rlp.encode(int(2104))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        # print(recive)
        return recive

    def listParam(self):
        """
        查询可治理参数列表
        """
        data = rlp.encode([rlp.encode(int(2105))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.call_result(self.address, to_address, data)
        # print(recive)
        return recive

    def submitCancel(self, verifier, pIDID, endVotingRounds, tobeCanceledProposalID, privatekey=None,
                     from_address=None, gasPrice=None, gas=None):
        '''
                提交取消提案
        :param verifier:
        :param pIDID:
        :param newVersion：
        :param endVotingRounds：
        :param tobeCanceledProposalID:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if tobeCanceledProposalID[:2] == '0x':
            tobeCanceledProposalID = tobeCanceledProposalID[2:]
        to_address = "0x1000000000000000000000000000000000000005"
        print(pIDID, endVotingRounds, tobeCanceledProposalID)
        data = rlp.encode([rlp.encode(int(2005)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pIDID), rlp.encode(int(endVotingRounds)),
                           rlp.encode(bytes.fromhex(tobeCanceledProposalID))])
        result = self.send_raw_transaction(data, from_address, to_address, gasPrice, gas, 0, privatekey)
        return self.get_result(result)
