import pytest
import allure
from copy import copy
import time
from common.log import log
import json


@pytest.fixture(scope="function", autouse=True)
def stop_env(global_test_env):
    global_test_env.stop_all()


@pytest.fixture(scope="module", autouse=True)
def reset_env(global_test_env):
    cfg = copy(global_test_env.cfg)
    yield
    log.info("reset deploy.................")
    global_test_env.cfg = cfg
    global_test_env.deploy_all()


@allure.title("不初始化启动节点和不同创世文件的节点互连")
@pytest.mark.P0
def test_no_init_no_join_chain(global_test_env):
    global_test_env.deploy_all()
    test_node = copy(global_test_env.get_a_normal_node())
    test_node.clean()
    new_cfg = copy(global_test_env.cfg)
    new_cfg.init_chain = False
    test_node.cfg = new_cfg
    test_node.deploy_me(genesis_file=None)
    test_node.admin.addPeer(global_test_env.get_rand_node().enode)
    time.sleep(5)
    assert test_node.web3.net.peerCount == 0, "连接节点数有增加"


@allure.title("测试部署单节点私链,同步单节点的区块")
@pytest.mark.P0
def test_build_one_node_privatechain(global_test_env):
    test_node = copy(global_test_env.get_a_normal_node())
    genesis_data = global_test_env.genesis_config
    genesis_data['config']['cbft']["initialNodes"] = [{"node": test_node.enode, "blsPubKey": test_node.blspubkey}]
    file = global_test_env.cfg.node_tmp+"/{}.json".format(test_build_one_node_privatechain.__name__)
    with open(file, "w+", encoding="UTF-8") as f:
        f.write(json.dumps(genesis_data, indent=4))
    test_node.deploy_me(file)
    time.sleep(5)
    assert test_node.block_number > 0, "区块高度没有增长"
    join_node = copy(global_test_env.get_rand_node())
    join_node.deploy_me(file)
    join_node.admin.addPeer(test_node.enode)
    time.sleep(5)
    assert join_node.block_number > 0, "区块高度没有增长"


@allure.title("测试不同initnode创始文件之间节点互连")
@pytest.mark.P0
def test_init_diff_genesis_join_chain(global_test_env):
    global_test_env.deploy_all()
    test_node = copy(global_test_env.get_a_normal_node())
    test_node.deploy_me(global_test_env.cfg.genesis_file)
    test_node.admin.addPeer(global_test_env.get_rand_node().enode)
    time.sleep(5)
    assert test_node.web3.net.peerCount == 0
