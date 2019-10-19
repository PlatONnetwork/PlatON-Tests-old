import time

import allure
import pytest
from client_sdk_python.eth import Eth
from eth_utils import is_integer

from common.log import log
from common.connect import run_ssh_cmd
from client_sdk_python.admin import Admin

#作用域设置为module，自动运行
from conf.settings import NODE_FILE
# from environment import test_env_impl


# py.test tests/cmd/account/test_account.py -s --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain --startAll

class AccountEnv:
    __slots__ = ('remote_pwd_file', 'remote_account_address', 'remote_account_file', 'remote_key_file')

@pytest.fixture(scope='module',autouse=False)
def account_env(global_test_env):
    log.info("module account begin.................................")

    env = global_test_env
    node = env.get_rand_node()
    log.info("Node::::::::::::::::::::::::::::::{}".format(node))

    remote_pwd_file = node.remote_node_path + "/password.txt"
    node.upload_file("./deploy/keystore/password.txt", remote_pwd_file)

    remote_account_file = node.remote_keystore_dir +"/UTC--2019-10-15T10-27-31.520865283Z--c198603d3793c11e5362c8564a65d3880bae341b"
    log.info("remote_account_file::P{}".format(remote_account_file))
    node.upload_file("./deploy/keystore/UTC--2019-10-15T10-27-31.520865283Z--c198603d3793c11e5362c8564a65d3880bae341b", remote_account_file)

    remote_key_file = node.remote_keystore_dir + "/key.pri"
    node.upload_file("./deploy/key.pri", remote_key_file)

    account_env = AccountEnv()
    account_env.remote_pwd_file = remote_pwd_file
    account_env.remote_account_file = remote_account_file
    account_env.remote_key_file = remote_key_file
    account_env.remote_account_address = "c198603d3793c11e5362c8564a65d3880bae341b"

    yield node, account_env

    log.info("module account end.................................")
    # node.deleteRemoteFile(remote_pwd_file)
    # node.deleteRemoteFile(remote_pwd_file)
    # node.deleteRemoteFile(remote_pwd_file)


'''
新建账号，指定密码文件
'''
def test_account_new_with_pwd_file(account_env):
    node, env = account_env
    returnList = run_ssh_cmd(node.ssh, "{} account list --datadir {}".format(node.remote_bin_file, node.remote_data_dir))
    oldCounts = len(returnList) - 1

    run_ssh_cmd(node.ssh, "{} account new --datadir {}  --keystore {} --password {}".format(node.remote_bin_file,
                                                                                            node.remote_data_dir,
                                                                                            node.remote_keystore_dir,
                                                                                            env.remote_pwd_file))

    returnList2 = run_ssh_cmd(node.ssh, "{} account list --datadir {}".format(node.remote_bin_file, node.remote_data_dir))
    newCounts = len(returnList2) - 1
    assert oldCounts + 1 == newCounts



'''
修改账号密码，指定keystore
'''
def test_account_update(account_env):
    node, env = account_env
    run_ssh_cmd(node.ssh, "{} account update {} --keystore {}".format(node.remote_bin_file, env.remote_account_address, node.remote_keystore_dir), "88888888", "88888888", "88888888")
    pass


'''
导入账号，不指定密码文件，指定datadir
'''
def test_account_import(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env

    returnList = run_ssh_cmd(node.ssh, "{} account list --datadir {}".format(node.remote_bin_file, node.remote_data_dir))
    oldCounts = len(returnList) - 1

    remote_key_file = node.remote_keystore_dir + "/key.pri"
    node.upload_file("./deploy/key.pri", remote_key_file)

    log.info("import key, {}:{}".format(node.host, node.p2p_port))
    run_ssh_cmd(node.ssh, "{} account import {} --datadir {}".format(node.remote_bin_file, remote_key_file, node.remote_data_dir), "88888888", "88888888")

    returnList2 = run_ssh_cmd(node.ssh, "{} account list --datadir {}".format(node.remote_bin_file, node.remote_data_dir))

    newCounts = len(returnList2) - 1


    assert oldCounts + 1 == newCounts


'''
查看账号，指定datadir
'''
def test_account_list(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env


    returnList1 = run_ssh_cmd(node.ssh, "{} account list --datadir {}".format(node.remote_bin_file, node.remote_data_dir))

    counts1 = len(returnList1) - 1

    returnList2 = run_ssh_cmd(node.ssh, "{} account list --keystore {}".format(node.remote_bin_file, node.remote_keystore_dir))
    counts2 = len(returnList2) - 1

    assert  counts1 == counts2


'''
platon attach http / ws
'''
def test_attach_http(account_env):
    node, env = account_env

    blockNumber = node.run_ssh("{} attach {} --exec platon.blockNumber".format(node.remote_bin_file, node.url))

    bn = int(blockNumber[0])

    assert is_integer(bn)
    assert bn > 0


'''
platon attach http / ws
'''
def test_copydb(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    # copy deploy data to bak
    bakremote_data_dir = node.remote_node_path + "/data_bak"
    run_ssh_cmd(node.ssh, "sudo cp -r {} {}".format(node.remote_data_dir, bakremote_data_dir))

    # remove original data
    run_ssh_cmd(node.ssh, "sudo rm -rf {}/platon".format(node.remote_data_dir))
    run_ssh_cmd(node.ssh, "sudo rm -rf {}/chaindata".format(node.remote_data_dir))

    # re-init
    run_ssh_cmd(node.ssh, "{} init {} --datadir {}".format(node.remote_bin_file, node.remote_genesis_file, node.remote_data_dir))

    # copyDb from bak
    run_ssh_cmd(node.ssh, "{} copydb {}/platon/chaindata/ {}/platon/snapshotdb/ --datadir {}".format(node.remote_bin_file, bakremote_data_dir, bakremote_data_dir, node.remote_data_dir))

    node.start(False)

    blockNumber = node.run_ssh("{} attach {} --exec platon.blockNumber".format(node.remote_bin_file, node.url))
    bn = int(blockNumber[0])

    assert is_integer(bn)
    assert bn > 0


def test_dump_block(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    # dump
    returnList = run_ssh_cmd(node.ssh, "sudo {} --datadir {} dump 0".format(node.remote_bin_file, node.remote_data_dir))

    node.start(False)

    assert len(returnList) == 0


def test_dump_config(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    # dump
    returnList = run_ssh_cmd(node.ssh, "{} --nodekey {} --cbft.blskey {} dumpconfig".format(node.remote_bin_file, node.remote_nodekey_file, node.remote_blskey_file))
    assert returnList[0].strip()=='[Eth]'


def test_export_import_preimages(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    # dump
    exportList = run_ssh_cmd(node.ssh, "sudo {} export-preimages exportPreImage --datadir {}".format(node.remote_bin_file, node.remote_data_dir))
    for i in range(len(exportList)):
        log.info("序号：{}   结果：{}".format(i, exportList[i]))

    time.sleep(1)

    importList = run_ssh_cmd(node.ssh, "sudo {} import-preimages exportPreImage --datadir {}".format(node.remote_bin_file, node.remote_data_dir))
    node.start(False)

    for i in range(len(importList)):
        log.info("序号：{}   结果：{}".format(i, importList[i]))

    assert len(exportList) == 0
    assert len(importList) == 0


def test_license(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]

    returnList = run_ssh_cmd(node.ssh, "{} license".format(node.remote_bin_file))
    # for i in range(len(returnList)):
    #     log.info("序号：{}   结果：{}".format(i, returnList[i]))

    assert returnList[0].strip()=="platon is free software: you can redistribute it and/or modify"

def test_version(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]

    returnList = run_ssh_cmd(node.ssh, "{} version".format(node.remote_bin_file))
    # for i in range(len(returnList)):
    #     log.info("序号：{}   结果：{}".format(i, returnList[i]))

    assert returnList[0].strip()=="Platon"
    assert "Version:" in returnList[1]


def test_config(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    returnList = run_ssh_cmd(node.ssh, "sed -i 's/\"NetworkId\": 1/\"NetworkId\": 111/g' {}".format(node.remote_config_file))

    node.start(False)


    ret = node.admin.nodeInfo
    #print(ret)
    assert  ret["protocols"]["platon"]["network"] == 111



def no_test_removedb(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    returnList = run_ssh_cmd(node.ssh, "{} removedb --datadir {}".format(node.remote_bin_file, node.remote_data_dir, "y", "y"))
    for i in range(len(returnList)):
        log.info("序号：{}   结果：{}".format(i, returnList[i]))

    node.start(False)
    #assert returnList[0].strip()=="platon is free software: you can redistribute it and/or modify"