import copy
import queue
import random
import threading
import time

import web3
from common import log
from common.load_file import get_node_list
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton
from utils.platon_lib.dpos import PlatonDpos, get_sleep_time

q = queue.Queue()


def stop_node(node_list, platon_dpos):
    auto = AutoDeployPlaton()
    del node_list[0]
    del node_list[9]
    del node_list[0]
    while True:
        time.sleep(random.randrange(100, 5000))
        verfier_info_list = platon_dpos.GetVerifiersList()
        num = len(verfier_info_list)
        if num <= 1:
            continue
        f = int((num - 1) / 3)
        if f < 2:
            continue
        stop_node_list = random.sample(node_list, random.randrange(1, f))
        q.put(1)
        log.info("关闭节点:{}".format(stop_node_list))
        number = platon_dpos.web3.eth.blockNumber
        sleep_time = get_sleep_time(number)
        auto.kill_of_list(stop_node_list)
        if sleep_time > 21:
            time.sleep(random.randrange(1, sleep_time - 20))
        log.info("恢复节点:{}".format(stop_node_list))
        auto.restart_list(stop_node_list)
        q.get()


def restart_node(node_list, platon_dpos):
    auto = AutoDeployPlaton()
    del node_list[0]
    del node_list[9]
    del node_list[0]
    while True:
        time.sleep(random.randrange(100, 5000))
        verfier_info_list = platon_dpos.GetVerifiersList()
        num = len(verfier_info_list)
        if num <= 1:
            f = 1
        else:
            f = int((num - 1) / 3) + 1
        stop_node_list = random.sample(node_list, random.randrange(1, f + 1))
        q.put(1)
        log.info("重启节点:{}".format(stop_node_list))
        auto.restart_list(stop_node_list)
        q.get()


if __name__ == "__main__":
    node_yml = "./deploy/node/node_061.yml"
    node_list1, node_list2 = get_node_list(node_yml)
    node_list = node_list1 + node_list2
    node_list_stop = copy.copy(node_list)
    w3 = PlatonDpos(
        node_list[0]["url"], web3.Web3().toChecksumAddress(conf.ADDRESS), conf.PASSWORD, abi=conf.DPOS_CONTRACT_ABI)
    th1 = threading.Thread(target=stop_node, args=(node_list_stop, w3))
    th1.setDaemon(True)
    th1.start()
    th2 = threading.Thread(target=restart_node, args=(node_list, w3))
    th2.setDaemon(True)
    th2.start()
    input("input q quit:")
    while q.empty():
        exit()
