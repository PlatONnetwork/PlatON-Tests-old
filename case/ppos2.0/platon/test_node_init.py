# -*- coding: utf-8 -*-

import json

from client_sdk_python import Web3

from common.connect import connect_web3
from common.load_file import LoadFile, get_node_info
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton
from utils.platon_lib.dpos import PlatonDpos
from utils.platon_lib.ppos import Ppos


class TestDposinit:
    address = Web3.toChecksumAddress(conf.ADDRESS)
    pwd = conf.PASSWORD
    abi = conf.DPOS_CONTRACT_ABI
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.TWENTY_FIVENODE_YML
    file = conf.CASE_DICT




    def ppos_link(self,rpc_list):
        self.platon_dpos1 = PlatonDpos (
            rpc_list, self.address, self.pwd, abi=self.abi)
        return self.platon_dpos1

    def transfer_parameters(self, to_address, from_address):
        self.w3_list = [connect_web3 (url) for url in self.rpc_list]
        self.send_data = {
            "to": to_address,
            "from": from_address,
            "gas": '9000',
            "gasPrice": '1000000000',
            "value": self.w3_list[0].toWei (100000, 'ether'),
        }
        return self.send_data

    def create_new_address(self):
        self.new_address = Web3.toChecksumAddress (
            self.ppos_link(self.rpc_list).web3.personal.newAccount (self.pwd))
        return self.new_address

    def update_config(self, file, key, data):
        with open(self.file, 'r', encoding='utf-8') as f:
            res = json.loads(f.read())



    def test_init_token(self):
        self.auto = AutoDeployPlaton (cbft=self.cbft_json_path)
        self.auto.start_all_node (self.node_yml_path)
        proportion = {'FOUNDATION':0.001,
                      'DEVELOPERS':0.001,
                      'INCENTIVEPOOL':0.001,
                      'RESERVED':0.001
                      }
        FOUNDATION = self.platon_ppos.eth.getBalance(conf.FOUNDATIONADDRESS)
        DEVELOPERS = self.platon_ppos.eth.getBalance(conf.DEVELOPERSADDRESS)
        INCENTIVEPOOL = self.platon_ppos.eth.getBalance(conf.INCENTIVEPOOLADDRESS)
        RESERVED = self.platon_ppos.eth.getBalance(conf.RESERVEDADDRESS)
        FOUNDATIONLOCKUP = self.platon_dpos1.eth.getBalance (conf.FOUNDATIONLOCKUPADDRESS)
        token_init_total = conf.TOKENTOTAL
        assert (token_init_total * proportion['FOUNDATION']) == (FOUNDATION +FOUNDATIONLOCKUP)
        assert (token_init_total * proportion['DEVELOPERS']) == DEVELOPERS
        assert (token_init_total * proportion['INCENTIVEPOOL']) == INCENTIVEPOOL
        assert (token_init_total * proportion['RESERVED']) == RESERVED
        assert token_init_total == (FOUNDATION + FOUNDATIONLOCKUP + DEVELOPERS + INCENTIVEPOOL + RESERVED)



    def test_token_transactions(self):
        node_info = get_node_info(conf.TWENTY_FIVENODE_YML)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
            'collusion')
        from_address = Web3.toChecksumAddress (conf.ADDRESS)
        to_address = Web3.toChecksumAddress (
            self.ppos_link (self.rpc_list).web3.personal.newAccount (self.pwd))
        send_data = self.transfer_parameters(to_address,from_address)
        self.platon_ppos.eth.sendTransaction(send_data)
        assert self.platon_dpos1.eth.getBalance(to_address) == self.w3_list[0].toWei (100000, 'ether')

    def test_token_loukup(self):
        #查看初始化时锁仓余额
        file = conf.GENESIS_TMP_OTHER
        genesis_dict = LoadFile (file).get_data ()
        FOUNDATION = genesis_dict['alloc'][conf.FOUNDATIONADDRESS]
        FOUNDATIONLOCKUP = self.platon_dpos1.eth.getBalance(conf.FOUNDATIONLOCKUPADDRESS)
        node_info = get_node_info (conf.PPOS25NODE_YML)
        self.rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get (
            'collusion')
        FOUNDATIONTOTAL = conf.TOKENTOTAL * 0.01
        assert FOUNDATIONTOTAL == (FOUNDATION + FOUNDATIONLOCKUP)

    def test_loukupplan(self):
        from_address = Web3.toChecksumAddress (conf.ADDRESS)
        to_address = Web3.toChecksumAddress (
            self.ppos_link (self.rpc_list).web3.personal.newAccount (self.pwd))
        send_data = self.transfer_parameters (to_address, from_address)
        self.platon_ppos.eth.sendTransaction (send_data)
        toaddressbalace = self.platon_dpos1.eth.getBalance(to_address)
        loukupbalace = toaddressbalace / 4
        plan = [{'Epoch': 3 ,'Amount':loukupbalace},{'Epoch': 3 ,'Amount':loukupbalace}]
        Ppos.CreateRestrictingPlan(to_address,plan,to_address)
        result = Ppos.GetRestrictingInfo(to_address,to_address)

    def test_staking(self):
        pass






if __name__ == "__main__":
    a = TestDposinit()
    a.update_config('SyncMode','full1')