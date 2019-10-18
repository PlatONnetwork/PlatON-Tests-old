import allure
import pytest

from common.log import log
from common.connect import runCMDBySSH

#作用域设置为module，自动运行
from conf.settings import NODE_FILE
# from environment import test_env_impl


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
    for i in range(len(returnList)):
        print("序号：%s   值：%s" % (i + 1, returnList[i]))
    oldCounts = len(returnList) - 1

    remoteKeyFile = node.remoteKeystoreDir + "/key.pri"
    node.uploadFile("./deploy/key.pri", remoteKeyFile)

    log.info("import key, {}:{}".format(node.host, node.port))
    runCMDBySSH(node.ssh, "{} account import {} --datadir {}".format(node.remoteBinFile, remoteKeyFile, node.remoteDataDir), "88888888", "88888888")

    returnList2 = runCMDBySSH(node.ssh, "{} account list --datadir {}".format(node.remoteBinFile, node.remoteDataDir))
    for i in range(len(returnList)):
        print("序号：%s   值：%s" % (i + 1, returnList[i]))

    newCounts = len(returnList2) - 1


    assert oldCounts + 1 == newCounts


'''
查看账号，指定datadir
'''
def test_account_list(account_env):
    # env = global_test_env
    # node = env.get_rand_node()

    node, env = account_env

    returnList1 = runCMDBySSH(node.ssh, "platon account list --datadir {}".format(node.remoteDataDir))

    counts1 = len(returnList1) - 1

    returnList2 = runCMDBySSH(node.ssh, "platon account list --keystore {}".format(node.remoteKeystoreDir))
    counts2 = len(returnList2) - 1

    assert  counts1 == counts2