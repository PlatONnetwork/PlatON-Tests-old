import time

import allure
import pytest
from client_sdk_python.eth import Eth
from eth_utils import is_integer

from common.log import log
from common.connect import runCMDBySSH
from client_sdk_python.admin import Admin

#作用域设置为module，自动运行
from conf.settings import NODE_FILE
from environment import test_env_impl


# py.test tests/cmd/account/test_account.py -s --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain --startAll

class AccountEnv:
    __slots__ = ('remotePwdFile', 'remoteAccountAddress', 'remoteAccountFile', 'remoteKeyFile')

@pytest.fixture(scope='module',autouse=False)
def account_env(global_test_env):
    log.info("module account begin.................................")

    env = global_test_env
    node = env.get_rand_node()
    log.info("Node::::::::::::::::::::::::::::::{}".format(node))

    remotePwdFile = node.remoteDeployDir + "/password.txt"
    node.uploadFile("./deploy/keystore/password.txt", remotePwdFile)

    remoteAccountFile = node.remoteKeystoreDir +"/UTC--2019-10-15T10-27-31.520865283Z--c198603d3793c11e5362c8564a65d3880bae341b"
    node.uploadFile("./deploy/keystore/UTC--2019-10-15T10-27-31.520865283Z--c198603d3793c11e5362c8564a65d3880bae341b", remoteAccountFile)

    remoteKeyFile = node.remoteKeystoreDir + "/pri.key"
    node.uploadFile("./deploy/key.pri", remoteKeyFile)

    account_env = AccountEnv()
    account_env.remotePwdFile = remotePwdFile
    account_env.remoteAccountFile = remoteAccountFile
    account_env.remoteKeyFile = remoteKeyFile
    account_env.remoteAccountAddress = "c198603d3793c11e5362c8564a65d3880bae341b"

    yield node, account_env

    log.info("module account end.................................")
    node.deleteRemoteFile(remotePwdFile)
    node.deleteRemoteFile(remotePwdFile)
    node.deleteRemoteFile(remotePwdFile)


'''
新建账号，指定密码文件
'''
def test_account_new_with_pwd_file(account_env):
    node, env = account_env
    returnList = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    oldCounts = len(returnList) - 1

    runCMDBySSH(node.ssh, "{} account new --datadir {}  --keystore {} --password {}".format(node.remoteBinFile,
                                                                                            node.remoteDataDir,
                                                                                            node.remoteKeystoreDir,
                                                                                            env.remotePwdFile))

    returnList2 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    newCounts = len(returnList2) - 1
    assert oldCounts + 1 == newCounts



'''
修改账号密码，指定keystore
'''
def test_account_update(account_env):
    node, env = account_env
    runCMDBySSH(node.ssh, "{} account update {} --keystore {}".format(node.remoteBinFile, env.remoteAccountAddress, node.remoteKeystoreDir), "88888888", "88888888", "88888888")
    pass


'''
导入账号，不指定密码文件，指定datadir
'''
def test_account_import(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env

    returnList = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    oldCounts = len(returnList) - 1

    remoteKeyFile = node.remoteKeystoreDir + "/key.pri"
    node.uploadFile("./deploy/key.pri", remoteKeyFile)

    log.info("import key, {}:{}".format(node.host, node.port))
    runCMDBySSH(node.ssh, "{} account import {} --datadir {}".format(node.remoteBinFile, remoteKeyFile, node.remoteDataDir), "88888888", "88888888")

    returnList2 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))

    newCounts = len(returnList2) - 1


    assert oldCounts + 1 == newCounts


'''
查看账号，指定datadir
'''
def test_account_list(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env

    returnList1 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))

    counts1 = len(returnList1) - 1

    returnList2 = runCMDBySSH(node.ssh, "{} account list --keystore {}".format(node.remoteBinFile, node.remoteKeystoreDir))
    counts2 = len(returnList2) - 1

    assert  counts1 == counts2


'''
platon attach http / ws
'''
def test_attach_http(account_env):
    node, env = account_env

    if node.rpctype == "http":
        blockNumber = runCMDBySSH(node.ssh, "{} attach http://localhost:{} --exec platon.blockNumber".format(node.remoteBinFile, node.rpcport))
    else:
        blockNumber = runCMDBySSH(node.ssh, "{} attach ws://localhost:{} --exec platon.blockNumber".format(node.remoteBinFile, node.rpcport))

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
    bakRemoteDataDir = node.remoteDeployDir + "/data_bak"
    runCMDBySSH(node.ssh, "sudo cp -r {} {}".format(node.remoteDataDir, bakRemoteDataDir))

    # remove original data
    runCMDBySSH(node.ssh, "sudo rm -rf {}/platon".format(node.remoteDataDir))
    runCMDBySSH(node.ssh, "sudo rm -rf {}/chaindata".format(node.remoteDataDir))

    # re-init
    runCMDBySSH(node.ssh,"{} init {} --datadir {}".format(node.remoteBinFile, node.remoteGenesisFile, node.remoteDataDir))

    # copyDb from bak
    runCMDBySSH(node.ssh, "{} copydb {}/platon/chaindata/ {}/platon/snapshotdb/ --datadir {}".format(node.remoteBinFile, bakRemoteDataDir, bakRemoteDataDir, node.remoteDataDir))

    node.start(False)

    if node.rpctype == "http":
        blockNumber = runCMDBySSH(node.ssh, "{} attach http://localhost:{} --exec platon.blockNumber".format(node.remoteBinFile, node.rpcport))
    else:
        blockNumber = runCMDBySSH(node.ssh, "{} attach ws://localhost:{} --exec platon.blockNumber".format(node.remoteBinFile, node.rpcport))

    bn = int(blockNumber[0])

    assert is_integer(bn)
    assert bn > 0


def test_dump_block(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    # dump
    returnList = runCMDBySSH(node.ssh,"sudo {} --datadir {} dump 0".format(node.remoteBinFile, node.remoteDataDir))

    node.start(False)

    assert len(returnList) == 0


def test_dump_config(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    # dump
    returnList = runCMDBySSH(node.ssh,"{} --nodekey {} --cbft.blskey {} dumpconfig".format(node.remoteBinFile, node.remoteNodekeyFile, node.remoteBlskeyFile))
    assert returnList[0].strip()=='[Eth]'


def test_export_import_preimages(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    # dump
    exportList = runCMDBySSH(node.ssh,"sudo {} export-preimages exportPreImage --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    for i in range(len(exportList)):
        log.info("序号：{}   结果：{}".format(i, exportList[i]))

    time.sleep(1)

    importList = runCMDBySSH(node.ssh, "sudo {} import-preimages exportPreImage --datadir {}".format(node.remoteBinFile,node.remoteDataDir))
    node.start(False)

    for i in range(len(importList)):
        log.info("序号：{}   结果：{}".format(i, importList[i]))

    assert len(exportList) == 0
    assert len(importList) == 0


def test_license(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]

    returnList = runCMDBySSH(node.ssh,"{} license".format(node.remoteBinFile))
    # for i in range(len(returnList)):
    #     log.info("序号：{}   结果：{}".format(i, returnList[i]))

    assert returnList[0].strip()=="platon is free software: you can redistribute it and/or modify"

def test_version(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]

    returnList = runCMDBySSH(node.ssh,"{} version".format(node.remoteBinFile))
    # for i in range(len(returnList)):
    #     log.info("序号：{}   结果：{}".format(i, returnList[i]))

    assert returnList[0].strip()=="Platon"
    assert "Version:" in returnList[1]


def test_config(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    returnList = runCMDBySSH(node.ssh,"sed -i 's/\"NetworkId\": 1/\"NetworkId\": 111/g' {}".format(node.remoteConfigFile))

    node.start(False)

    admin = Admin(node.connect_node())
    ret = admin.nodeInfo
    #print(ret)
    assert  ret["protocols"]["platon"]["network"] == 111



def no_test_removedb(global_test_env):
    globalEnv = global_test_env

    node = globalEnv.collusion_node_list[0]
    node.stop()

    returnList = runCMDBySSH(node.ssh,"{} removedb --datadir {}".format(node.remoteBinFile, node.remoteDataDir, "y", "y"))
    for i in range(len(returnList)):
        log.info("序号：{}   结果：{}".format(i, returnList[i]))

    node.start(False)
    #assert returnList[0].strip()=="platon is free software: you can redistribute it and/or modify"