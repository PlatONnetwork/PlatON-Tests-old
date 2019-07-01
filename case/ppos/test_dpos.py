import json
import math
import time

from client_sdk_python import Web3
from common.connect import connect_web3
from utils.platon_lib.dpos import PlatonDpos
from conf import  setting as conf
from common.load_file import LoadFile, get_node_info
from common import log
from deploy.deploy import AutoDeployPlaton

def get_sleep_time(number):
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        return total_time - number + 20
    else:
        return total_time - number + i + 20

def update_cbft_json(template, tmp, max_count, max_chair):
    with open(template, 'r', encoding='utf-8') as f:
        res = json.loads(f.read())
        res['ppos']["candidate"]["maxCount"] = max_count
        res['ppos']["candidate"]["maxChair"] = max_chair
    with open(tmp, 'w', encoding='utf-8') as b:
        cbft_json = json.dumps(res)
        b.write(cbft_json)

class TestDpos:
    node_yml_path = conf.NODE_YML
    cbft_json_path = conf.CBFT2
    node_info = get_node_info(node_yml_path)
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get(
        'collusion')
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get(
        'nocollusion')
    cbft_dict = LoadFile(cbft_json_path).get_data()
    address = Web3.toChecksumAddress(conf.ADDRESS)
    pwd = conf.PASSWORD
    ticket_price = Web3.fromWei(
        int(cbft_dict['ppos']['ticket']['ticketPrice']), 'ether')
    allowed = int(cbft_dict['ppos']['candidate']['allowed'])
    total_ticket = int(cbft_dict['ppos']['ticket']['maxCount'])
    rpc_list += rpc_list2
    enode_list += enode_list2
    nodeid_list += nodeid_list2
    ip_list += ip_list2
    port_list += port_list2
    key_list = ["node" + str(i) for i in range(1, 1 + len(rpc_list))]
    rpc_dict = dict(zip(key_list, rpc_list))
    enode_dict = dict(zip(key_list, enode_list))
    nodeid_dict = dict(zip(key_list, nodeid_list))
    ip_dict = dict(zip(key_list, ip_list))
    port_dict = dict(zip(key_list, port_list))
    abi = conf.DPOS_CONTRACT_ABI

    def setup_class(self):
        self.auto = AutoDeployPlaton(cbft=self.cbft_json_path)
        self.auto.start_all_node(self.node_yml_path)
        self.platon_dpos1 = PlatonDpos(
            self.rpc_list[0], self.address, self.pwd, abi=self.abi)
        self.w3_list = [connect_web3(url) for url in self.rpc_list]
        self.new_address = Web3.toChecksumAddress(
            self.platon_dpos1.web3.personal.newAccount(self.pwd))
        self.send_data = {
            "to": self.new_address,
            "from": self.address,
            "gas": '9000',
            "gasPrice": '1000000000',
            "value": self.w3_list[0].toWei(100000, 'ether'),
        }
        tx_hash = self.platon_dpos1.eth.sendTransaction(self.send_data)
        self.platon_dpos1.eth.waitForTransactionReceipt(tx_hash)
        self.platon_dpos2 = PlatonDpos(
            self.rpc_list[0], self.new_address, self.pwd, abi=self.abi)
        self.fee = int(1000).to_bytes(4, 'big')
        self.extra = "Test"

    # def teardown_class(self):
    #     self.auto.start_all_node(self.node_yml_path)

    def check_event(self, msg):
        event_data, func_name = msg
        func_name += "Event"
        assert func_name in event_data, "{}中不包含{}键".format(
            event_data, func_name)
        event = event_data[func_name][0]
        event = json.loads(event)
        assert event["Ret"], "质押结果状态错误"
        assert event["ErrMsg"] == "success", "质押结果msg错误"

    def test_candidate_deposit(self):
        '''
        @Description: 质押节点，使其成为候选人
        @param {type} @@@@
        @return: @@@@
        '''
        result = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node5'], self.new_address, self.fee,
                                                    self.ip_dict['node5'],
                                                    self.port_dict['node5'], self.extra, value=100)
        self.check_event(result)
        candidate_info = self.platon_dpos1.GetCandidateDetails(
            self.nodeid_dict['node5'])
        assert isinstance(candidate_info, dict), "返回结果错误{}".format(
            candidate_info)
        assert candidate_info["Deposit"] == self.platon_dpos1.web3.toWei(
            100, 'ether')
        assert candidate_info["Host"] == self.ip_dict["node5"], "质押ip与传输的ip不一致"
        assert candidate_info["CandidateId"] == self.nodeid_dict["node5"], "质押nodeid与传输的不一致"
        assert candidate_info["Port"] == self.port_dict['node5'], "质押端口与传输的不一致,获取port:{}，实际质押port:{}".format(
            candidate_info["Port"], self.port_dict['node5'])
        assert self.platon_dpos1.web3.toChecksumAddress(
            candidate_info["Owner"]) == self.new_address, "质押地址不正确"
        candidate_list = self.platon_dpos2.GetCandidateList()
        # 校验candidate_list包含节点179
        assert candidate_info in candidate_list, "候选人列表不包含节点{}".format(
            self.ip_dict['node5'])

    # @pytest.mark.skip
    # def add_pledge(self):
    #     '''
    #     已不支持增加质押，用例暂不执行
    #     增加质押
    #     :return:
    #     '''
    #     result = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node5'], self.new_address, self.fee,
    #                                                 self.ip_dict['node5'],
    #                                                 self.port_dict['node5'], self.extra, value=10)
    #     self.check_event(result)
    #     candidate_info = self.platon_dpos1.GetCandidateDetails(
    #         self.nodeid_dict['node5'])
    #     # candidate_info为节点179的质押信息
    #     assert isinstance(candidate_info, dict), "返回结果错误{}".format(
    #         candidate_info)
    #     assert candidate_info["Deposit"] == self.platon_dpos1.web3.toWei(
    #         60, 'ether')

    # @pytest.mark.skip
    # def test_refund_10(self):
    #     '''
    #     已不支持部分退款，用例暂不执行
    #     @Description: 查询退款金额低于10%
    #     @param {type} @@@@
    #     @return: @@@@
    #     '''
    #     i = 500000000000000000
    #     status = 0
    #     try:
    #         self.platon_dpos2.CandidateApplyWithdraw(
    #             self.nodeid_dict['node5'], i)
    #     except:
    #         status = 1
    #     assert status == 1, "低于10%应不允许提取"

    def test_refund(self):
        '''
        @Description: 查询退款是否正常，是否退出候选人列表
        @param {type} @@@@
        @return: @@@@
        '''
        i = 50000000000000000000
        start_balance = self.platon_dpos2.eth.getBalance(self.new_address)
        result = self.platon_dpos2.CandidateDeposit(self.nodeid_dict['node6'], self.new_address, self.fee,
                                                    self.ip_dict['node6'],
                                                    self.port_dict['node6'], self.extra, value=50)
        candidate_info = self.platon_dpos1.GetCandidateDetails(
            self.nodeid_dict['node6'])
        self.check_event(result)
        result = self.platon_dpos2.CandidateApplyWithdraw(
            self.nodeid_dict['node6'], i)
        self.check_event(result)
        time.sleep(3)
        withdraw_list = self.platon_dpos2.GetCandidateWithdrawInfos(
            self.nodeid_dict['node6'])
        assert withdraw_list["Balance"] == i, "申请退款的金额与查询结果不一致"
        result = self.platon_dpos1.CandidateWithdraw(self.nodeid_dict["node6"])
        self.check_event(result)
        end_balance = self.platon_dpos1.eth.getBalance(self.new_address)
        assert end_balance - start_balance < 100000000000000000, "退款金额错误，退款前:{}|退款后:{}".format(
            self.platon_dpos1.web3.fromWei(start_balance, 'ether'), self.platon_dpos1.web3.fromWei(end_balance, 'ether'))
        candidate_list = self.platon_dpos1.GetCandidateList()
        assert candidate_info not in candidate_list, "node6还在候选人列表中"

    def test_candidate_sort(self):
        '''
        @Description: 候选人排序
        @param {type} @@@@
        @return: @@@@
        '''
        # result_1 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node5'], self.new_address, self.fee,
        #                                               self.ip_dict['node5'],
        #                                               self.port_dict['node5'], self.extra, value=45)
        # self.check_event(result_1)
        result_2 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node6'], self.new_address, self.fee,
                                                      self.ip_dict['node6'],
                                                      self.port_dict['node6'], self.extra, value=160)
        self.check_event(result_2)
        candidate_list = self.platon_dpos1.GetCandidateList()
        candidate_info = self.platon_dpos1.GetCandidateDetails(
            self.nodeid_dict['node6'])
        assert candidate_list[0] == candidate_info, "候选人列表排序错误"

    def test_candidate_cap(self):
        '''
        @Description: 候选人列表容量
        @param {type} @@@@
        @return: @@@@
        '''
        status = 0
        candidate_info = self.platon_dpos1.GetCandidateDetails(
            self.nodeid_dict['node5'])
        result_1 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node1'], self.new_address, self.fee,
                                                      self.ip_dict['node1'],
                                                      self.port_dict['node1'], self.extra, value=131)
        self.check_event(result_1)
        result_2 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node2'], self.new_address, self.fee,
                                                      self.ip_dict['node2'],
                                                      self.port_dict['node2'], self.extra, value=135)
        self.check_event(result_2)
        result_3 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node3'], self.new_address, self.fee,
                                                      self.ip_dict['node3'],
                                                      self.port_dict['node3'], self.extra, value=135)
        self.check_event(result_3)
        result_4 = self.platon_dpos1.CandidateDeposit(self.nodeid_dict['node4'], self.new_address, self.fee,
                                                      self.ip_dict['node4'],
                                                      self.port_dict['node4'], self.extra, value=140)
        self.check_event(result_4)
        candidate_list = self.platon_dpos1.GetCandidateList()
        log.info("入围节点列表：{}".format(candidate_list))
        assert candidate_info not in candidate_list, "node5还在候选人列表中"

    def test_ticket_price(self):
        '''校验票价是否与配置文件中一致'''
        price = self.platon_dpos1.GetTicketPrice()
        config_price = Web3.toWei(self.ticket_price, 'ether')
        assert config_price == price, '实际票价:{},与配置文件中:{},不一致'.format(
            config_price, price)

    def test_vote_ticket(self):
        '''投票'''
        value = self.allowed * self.ticket_price
        vote_info, _ = self.platon_dpos1.VoteTicket(self.allowed, self.ticket_price, self.nodeid_dict['node6'],
                                                    self.new_address, value)
        self.platon_dpos1.VoteTicket(self.allowed, self.ticket_price, self.nodeid_dict['node1'],
                                     self.new_address, value)
        self.platon_dpos1.VoteTicket(self.allowed, self.ticket_price, self.nodeid_dict['node2'],
                                     self.new_address, value)
        self.platon_dpos1.VoteTicket(self.allowed, self.ticket_price, self.nodeid_dict['node3'],
                                     self.new_address, value)
        vote_info, _ = self.platon_dpos1.VoteTicket(self.allowed - 1, self.ticket_price, self.nodeid_dict['node4'],
                                     self.new_address, value - 1)
        assert 'success' in vote_info['VoteTicketEvent'][0], '投票失败，结果:{}'.format(
            vote_info)

    # @pytest.skip
    # def test_ticket_detail(self):
    #     '''
    #     接口已经删除，用例屏蔽
    #     验证节点下选票数量、选票的详细信息
    #     '''
    #     ticket_ids = self.platon_dpos1.GetCandidateTicketIds(self.nodeid_dict['node1'])
    #     ticket_num = len(ticket_ids)
    #     assert ticket_num == self.allowed, '节点选票数:{}与已投票数:{}不一致'.format(ticket_num, self.allowed)
    #     ticket_detail = self.platon_dpos1.GetTicketDetail(ticket_ids[0])
    #     owner = Web3.toChecksumAddress(ticket_detail[0]['Owner'])
    #     assert owner == self.new_address, '投票人:{}与投票时用的钱包地址:{}不一致'.format(owner, self.new_address)
    #     dposite = ticket_detail[0]['Deposit']
    #     price = Web3.toWei(self.ticket_price, 'ether')
    #     assert dposite == price, '投票金额:{}与票价:{}不一致'.format(dposite, price)
    #     candidateid = ticket_detail[0]['CandidateId']
    #     assert candidateid == self.nodeid_dict['node1'], '票详情中节点id:{},与投票时节点id不一致:{}'.format(candidateid,
    #                                                                                          self.nodeid_dict['node1'])

    # @pytest.skip
    # def test_batch_ticket_detail(self):
    #     '''
    #     接口已删除，用例屏蔽
    #     验证批量获取节点下选票数量、选票的详细信息
    #     '''
    #     batch_ticket_ids = self.platon_dpos1.GetBatchCandidateTicketIds(
    #         [self.nodeid_dict['node1'], self.nodeid_dict['node2']])
    #     print('batch_ticket_ids = ', batch_ticket_ids)
    #     ticket_ids = batch_ticket_ids[0].get(self.nodeid_dict['node1'])
    #     ticket_ids_one = self.platon_dpos1.GetCandidateTicketIds(self.nodeid_dict['node1'])
    #     assert ticket_ids == ticket_ids_one, '批量获取详情{}\n单独获取详情{}不一致'.format(ticket_ids, ticket_ids_one)
    #     node1_tickets = batch_ticket_ids[0].get(self.nodeid_dict['node1'])
    #     node2_tickets = batch_ticket_ids[0].get(self.nodeid_dict['node2'])
    #     ticket_details = self.platon_dpos1.GetBatchTicketDetail([node1_tickets[0], node2_tickets[0]])
    #     ticket_detail = ticket_details[0]
    #     ticket_detail_one = self.platon_dpos1.GetTicketDetail(ticket_details[0]['TicketId'])[0]
    #     assert ticket_detail == ticket_detail_one, '批量获取的票详情{}与单独查询票详情不一致{}'.format(ticket_detail, ticket_detail_one)
    #     assert len(ticket_details) == 2, '批量获取票详情数{}不等于请求数2'.format(len(ticket_details))

    def test_vote_undpos_node(self):
        '''向非备选池节点投票'''
        value = self.allowed * self.ticket_price
        status = 0
        try:
            self.platon_dpos1.VoteTicket(self.allowed, self.ticket_price, self.nodeid_dict['node5'],
                                         self.new_address, value)
        except:
            status = 1
        assert status, '不在备选池的节点不能投票成功'

    def test_ticket_pool_remainder(self):
        '''验证票池剩余数量'''
        remaind = self.platon_dpos1.GetPoolRemainder()
        should_remaind = self.total_ticket - (self.allowed * 5 - 1)
        assert remaind == should_remaind, '票池剩余票:{}与已消费后应剩余数:{}不一致'.format(
            remaind, should_remaind)

    # @pytest.skip
    # def test_get_candidate_epoch(self):
    #     '''
    #     获取票龄详情接口已删除，无法获取选票产生区块，用例无法验证
    #     该接口以后会去掉，用例暂不运行
    #     验证候选人票龄
    #     '''
    #     ticket_ids = self.platon_dpos1.GetCandidateTicketIds(self.nodeid_dict['node1'])
    #     vote_block_number = self.platon_dpos1.GetTicketDetail(ticket_ids[0])[0]['BlockNumber']
    #     should_epoch = (self.platon_dpos1.eth.blockNumber - vote_block_number + 1) * len(ticket_ids)
    #     epoch = self.platon_dpos1.GetCandidateEpoch(self.nodeid_dict['node1'])
    #     assert epoch == should_epoch, '候选人票龄计算结果:{},与预期结果:{}不一致'.format(epoch, should_epoch)

    def test_get_candidate_ticket_count(self):
        '''批量查询候选节点的有效选票数量'''
        ctc_dict = self.platon_dpos1.GetCandidateTicketCount(
            '{}:{}:{}:{}'.format(self.nodeid_dict['node1'], self.nodeid_dict['node2'], self.nodeid_dict['node3'],
                                 self.nodeid_dict['node4']))
        count1 = int(ctc_dict.get(self.nodeid_dict['node1']))
        count2 = int(ctc_dict.get(self.nodeid_dict['node2']))
        count3 = int(ctc_dict.get(self.nodeid_dict['node3']))
        count4 = int(ctc_dict.get(self.nodeid_dict['node4']))
        assert count1 == self.allowed, '候选节点有效选票数量{},与预期结果{}不一致'.format(
            count1, self.allowed)
        assert count2 == self.allowed, '候选节点有效选票数量{},与预期结果{}不一致'.format(
            count2, self.allowed)
        assert count3 == self.allowed, '候选节点有效选票数量{},与预期结果{}不一致'.format(
            count3, self.allowed)
        assert count4 == self.allowed - \
            1, '候选节点有效选票数量{},与预期结果{}不一致'.format(count4, self.allowed)

    # def test_get_ticket_count_by_tx_hash(self):
    #     '''批量查询交易的有效选票数量'''
    #     _, tx_hash1 = self.platon_dpos1.VoteTicket(
    #         self.allowed, 1, self.nodeid_dict['node1'], self.address, 10)
    #     _, tx_hash2 = self.platon_dpos1.VoteTicket(
    #         self.allowed, 1, self.nodeid_dict['node2'], self.address, 10)
    #     _, tx_hash3 = self.platon_dpos1.VoteTicket(
    #         self.allowed, 1, self.nodeid_dict['node3'], self.address, 10)
    #     _, tx_hash4 = self.platon_dpos1.VoteTicket(
    #         self.allowed, 1, self.nodeid_dict['node4'], self.address, 10)
    #     tc_dict = self.platon_dpos1.GetTicketCountByTxHash(
    #         '{}:{}:{}:{}'.format(tx_hash1, tx_hash2, tx_hash3, tx_hash4))
    #     assert tc_dict.get(tx_hash1) == self.allowed, '交易的有效选票数量{},与预期结果{}不一致'.format(tc_dict.get(tx_hash1),
    #                                                                                   self.allowed)
    #     assert tc_dict.get(tx_hash2) == self.allowed, '交易的有效选票数量{},与预期结果{}不一致'.format(tc_dict.get(tx_hash2),
    #                                                                                   self.allowed)
    #     assert tc_dict.get(tx_hash3) == self.allowed, '交易的有效选票数量{},与预期结果{}不一致'.format(tc_dict.get(tx_hash3),
    #                                                                                   self.allowed)
    #     assert tc_dict.get(tx_hash4) == self.allowed, '交易的有效选票数量{},与预期结果{}不一致'.format(tc_dict.get(tx_hash4),
    #                                                                                   self.allowed)

    def test_verifiers(self):
        '''
        @Description: 验证人为候选人列表的前四，幸运票奖励发放
        @param {type} @@@@
        @return: @@@@
        '''
        before_reward = self.platon_dpos1.eth.getBalance(self.new_address)
        candidate_list = self.platon_dpos1.GetCandidateList()
        log.info("新的的入围节点列表：{}".format(candidate_list))
        candidate_id = [i['CandidateId'] for i in candidate_list]
        block_number = self.platon_dpos1.eth.blockNumber
        sleep_time = get_sleep_time(block_number)
        time.sleep(sleep_time)
        verfier_info_list = self.platon_dpos1.GetVerifiersList()
        log.info("验证人列表:{}".format(verfier_info_list))
        assert len(verfier_info_list) > 0,"查询结果异常，验证人列表为空。"
        verfier_list = [info['CandidateId'] for info in verfier_info_list]
        assert verfier_list == candidate_id[:4], "验证人没有取候选人的前四,验证人id:{}\n候选人id:{}".format(verfier_list,
                                                                                            candidate_list[:4])
        status = 1
        for verfier in verfier_list:
            if self.nodeid_dict['node4'] in verfier:
                status = 0
        assert status, '投票不达到门槛不能成为见证人'
        # 校验幸运选票是否发放奖励
        after_reward = self.platon_dpos1.eth.getBalance(self.new_address)
        assert after_reward > before_reward, '见证人奖励未发放，发放前余额:{},发放后余额:{}'.format(
            before_reward, after_reward)

    def test_verify_transaction(self):
        '''
        @Description: 切换验证人后，测试交易是否成功，所有节点块高是否一致
        @param {type} @@@@
        @return: @@@@
        '''
        tx_hash = self.platon_dpos1.eth.sendTransaction(self.send_data)
        self.platon_dpos1.eth.waitForTransactionReceipt(tx_hash)
        block_list = []
        for w in self.w3_list:
            block_list.append(w.eth.blockNumber)
        assert min(block_list) > 60, "区块没有正常增加"
        assert max(block_list) - min(block_list) < 5, "各节点区块高度差距过高"
        time.sleep(60)
        w3 = Web3(Web3.HTTPProvider(self.rpc_dict["node6"]))
        assert w3.net.peerCount >= 3, "节点node6连接的节点数少于3个"
