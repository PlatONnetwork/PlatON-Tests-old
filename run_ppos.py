'''
@Author: xiaoming
@Date: 2018-12-13 14:35:48
@LastEditors: xiaoming
@LastEditTime: 2019-01-25 11:18:48
@Description: file content
'''
import json
import math
import random
import threading
import time
import queue
from web3 import Web3

from common import log
from common.load_file import LoadFile, get_node_list
from conf import setting as conf
from utils.platon_lib.dpos_1 import PlatonDpos

q = queue.Queue()

def sleep_time(w3):
    number = w3.eth.blockNumber
    i = 250
    d = math.ceil(number / i)
    total_time = i * d
    if total_time - number > 20:
        sleep_number = total_time - number
    else:
        sleep_number = total_time - number + i
    while True:
        new_block = w3.eth.blockNumber
        if new_block - number >= sleep_number:
            return
        time.sleep(2)


def wait_one(w3):
    number = w3.eth.blockNumber
    while True:
        time.sleep(1)
        new_number = w3.eth.blockNumber
        if new_number - number >= 1:
            return


class Ppos:
    def __init__(self, node_yml_path, cbft_json_path):
        node1, node2 = get_node_list(node_yml_path)
        self.node_list = node1 + node2
        key_list = ["node" + str(i) for i in range(1, 1 + len(self.node_list))]
        self.node_dict = dict(zip(key_list, self.node_list))
        cbft_dict = LoadFile(cbft_json_path).get_data()
        self.address = Web3.toChecksumAddress(conf.ADDRESS)
        self.address_candidate = Web3.toChecksumAddress("0x03f0E0a226f081A5dAeCFdA222caFc959eD7B800")
        self.private_candidate = "11e20dc277fafc4bc008521adda4b79c2a9e403131798c94eacb071005d43532"
        self.address_refund = Web3.toChecksumAddress("0x2B645d169998eb0447A21D0c48a1780d115251a9")
        self.private_refund = "6382b6fc972ae9c22a2d8913dace308d09e406d118efddb702a7ea9e505cc823"
        self.address_vote = Web3.toChecksumAddress("0x1E1ae3407377F7897470FEf31a80873B4FD75cA1")
        self.private_vote = "f7aa4dc6fceed0f099d0466ce2136a2cf3b500b15e8286572f39198b562a3bdb"
        self.pwd = conf.PASSWORD
        self.ticket_price = Web3.fromWei(
            int(cbft_dict['ppos']['ticket']['ticketPrice']), 'ether')
        self.allowed = int(cbft_dict['ppos']['candidate']['allowed'])
        self.total_ticket = int(cbft_dict['ppos']['ticket']['maxCount'])
        self.abi = conf.DPOS_CONTRACT_ABI
        self.platon_dpos = PlatonDpos(
            self.node_list[1]["url"], self.address, self.pwd, abi=self.abi)
        # self.w3_list = [connect_web3(node["url"]) for node in self.node_list]
        # self.new_address = Web3.toChecksumAddress(
        #     self.platon_dpos1.web3.personal.newAccount(self.pwd))
        self.platon_dpos.web3.personal.unlockAccount(self.address, self.pwd, 88888899)
        self.send_data = {
            "to": self.address_vote,
            "from": self.address,
            "gas": '9000',
            "gasPrice": '1000000000',
            "value": Web3.toWei(1000000, 'ether'),
        }
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.sendTransaction(self.send_data)
        tx_hash = self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.waitForTransactionReceipt(tx_hash)
        balance = self.platon_dpos.eth.getBalance(self.address_vote)
        log.info(balance)
        self.send_data = {
            "to": self.address_refund,
            "from": self.address,
            "gas": '9000',
            "gasPrice": '1000000000',
            "value": Web3.toWei(100000, 'ether'),
        }
        tx_hash = self.platon_dpos.eth.sendTransaction(self.send_data)
        self.platon_dpos.eth.waitForTransactionReceipt(tx_hash)
        self.fee = int(1000).to_bytes(4, 'big')
        self.extra = "Test"
        self.node_number = len(self.node_dict.keys())

    def check_event(self, msg):
        """
        校验event
        :param msg:
        :return:
        """
        event_data, func_name = msg
        func_name += "Event"
        assert func_name in event_data, "{}中不包含{}键".format(
            event_data, func_name)
        event = event_data[func_name][0]
        event = json.loads(event)
        assert event["Ret"], "质押结果状态错误"
        assert event["ErrMsg"] == "success", "质押结果msg错误"

    def candidate_deposit(self):
        '''
        @Description: 质押节点，使其成为候选人
        @param {type} @@@@
        @return: @@@@
        '''
        send_data = {
            "to": self.address_candidate,
            "from": self.address,
            "gas": '9000',
            "gasPrice": '1000000000',
            "value": Web3.toWei(2000, 'ether'),
        }
        platon_dpos = PlatonDpos(
            self.node_list[1]["url"], self.address_candidate, self.pwd, abi=self.abi, privatekey=self.private_candidate)
        while True:
            try:
                tx_hex = self.platon_dpos.eth.sendTransaction(send_data)
                self.platon_dpos.eth.waitForTransactionReceipt(tx_hex)
            except Exception as e:
                log.error(e)
            node_dict = random.sample(self.node_dict.keys(), random.randrange(1, self.node_number))
            log.info("选出的质押节点：{}".format(node_dict))
            candidate_list = self.get_candidate_list()
            verifier_list, _ = self.get_verifier_list()
            # log.info("不可质押节点:{}-{}".format(candidate_list, verifier_list))
            for node in node_dict:
                try:
                    if (self.node_dict[node]["id"] in candidate_list) or (self.node_dict[node]["id"] in verifier_list):
                        # log.info("不可质押:{}".format(self.node_dict[node]["id"]))
                        continue
                    value = random.randrange(50, 200)
                    result = platon_dpos.CandidateDeposit(self.node_dict[node]['id'], self.address_refund, self.fee,
                                                          self.node_dict[node]['host'],
                                                          self.node_dict[node]['port'], self.extra, value=value)
                    self.check_event(result)
                    candidate_info = platon_dpos.GetCandidateDetails(self.node_dict[node]['id'])
                    assert isinstance(candidate_info, dict), "返回结果错误{}".format(
                        candidate_info)
                    candidate_list = platon_dpos.GetCandidateList()
                    assert candidate_info in candidate_list, "候选人列表不包含节点{}".format(self.node_dict[node]['ip'])
                    log.info("质押成功：{}".format(node))
                except Exception as e:
                    log.error("质押节点：{}-{}".format(node, e))
            time.sleep(random.randrange(20, 200))

    def refund(self):
        '''
        @Description: 查询退款是否正常，是否退出候选人列表
        @param {type} @@@@
        @return: @@@@
        '''
        platon_dpos = PlatonDpos(
            self.node_list[1]["url"], self.address_refund, self.pwd, abi=self.abi, privatekey=self.private_refund)
        while True:
            n = 0
            if q.empty():
                status = 0
            else:
                q.get()
                status = 1
            node_dict = random.sample(self.node_dict.keys(), random.randrange(1, self.node_number))
            log.info("选出的退出节点：{}".format(node_dict))
            candidate_list = self.get_candidate_list()
            verifier_list, _ = self.get_verifier_list()
            if len(verifier_list) < 4:
                f = 0
            else:
                f = (len(verifier_list) - 1) / 3
            # log.info("可退出节点:{}".format(verifier_list))
            for node in node_dict:
                try:
                    if self.node_dict[node]["id"] in verifier_list:
                        if n >= f or not status:
                            continue
                        n += 1
                    if (self.node_dict[node]["id"] not in candidate_list) and (
                            self.node_dict[node]["id"] not in verifier_list):
                        # log.info("不可退出质押:{}".format(self.node_dict[node]["id"]))
                        continue
                    candidate_detail = platon_dpos.GetCandidateDetails(self.node_dict[node]["id"])
                    candidate_value = candidate_detail["Deposit"]
                except:
                    continue
                candidate_value_eth = platon_dpos.web3.fromWei(candidate_value, "ether")
                try:
                    result = platon_dpos.CandidateApplyWithdraw(
                        self.node_dict[node]['id'], candidate_value_eth)
                    self.check_event(result)
                    wait_one(platon_dpos.web3)
                    withdraw_list = platon_dpos.GetCandidateWithdrawInfos(
                        self.node_dict[node]['id'])
                    assert withdraw_list["Balance"] == candidate_value, "申请退款的金额与查询结果不一致"
                    result = platon_dpos.CandidateWithdraw(self.node_dict[node]["id"])
                    self.check_event(result)
                    log.info("退出质押成功：{}".format(node))
                except Exception as e:
                    log.error("解质押节点：{}-{}".format(node, e))
            time.sleep(random.randrange(20, 200))

    def vote_ticket(self):
        '''投票'''
        platon_dpos = PlatonDpos(
            self.node_list[1]["url"], self.address_vote, self.pwd, abi=self.abi, privatekey=self.private_vote)
        while True:
            node_dict = random.sample(self.node_dict.keys(), random.randrange(5, self.node_number))
            log.info("选出的投票节点：{}".format(node_dict))
            candidate_list = self.get_candidate_list()
            # log.info("可投票节点:{}".format(candidate_list))
            for node in node_dict:
                try:
                    if self.node_dict[node]["id"] not in candidate_list:
                        # log.info("不可投票:{}".format(self.node_dict[node]["id"]))
                        continue
                    allowed = random.randrange(1, self.allowed*3)
                    vote_info, _ = platon_dpos.VoteTicket(allowed, self.ticket_price, self.node_dict[node]['id'],
                                                          self.address_vote, allowed * self.ticket_price)
                    assert 'success' in vote_info['VoteTicketEvent'][0], '投票失败，结果:{}'.format(
                        vote_info)
                    log.info("投票成功:{},投票数:{}".format(node, allowed))
                except Exception as e:
                    log.error("投票节点：{}-{}".format(node, e))
            time.sleep(random.randrange(20, 200))

    def get_candidate_list(self):
        """
        获取候选人列表
        :return:
        """
        candidate_list = self.platon_dpos.GetCandidateList()
        candidate_list = [c['CandidateId'] for c in candidate_list]
        return candidate_list

    def get_verifier_list(self):
        """
        获取见证人列表
        :return:
        """
        verfier_info_list = self.platon_dpos.GetVerifiersList()
        verifier_list = [info['CandidateId'] for info in verfier_info_list]
        return verifier_list, verfier_info_list

    def verifiers(self):
        '''
        @Description: 验证人为候选人列表的前四，幸运票奖励发放
        @param {type} @@@@
        @return: @@@@
        '''
        while True:
            sleep_time(self.platon_dpos.web3)
            q.put(1)
            try:
                verifier_list, verfier_info_list = self.get_verifier_list()
                log.info("验证人列表:{},验证节点数：{}".format(verfier_info_list, len(verfier_info_list)))
            except Exception as e:
                log.error(e)

    def run(self):
        # while True:
        #     self.candidate_deposit()
        #     self.refund()
        #     self.vote_ticket()
        #     self.verifiers()
        th1 = threading.Thread(target=self.candidate_deposit)
        th1.setDaemon(True)
        th1.start()
        time.sleep(10)
        th2 = threading.Thread(target=self.vote_ticket)
        th2.setDaemon(True)
        th2.start()
        th = threading.Thread(target=self.refund)
        th.setDaemon(True)
        th.start()
        th5 = threading.Thread(target=self.verifiers)
        th5.setDaemon(True)
        th5.start()
        input("Input quit Enter:")


if __name__ == "__main__":
    ppos = Ppos("./deploy/node/node_061.yml", "./deploy/rely/cbft.json")
    ppos.run()
