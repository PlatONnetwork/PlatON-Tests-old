import os

import pytest
from test_env_impl import TestEnvironment




@pytest.fixture(scope="module")
def consensus_test_env(global_test_env):
    with open("/etc/passwd") as f:
        yield f.readlines()


def pytest_addoption(parser):
    parser.addoption("--binFile", action="store", default="platon", help="binFile: the platon binary file")
    parser.addoption("--nodeFile", action="store",  help="nodeFile: the node config file")
    parser.addoption("--genesisFile", action="store", help="genesisFile: the node config file")
    parser.addoption("--staticNodeFile", action="store", help="staticNodeFile: the node config file")
    parser.addoption("--accountFile", action="store", help="accountFile: the node config file")
    parser.addoption("--initChain", action="store", default=True, help="nodeConfig: the node config file")
    parser.addoption("--startAll", action="store", default=True, help="startAll: the node config file")
    parser.addoption("--isHttpRpc", action="store", default=True, help="isHttpRpc: the node config file")

# py.test test_start.py -s --concmode=asyncnet --binFile "deploy/platon" --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --genesisFile "deploy/genesis.json" --initChain True --startAll True --isHttpRpc True
@pytest.fixture(scope="session", autouse=True)
def global_test_env(request):
    '''
    'binFile', 'nodeConfigFile', 'collusionNodeList', 'bootstrapNodeList', 'normalNodeList', 'cbftConfigFile', 'cbftConfig', 'accountConfigFile', 'accountConfig', 'genesisFile', 'genesisConfig', 'staticNodeFile', 'initChain', 'startAll', 'isHttpRpc')
    :param request:
    :return:
    '''
    binFile = request.config.getoption("--binFile")
    nodeFile = request.config.getoption("--nodeFile")
    genesisFile = request.config.getoption("--genesisFile")
    staticNodeFile = request.config.getoption("--staticNodeFile")
    accountFile = request.config.getoption("--accountFile")
    initChain = request.config.getoption("--initChain")
    startAll = request.config.getoption("--startAll")
    isHttpRpc = request.config.getoption("--isHttpRpc")

    create_env_impl(binFile, nodeFile,  genesisFile, staticNodeFile, accountFile, initChain, startAll, isHttpRpc)

    yield




def create_env_impl(binFile, nodeFile,  genesisFile, staticNodeFile, accountFile, initChain, startAll, isHttpRpc):
    env = TestEnvironment()
    env.binFile = binFile
    env.nodeFile = nodeFile
    env.genesisFile = genesisFile
    env.staticNodeFile = staticNodeFile
    env.accountFile = accountFile
    env.initChain = initChain
    env.startAll = startAll
    env.isHttpRpc = isHttpRpc

    env.deploy_all()
    env.startAll()
