import time

import allure
import pytest

from common import log
from deploy.deploy import AutoDeployPlaton
from common.connect import connect_web3
from conf import setting as conf
from common.load_file import get_f, get_node_info, get_node_list

node_yml = conf.NODE_YML
collusion_list, _ = get_node_list(node_yml)
f = int(get_f(collusion_list))
n = len(collusion_list)
auto = AutoDeployPlaton()
url_list, enode_list, nodeid_list, ip_list, _ = get_node_info(
    node_yml)["collusion"]
genesis_file = conf.GENESIS_TMP
static_node_file = conf.STATIC_NODE_FILE


def teardown_function():
    log.info("每个用例结束后都会执行")
    auto.kill_of_yaml(node_yml)


def teardown_module():
    auto.start_all_node(node_yml)


@allure.title("正常启动所有节点")
def test_start_all_node():
    """
    用例id：50
    用于测试启动所有共识节点后，检查出块情况
    """
    log.info("部署{}节点".format(n))
    auto.start_all_node(node_yml)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list]
    check_block_sync(w3_list)


def check_block_sync(w3_list):
    status = 0
    for i in range(100):
        time.sleep(0.5)
        block_list = [w3.eth.blockNumber for w3 in w3_list]
        log.info("所有节点块高：{}".format(block_list))
        max_value = max(block_list)
        min_value = min(block_list)
        if max_value - min_value <= 10:
            status = 0
            break
        else:
            status += 1
    assert status < 100, "块高不同步"


@allure.title("启动共识节点2f+1开始出块")
def test_start_mini_node():
    """
    用例id:51
    测试启动共识节点达到最低共识节点数量时，开始出块
    """
    num = int(2*f+1)
    log.info("部署{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    time.sleep(30)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list[0:num]]
    check_block_sync(w3_list)


@allure.title("正常启动所有节点,逐渐关闭f个")
def test_start_all_node_close_f():
    """
    用例id：52
    启动n个节点后，逐渐关闭f个，那么关闭节点的窗口期不出块
    """
    log.info("部署{}个节点".format(n))
    auto.start_all_node(node_yml)
    log.info("关闭{}个节点".format(f))
    auto.kill_of_list(collusion_list[0:f])
    check_block_node(url_list[f:], n)


def check_block_node(urls_list, n):
    time.sleep(10)
    w3_list = [connect_web3(url) for url in urls_list]
    log.info("查询所有节点块高")
    start = max([w3.eth.blockNumber for w3 in w3_list])
    log.info("开始块高：{}".format(start))
    log.info("sleep {}s".format(n*10))
    time.sleep(n*10)
    end = max([w3.eth.blockNumber for w3 in w3_list])
    log.info("结束块高:{}".format(end))
    assert end - start > 0, "没有出块了"


@allure.title("正常启动2f+1个节点,{t}秒后在启动一个")
@pytest.mark.parametrize('t', [50, 100, 150])
def test_start_2f1_node_and_start_one(t):
    """
    用例id：53,54,55
    先启动2f+1个，n秒后在启动一个
    """
    num = int(2*f+1)
    log.info("部署{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    log.info("sleep {}s".format(t))
    time.sleep(int(t))
    auto.start_of_list(
        collusion_list[num:num+1], genesis_file=genesis_file, static_node_file=static_node_file)
    check_block_node(url_list, n)


@allure.title("只启动2f个节点")
def test_start_2f():
    """
    用例id：56
    启动2f个节点
    """
    num = int(2*f)
    log.info("部署{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    time.sleep(4)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list[0:num]]
    log.info("查询所有节点块高")
    block_list = [w3.eth.blockNumber for w3 in w3_list]
    log.info("所有节点块高：{}".format(block_list))
    max_value = max(block_list)
    assert max_value == 0, "出块了"


@allure.title("正常启动所有节点,逐渐关闭f+1个")
def test_start_all_node_close_f_add_1():
    """
    用例id：57
    启动25个节点后，逐渐关闭f+1个，那么关闭后将不会出块
    """
    log.info("部署{}个节点".format(n))
    auto.start_all_node(node_yml)
    log.info("关闭{}个节点".format(f+1))
    auto.kill_of_list(collusion_list[0:f+1])
    url_run = url_list[f+1:]
    w3_list = [connect_web3(url) for url in url_run]
    blocknumber_list_start = [w3.eth.blockNumber for w3 in w3_list]
    log.info("获取所有运行节点块高：{}".format(blocknumber_list_start))
    log.info("sleep {}s".format((f+1)*10+5))
    time.sleep((f+1)*10+5)
    blocknumber_list_end = [w3.eth.blockNumber for w3 in w3_list]
    log.info("关闭{}秒后再次获取所有运行节点块高：{}".format((f+1)*10+5, blocknumber_list_end))
    assert blocknumber_list_start == blocknumber_list_end, "关闭{}个节点后还在出块".format(
        f+1)


@allure.title("先启动2f个节点，间隔{t}秒后再启动一个")
@pytest.mark.parametrize('t', [50, 100, 150])
def test_start_2f_after_one(t):
    """
    用例id:58,59,60
    先启动2f个节点，间隔一定时间之后再启动一个节点，查看出块情况
    """
    num = int(2*f)
    log.info("先启动{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    time.sleep(4)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list[0:num]]
    log.info("查询所有节点块高")
    block_list = [w3.eth.blockNumber for w3 in w3_list]
    log.info("所有节点块高：{}".format(block_list))
    max_value = max(block_list)
    assert max_value == 0, "启动{}个节点就开始出块了".format(2*f)
    log.info("sleep {}s".format(t))
    time.sleep(int(t))
    log.info("在启动另外1个节点")
    auto.start_of_list(
        collusion_list[num:num+1], genesis_file=genesis_file, static_node_file=static_node_file)
    check_blocknumber(url_list[:num+1], (num-1)*10, n)


@allure.title("先启动2f个节点，间隔{t}秒后启动所有节点")
@pytest.mark.parametrize('t', [50, 100, 150])
def test_start_2f_after_all(t):
    """
    用例id:63,64,65
    先启动2f个节点，间隔一定时间之后再启动未启动的所有共识节点，查看出块情况
    """
    num = int(2*f)
    log.info("先启动{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    time.sleep(4)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list[0:num]]
    log.info("查询所有节点块高")
    block_list = [w3.eth.blockNumber for w3 in w3_list]
    log.info("所有节点块高：{}".format(block_list))
    max_value = max(block_list)
    assert max_value == 0, "启动{}个节点就开始出块了".format(num)
    log.info("sleep {}s".format(t))
    time.sleep(int(t))
    log.info("在启动另外所有共识节点")
    auto.start_of_list(
        collusion_list[num:], genesis_file=genesis_file, static_node_file=static_node_file)
    check_blocknumber(url_list, (n-1)*10, n)


def check_blocknumber(url_list, number, n):
    log.info(n)
    time.sleep(20)
    w3_list = [connect_web3(url) for url in url_list]
    start_blocknumbers = [w3.eth.blockNumber for w3 in w3_list]
    log.info("开始块高：{}".format(start_blocknumbers))
    start_max_value = max(start_blocknumbers)
    log.info("sleep {}s".format(n*10))
    time.sleep(int(n*10))
    end_blocknumbers = [w3.eth.blockNumber for w3 in w3_list]
    log.info("结束块高:{}".format(end_blocknumbers))
    end_max_value = max(end_blocknumbers)
    assert end_max_value - start_max_value >= number, "出块数少于{}".format(number)


@allure.title("先启动2f个节点，30秒内不停重启另外{x}节点")
@pytest.mark.parametrize('x', [1, n-int(2*f)])
def test_up2f_after_other(x):
    """
    用例id:61,62
    """
    num = int(2*f)
    log.info("先启动{}个节点".format(num))
    auto.start_of_list(
        collusion_list[0:num], genesis_file=genesis_file, static_node_file=static_node_file)
    time.sleep(4)
    log.info("跟所有节点建立连接")
    w3_list = [connect_web3(url) for url in url_list[0:num]]
    log.info("查询所有节点块高")
    block_list = [w3.eth.blockNumber for w3 in w3_list]
    log.info("所有节点块高：{}".format(block_list))
    auto.start_of_list(
        collusion_list[num:num+x], genesis_file=genesis_file, static_node_file=static_node_file)
    i = 0
    while i <= 30:
        auto.kill_of_list(collusion_list[num:num+x])
        auto.start_of_list(collusion_list[num:num+x], is_need_init=False)
        time.sleep(5)
        i += 5
    check_blocknumber(url_list[:num+x], (num+x-2)*10, n)
