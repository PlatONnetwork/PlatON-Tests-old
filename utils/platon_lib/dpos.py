'''
@Author: xiaoming
@Date: 2018-12-10 16:30:41
@LastEditors: xiaoming
@LastEditTime: 2019-01-25 11:11:31
@Description: file content
'''

import json
import re
import math
import rlp
from hexbytes import HexBytes
from web3.eth import Eth

from common.connect import connect_web3
from utils.platon_lib.event import Event


def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number
    else:
        return total_time - number + i

class PlatonDpos:
    def __init__(self, url, address, pwd, abi=r"./data/dpos/candidateConstract.json",
                 vote_abi=r'./data/dpos/ticketContract.json'):
        self.web3 = connect_web3(url)
        if not self.web3.isConnected():
            raise Exception("节点连接失败")
        print("连接成功")
        self.eth = Eth(self.web3)
        self.address = address
        if not self.web3.personal.unlockAccount(self.address, pwd, 22222):
            raise Exception("账号解锁失败")
        print("解锁账号成功")
        self.abi = abi
        self.vote_abi = vote_abi
        self.value = 100

    def get_result(self, tx_hash, func_name, abi=None):
        result = self.eth.waitForTransactionReceipt(tx_hash)
        """查看eventData"""
        topics = result['logs'][0]['topics']
        data = result['logs'][0]['data']
        if abi is None:
            event = Event(json.load(open(self.abi)))
        else:
            event = Event(json.load(open(abi)))
        event_data = event.event_data(topics, data)
        return event_data, func_name

    def CandidateDeposit(self, nodeid, owner, fee, host, port, extra, value=None):
        '''
        @Description: 节点候选人申请/增加质押，质押金额为交易的value值。
        @param
            nodeId: [64]byte 节点ID(公钥)
            owner: [20]byte 质押金退款地址
            fee: uint32 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            host: string 节点IP
            port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        @return:
            出参（事件：CandidateDepositEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        data = HexBytes(rlp.encode([int(1001).to_bytes(8, 'big'), self.CandidateDeposit.__name__, nodeid,
                                    owner, fee, host, str(port), extra])).hex()
        if not value:
            value = self.value
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "value": self.web3.toWei(value, "ether"),
            "data": data,
            "gas": "90000",
            "gasPrice": self.eth.gasPrice
        }
        self.value -= 1
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        # print('!!!!!', result)
        return self.get_result(result, self.CandidateDeposit.__name__)

    def CandidateApplyWithdraw(self, nodeid, withdraw):
        '''
        @Description: 节点质押金退回申请，申请成功后节点将被重新排序，权限校验from==owner
        @param
            nodeId: [64]byte 节点ID(公钥)
            withdraw: uint256 退款金额 (单位：ADP)
        @return:
            出参（事件：CandidateApplyWithdrawEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        # withdraw = np.uint256(withdraw)
        data = rlp.encode(
            [int(1002).to_bytes(8, 'big'), self.CandidateApplyWithdraw.__name__, nodeid, self.web3.toWei(withdraw, 'ether')])
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data,
            "gas": "9000",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        # print('申请退回hx：', result)
        return self.get_result(result, self.CandidateApplyWithdraw.__name__)

    def GetCandidateWithdrawInfos(self, nodeid):
        '''
        @Description: 获取节点申请的退款记录列表
        @param {type}
            nodeId: [64]byte 节点ID(公钥)
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'Balance': uint256 退款金额 (单位：ADP)
            LockNumber: uint256 退款申请所在块高
            LockBlockCycle: uint256 退款金额锁定周期
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateWithdrawInfos.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r'{.*}')
        recive = re.findall(p, recive)[0]
        recive = json.loads(recive)
        return recive

    def CandidateWithdraw(self, nodeid):
        '''
        @Description: 节点质押金提取，调用成功后会提取所有已申请退回的质押金到owner账户。
        @param:
            nodeId: [64]byte 节点ID(公钥)
        @return:
            出参（事件：CandidateWithdrawEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        data = HexBytes(rlp.encode(
            [int(1003).to_bytes(8, 'big'), self.CandidateWithdraw.__name__, nodeid])).hex()
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data,
            "gas": "9000",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        # print('退回hx：', result)
        return self.get_result(result, self.CandidateWithdraw.__name__)

    def SetCandidateExtra(self):
        '''
        @Description: 设置节点附加信息，供前端扩展使用
        @param:
            nodeId: [64]byte 节点ID(公钥)
            extra: string 附加信息
        @return:
            出参（事件：SetCandidateExtraEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        pass

    def GetCandidateDetails(self, nodeid):
        '''
        @Description: 获取候选人信息。
        @param {type} nodeId: [64]byte 节点ID(公钥)
        @return:
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateDetails.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r'{.*}')
        recive = re.findall(p, recive)[0]
        recive = re.sub("{{", "{", recive)
        recive = json.loads(recive)
        return recive

    def GetCandidateList(self):
        '''
        @Description: 获取所有入围节点的信息列表
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateList.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        recive = re.sub("{\[", "[", recive)
        p = re.compile(r'{.*?}')
        recive = re.findall(p, recive)
        try:
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def GetVerifiersList(self):
        '''
        @Description: 获取参与当前共识的验证人列表
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = rlp.encode(
            [int(10).to_bytes(8, 'big'), self.GetVerifiersList.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r'{.*?}')
        recive = re.findall(p, recive)
        recive = [json.loads(i) for i in recive]
        return recive

    def VoteTicket(self, count, price, nodeid, voter, value=None):
        '''
        购买选票，投票给候选人
        :param count: uint64 购票数量
        :param price:*big.Int 选票单价
        :param nodeid:[64]byte 候选人节点Id
        :param value: 发送交易的value为  购票数量 * 选票单价
        :return:
            出参（事件：VoteTicketEvent）：
            Ret: bool  操作结果
            Data: string  返回数据(成功选票的数量）
            ErrMsg: string  错误信息
        '''
        data = HexBytes(
            rlp.encode([int(1000).to_bytes(8, 'big'), self.VoteTicket.__name__, int(count).to_bytes(4, 'big'),
                        int(self.web3.toWei(price, 'ether')).to_bytes(8, 'big'), nodeid])).hex()
        if not value:
            value = self.value
        send_data = {
            "from": voter,
            "to": "0x1000000000000000000000000000000000000002",
            "value": self.web3.toWei(value, "ether"),
            "data": data,
            "gas": "0x6fffffff",
            "gasPrice": self.eth.gasPrice
        }
        txHashs = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result, _ = self.get_result(
            txHashs, self.VoteTicket.__name__, abi=self.vote_abi)
        return result, txHashs

    def GetTicketPrice(self):
        '''
        获取当前的票价
        :return:
            ret: *big.Int 当前票价
            error: string  错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketPrice.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = HexBytes(recive).decode('utf-8')
        partern = re.compile(r'\d')
        recive = ''.join(re.findall(partern, recive))
        return int(recive)

    def GetCandidateTicketIds(self, nodeid):
        '''
        获取指定候选人的选票Id的列表
        :param nodeid: [64]byte 节点Id
        :return:
            ret: []ticketId 选票的Id列表
            error: string 错误信息
        '''
        data = HexBytes(rlp.encode([int(10).to_bytes(8, 'big'),
                                    self.GetCandidateTicketIds.__name__, nodeid])).hex()
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile('\"(.+?)\"')
        recive = re.findall(p, recive)
        return recive

    def GetBatchCandidateTicketIds(self, node_ids):
        '''
        批量获取指定候选人的选票Id的列表
        :param node_ids: []nodeId 节点Id列表
        :return:
            ret: []ticketIds 多个节点的选票的Id列表
            error: string 错误信息
        '''
        encode_list = [int(10).to_bytes(
            8, 'big'), self.GetBatchCandidateTicketIds.__name__, ':'.join(node_ids)]
        data = rlp.encode(encode_list)
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r"{.*?}")
        recive = re.findall(p, recive)
        recive = [json.loads(i) for i in recive]
        return recive

    def GetTicketDetail(self, ticket_id):
        '''
        获取票详情
        :param ticket_id:[32]byte 票Id
        :return:
            ret: Ticket 选票信息
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketDetail.__name__, ticket_id])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r"{.*?}")
        recive = re.findall(p, recive)
        recive = [json.loads(i) for i in recive]
        return recive

    def GetBatchTicketDetail(self, ticket_ids):
        '''
        批量获取票详情
        :param ticket_ids:[]ticketId 票Id列表
        :return:
            ret: []Ticket 选票信息列表
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetBatchTicketDetail.__name__, ':'.join(ticket_ids)])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        p = re.compile(r"{.*?}")
        recive = re.findall(p, recive)
        recive = [json.loads(i) for i in recive]
        return recive

    def GetCandidateEpoch(self, nodeid):
        '''
        获取指定候选人的票龄
        :param nodeid:[64]byte 节点Id
        :return:
            ret: uint64 票龄
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateEpoch.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        partern = re.compile(r'\d')
        recive = ''.join(re.findall(partern, recive))
        return int(recive)

    def GetTicketCountByTxHash(self, txHashs):
        '''
        (批量)获取交易的有效选票数量
        :param txHashs: string 多个txHashs通过":"拼接的字符串
        :return:
            ret: dict(nodeId)uint32 多个节点的有效选票数量
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketCountByTxHash.__name__, txHashs])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        partern = re.compile(r'{.+?}')
        recive = re.findall(partern, recive)[0]
        recive = eval(recive)
        return recive

    def GetCandidateTicketCount(self, nodeIds):
        '''
        (批量)获取指定候选人的有效选票数量
        :param nodeIds: string 多个nodeId通过":"拼接的字符串
        :return:
            ret: dict(txHash)uint32 多个交易的有效选票数量
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateTicketCount.__name__, nodeIds])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        partern = re.compile(r'{.+?}')
        recive = re.findall(partern, recive)[0]
        recive = eval(recive)
        return recive

    def GetPoolRemainder(self):
        '''
        获取票池剩余票数量
        :return:
            ret: uint64 剩余票数量
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetPoolRemainder.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        recive = str(recive, encoding="ISO-8859-1")
        partern = re.compile(r'\d')
        recive = ''.join(re.findall(partern, recive))
        return int(recive)


if __name__ == "__main__":
    address = '0x493301712671Ada506ba6Ca7891F436D29185821'
    platon_p = PlatonDpos('http://192.168.9.160:6789', address, '88888888')
    node_id = '0x858d6f6ae871e291d3b7b2b91f7369f46deb6334e9dacb66fa8ba6746ee1f025bd4c090b17d17e0d9d5c19fdf81eb8bde3d40a383c9eecbe7ebda9ca95a3fb94'
    node_id2 = '0x97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0'
    node_id3 = '0x3b53564afbc3aef1f6e0678171811f65a7caa27a927ddd036a46f817d075ef0a5198cd7f480829b53fe62bdb063bc6a17f800d2eebf7481b091225aabac2428d'
    fee = int(6000).to_bytes(4, 'big')
    host = '192.168.9.162'
    port = '16789'
    extra = 'Test'
    value = 102
    # res_cd = platon_p.CandidateDeposit(node_id, address, fee, host, port, extra, value)  # 质押节点
    res_vt = platon_p.VoteTicket(10, 1, node_id3, address, 10)  # 投票
    # res_tc = platon_p.GetCandidateTicketCount(node_id+':'+node_id2)  #查询投票数
    # res_ct = platon_p.GetTicketCountByTxHash()

    # auto.start_one_node(
    #     './conf/dpos_join16785.yml', genesis_file='./data/genesis.json')
    # auto.start_one_node('./conf/dpos_join16786.yml',
    #                     genesis_file='./data/genesis.json')
    # auto.start_multi_node('./conf/dpos.yml')
    # # 可以通过yml文件获取nodeid，url_list,ip_list
    # boot_id_list = [
    #     "97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0",
    #     "3b53564afbc3aef1f6e0678171811f65a7caa27a927ddd036a46f817d075ef0a5198cd7f480829b53fe62bdb063bc6a17f800d2eebf7481b091225aabac2428d",
    #     "858d6f6ae871e291d3b7b2b91f7369f46deb6334e9dacb66fa8ba6746ee1f025bd4c090b17d17e0d9d5c19fdf81eb8bde3d40a383c9eecbe7ebda9ca95a3fb94",
    #     "b0971a3670e593ad7a3d5b3983b5d67db827e1fd267688dfef97e27604c1121dc6b8e5ba82a89d6dc552083296df8a7ab41466ab1e47929af69e94efd65df7b3",
    #     "64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617",
    #     "805b617b9d321a65d8936e758b5c60cd6e8c873b9f1e7c793ad5f887d26ce9667d0db2fe55a9aeb1cc81f9cf9a1e7c54473203473e3ebda89e63c03cbcfe5347"]
    # rpc_list = ["http://192.168.18.175:6789", "http://192.168.18.176:6789",
    #             "http://192.168.18.177:6789", "http://192.168.18.178:6789"]
    # need_join = ["http://192.168.9.178:6789", "http://192.168.18.179:6789"]
    # rpc_list = rpc_list + need_join
    # for url in rpc_list:
    #     w3 = Web3(Web3.HTTPProvider(url))
    #     w3.miner.start(1)
    # need_join = ["http://192.168.9.178:6789", "http://192.168.18.179:6789"]
    # rpc_list = rpc_list + need_join
    # for url in need_join:
    #     w3 = Web3(Web3.HTTPProvider(url))
    #     w3.miner.start(1)
    #     i = 0
    #     for boot_id in boot_id_list:
    #         enode = r"enode://" + boot_id + "@" + \
    #                 rpc_list[i].split(":")[1].strip("//") + ":16789"
    #         for _ in range(5):
    #             import time
    #
    #             time.sleep(0.05)
    #             w3.admin.addPeer(enode)
    #         i += 1
    #     print(w3.net.peerCount)
    # url = "http://192.168.18.175:6789"
    # url_list = ["http://192.168.18.175:6789", "http://192.168.18.176:6789",
    #             "http://192.168.18.177:6789", "http://192.168.18.178:6789",
    #             "http://192.168.9.178:6789", "http://192.168.18.179:6789"]
    # address = Web3.toChecksumAddress(
    #     "0x493301712671ada506ba6ca7891f436d29185821")
    # nodeid_dict = {
    #     '175': '0x97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0',
    #     '176': '0x3b53564afbc3aef1f6e0678171811f65a7caa27a927ddd036a46f817d075ef0a5198cd7f480829b53fe62bdb063bc6a17f800d2eebf7481b091225aabac2428d',
    #     '177': '0x858d6f6ae871e291d3b7b2b91f7369f46deb6334e9dacb66fa8ba6746ee1f025bd4c090b17d17e0d9d5c19fdf81eb8bde3d40a383c9eecbe7ebda9ca95a3fb94',
    #     '178': '0xb0971a3670e593ad7a3d5b3983b5d67db827e1fd267688dfef97e27604c1121dc6b8e5ba82a89d6dc552083296df8a7ab41466ab1e47929af69e94efd65df7b3',
    #     '179': '0x805b617b9d321a65d8936e758b5c60cd6e8c873b9f1e7c793ad5f887d26ce9667d0db2fe55a9aeb1cc81f9cf9a1e7c54473203473e3ebda89e63c03cbcfe5347',
    #     '178_2': '0x64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617'
    # }
    # ip_dict = {
    #     '175': '192.168.18.175',
    #     '176': '192.168.18.176',
    #     '177': '192.168.18.177',
    #     '178': '192.168.18.178',
    #     '179': '192.168.18.179',
    #     '178_2': '192.168.9.178'
    # }
    # pwd = "88888888"
    # platon_dpos = Platondpos(url, address, pwd)
    # # 新建一个账号用于质押
    # new_account = Web3.toChecksumAddress(
    #     platon_dpos.web3.personal.newAccount("88888888"))
    # params = {
    #     "to": new_account,
    #     "from": address,
    #     "gas": '9000',
    #     "gasPrice": '1000000000',
    #     "value": 210000000000000000000,
    # }
    # platon_dpos.eth.sendTransaction(params)
    # start_block = platon_dpos.eth.blockNumber
    # print(platon_dpos.eth.blockNumber)
    # owner = address
    # fee = int(1000).to_bytes(8, 'big')
    # port = '16789'
    # extra = "hahahah"
    # # for k in nodeid_dict.keys():
    # #     if k == '175' or k == '178_2':
    # #         continue
    # #     result = platon_dpos.CandidateDeposit(
    # #         nodeid_dict[k], owner, fee, ip_dict[k], port, extra)
    # platon_dpos.CandidateDeposit(
    #     nodeid_dict['176'], owner, fee, ip_dict['176'], port, extra)
    # platon_p = Platondpos(url, new_account, pwd)
    # print("获取质押前的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # print("发起质押")
    # platon_p.CandidateDeposit(
    #     nodeid_dict['178_2'], new_account, fee, ip_dict['178_2'], port, extra, 110)
    # platon_p.CandidateDeposit(
    #     nodeid_dict['178_2'], new_account, fee, ip_dict['178_2'], port, extra, 50)
    # print("获取质押后的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # print("查看候选人信息")
    # platon_dpos.GetCandidateDetails(nodeid_dict['178_2'])
    # print("获取候选人列表")
    # platon_dpos.GetGetCandidateList()
    # print("发起质押金退回申请")
    # platon_p.CandidateApplyWithdraw(
    #     nodeid_dict['178_2'], 110000000000000000000)
    # print("获取节点申请的退款记录列表")
    # platon_dpos.GetCandidateWithdrawInfos(nodeid_dict['178_2'])
    # print("获取申请后的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # a = platon_p.eth.getBalance(new_account)
    # time.sleep(2)
    # print("节点质押金提取，调用成功后会提取所有已申请退回的质押金到owner账户")
    # platon_p.CandidateWithdraw(nodeid_dict['178_2'])
    # print("获取质押金提取后的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # b = platon_p.eth.getBalance(new_account)
    # print(b - a)
    # print("退回金额:{}".format(platon_p.web3.fromWei(b - a, 'ether')))
    # print("退回路上损失金额:{}".format(platon_p.web3.fromWei(
    #     110000000000000000000 - b + a, 'ether')))
    # print("获取候选人列表")
    # platon_dpos.GetGetCandidateList()
    # time.sleep(60 - start_block + 1)
    # print("获取验证人列表")
    # platon_dpos.GetVerifiersList()
    # print(platon_dpos.eth.blockNumber)
    # time.sleep(5)
    # print(platon_dpos.eth.blockNumber)
    # hash_tx = platon_dpos.eth.sendTransaction(params)
    # result = platon_dpos.eth.waitForTransactionReceipt(hash_tx)
    # print(result)
    # for url in url_list:
    #     w = Web3(Web3.HTTPProvider(url))
    #     print(url, w.eth.blockNumber)
