import pytest

from global_var import initGlobal
from test_env_impl import TestEnvironment


@pytest.fixture(scope="module")
def consensus_test_env(global_test_env):
    with open("/etc/passwd") as f:
        yield f.readlines()


def pytest_addoption(parser):
    parser.addoption("--binFile", action="store", default="platon", help="binFile: the platon binary file")
    parser.addoption("--nodeFile", action="store",  help="nodeFile: the node config file")
    parser.addoption("--accountFile", action="store", help="accountFile: the node config file")
    parser.addoption("--initChain", action="store", default=True, help="nodeConfig: the node config file")
    parser.addoption("--startAll", action="store", default=True, help="startAll: the node config file")
    parser.addoption("--isHttpRpc", action="store", default=True, help="isHttpRpc: the node config file")
    parser.addoption("--installDependency", action="store", default=False, help="installDependency: the node config file")
    parser.addoption("--installSuperVisor", action="store", default=False, help="intallSuperVisor: the node config file")


# py.test test_start.py -s --concmode=asyncnet --binFile "deploy/platon" --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain True --startAll True --isHttpRpc True --installDependency True --installSuperVisor True
@pytest.fixture(scope="session", autouse=True)
def global_test_env(request):
    '''
    'binFile', 'nodeConfigFile', 'collusionNodeList', 'bootstrapNodeList', 'normalNodeList', 'cbftConfigFile', 'cbftConfig', 'accountConfigFile', 'accountConfig', 'genesisFile', 'genesisConfig', 'staticNodeFile', 'initChain', 'startAll', 'isHttpRpc')
    :param request:
    :return:
    '''
    initGlobal()

    binFile = request.config.getoption("--binFile")
    nodeFile = request.config.getoption("--nodeFile")
    accountFile = request.config.getoption("--accountFile")
    initChain = request.config.getoption("--initChain")== "True"
    startAll = request.config.getoption("--startAll")== "True"
    isHttpRpc = request.config.getoption("--isHttpRpc") == "True"
    installDependency = request.config.getoption("--installDependency")== "True"
    installSuperVisor = request.config.getoption("--installSuperVisor")== "True"


    env = create_env_impl(binFile, nodeFile, accountFile, initChain, startAll, isHttpRpc, installDependency, installSuperVisor)

    yield env

    #todo
    #env.shutdown()





def create_env_impl(binFile, nodeFile, accountFile, initChain=True, startAll=True, isHttpRpc=True, installDependency=False, installSuperVisor=False):
    env = TestEnvironment()
    env.binFile = binFile
    env.nodeFile = nodeFile
    env.accountFile = accountFile
    env.initChain = initChain
    env.startAll = startAll
    env.isHttpRpc = isHttpRpc
    env.installDependency = installDependency
    env.installSuperVisor = installSuperVisor

    print(env.installDependency)
    print(env.installSuperVisor)
    env.deploy_all()
    env.startAll()

    return env
