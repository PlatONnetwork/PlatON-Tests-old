# -*- coding: utf-8 -*-


from client_sdk_python import Web3
from common.connect import connect_web3
from utils.platon_lib.ppos_wyq import Ppos
from conf import  setting as conf
import time
from common import log
from common.load_file import LoadFile, get_node_info

node_yml_path = conf.PPOS_NODE_YML
node_info = get_node_info(node_yml_path)
rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get(
    'collusion')
rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get(
    'nocollusion')

address = Web3.toChecksumAddress(conf.ADDRESS)
privatekey = conf.PRIVATE_KEY
account_list = conf.account_list
privatekey_list = conf.privatekey_list
chainid = 101


ppos_noconsensus_1 = Ppos(rpc_list[0], account_list[0], chainid, privatekey=privatekey_list[0])


config_json_path = conf.PLATON_CONFIG_PATH


data = LoadFile (config_json_path).get_data ()
ExpectedMinutes = data['EconomicModel']['Common']['ExpectedMinutes']
Interval = data['EconomicModel']['Common']['Interval']
PerRoundBlocks = data['EconomicModel']['Common']['PerRoundBlocks']
ValidatorCount = data['EconomicModel']['Common']['ValidatorCount']
Consensuswheel = (ExpectedMinutes * 60) // (Interval * PerRoundBlocks * ValidatorCount)
ConsensusSize = Consensuswheel * (Interval * PerRoundBlocks * ValidatorCount)



def getCandidateList():
    """
    获取实时验证人的nodeID list
    """
    msg = ppos_noconsensus_1.getCandidateList()
    recive_list = msg.get("Data")
    nodeid_list = []
    if recive_list is None:
        return recive_list
    else:
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
    return nodeid_list


def getVerifierList():
    """
    查询当前结算周期的nodeID list
    """
    msg = ppos_noconsensus_1.getVerifierList()
    recive_list = msg.get("Data")
    nodeid_list = []
    if recive_list is None:
        return recive_list
    else:
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
    return nodeid_list


def getValidatorList():
    """
    查询当前共识轮的nodeID list
    """
    msg = ppos_noconsensus_1.getVerifierList()
    recive_list = msg.get("Data")
    nodeid_list = []
    if recive_list is None:
        return recive_list
    else:
        for node_info in recive_list:
            nodeid_list.append(node_info.get("NodeId"))
    return nodeid_list



def get_block_number(w3,settlement=ConsensusSize):
    """
    :param settlement: 结算周期的块高
    :return:
    """
    current_block = w3.eth.blockNumber
    digital_block = settlement - (current_block % settlement)
    next_cycle_block = current_block + digital_block
    log.info ('当前块高：{} ，离下个结算周期的块高：{}'.format (current_block,next_cycle_block))
    while 1:
        current_block = w3.eth.blockNumber
        differ_block = settlement - (current_block % settlement)
        log.info ('当前块高度：{}，还差块高：{}'.format ((current_block),differ_block))
        if current_block > next_cycle_block :
            break
        time.sleep(20)
        current_block_after = w3.eth.blockNumber
        if current_block_after == current_block:
            log.info('区块不增长,块高：{}'.format(current_block_after))
            raise Exception('区块不增长,块高：{}'.format(current_block_after))




# if __name__ == '__main__':
#     getCandidateList()