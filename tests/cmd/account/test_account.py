import allure
import pytest

from common.log import log
from common.connect import runCMDBySSH

#作用域设置为module，自动运行
from conf.settings import NODE_FILE
from environment import test_env_impl

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
新建账号，不指定密码文件
'''
def test_account_new(account_env):
    node, env = account_env


    #returnList = runCMDBySSH(node.ssh, "find {} -name UTC--* | wc - l".format(node.remoteKeystoreDir))
    #oldCounts = int(returnList[0].strip())

    returnList = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    oldCounts = len(returnList) -1

    runCMDBySSH(node.ssh, "{} account new --datadir {}  --keystore {}".format(node.remoteBinFile, node.remoteDataDir, node.remoteKeystoreDir), "88888888", "88888888")

    #returnList2 = runCMDBySSH(node.ssh, "find {} -name UTC--* | wc - l".format(node.remoteKeystoreDir))
    #assert  oldCounts + 1 == int(returnList2[0].strip())

    returnList2 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    newCounts = len(returnList2) -1
    assert  oldCounts + 1 == newCounts


'''
新建账号，指定密码文件
'''
def test_account_new_with_pwd_file(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env

    #returnList = runCMDBySSH(node.ssh, "find {} -name UTC--* | wc - l".format(node.remoteKeystoreDir))
    #oldCounts = int(returnList[0].strip())
    returnList = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    oldCounts = len(returnList) - 1

    # remotePwdFile = node.remoteDeployDir + "/password.txt"
    # node.uploadFile("./deploy/keystore/password.txt", remotePwdFile)
    # runCMDBySSH(node.ssh, "{} account new --datadir {}  --keystore {} --password {}".format(node.remoteBinFile, node.remoteDataDir, node.remoteKeystoreDir, remotePwdFile))
    runCMDBySSH(node.ssh, "{} account new --datadir {}  --keystore {} --password {}".format(node.remoteBinFile,
                                                                                            node.remoteDataDir,
                                                                                            node.remoteKeystoreDir,
                                                                                            env.remotePwdFile))

    #returnList2 = runCMDBySSH(node.ssh, "find {} -name UTC--* | wc - l".format(node.remoteKeystoreDir))
    #assert  oldCounts + 1 == int(returnList2[0].strip())
    returnList2 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    newCounts = len(returnList2) - 1
    assert oldCounts + 1 == newCounts

