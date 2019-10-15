import pytest

from global_var import initGlobal
from test_env_impl import TestEnvironment
import requests
import settings
import os
import shutil
import tarfile


@pytest.fixture(scope="module")
def consensus_test_env(global_test_env):
    with open("/etc/passwd") as f:
        yield f.readlines()


def pytest_addoption(parser):
    parser.addoption("--platon_url", action="store",  help="platon_url: url to download platon bin")
    parser.addoption("--nodeFile", action="store",  help="nodeFile: the node config file")
    parser.addoption("--accountFile", action="store", help="accountFile: the accounts file")
    parser.addoption("--initChain", action="store_true", default=False, dest="initChain", help="nodeConfig: default to init chain data")
    parser.addoption("--startAll", action="store_true", default=False, dest="startAll", help="startAll: default to start all nodes")
    parser.addoption("--httpRpc", action="store_true", default=False, dest="httpRpc", help="httpRpc: default to HTTP PRC")
    parser.addoption("--installDependency", action="store_true", default=False, dest="installDependency", help="installDependency: default do not install dependencies")
    parser.addoption("--installSuperVisor", action="store_true", default=False, dest="installSuperVisor", help="installSuperVisor: default do not install supervisor service")

# py.test test_start.py -s --concmode=asyncnet --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain --startAll --httpRpc
@pytest.fixture(scope="session", autouse=True)
def global_test_env(request):
    initGlobal()

    nodeFile = request.config.getoption("--nodeFile")
    accountFile = request.config.getoption("--accountFile")
    initChain = request.config.getoption("--initChain")
    startAll = request.config.getoption("--startAll")
    isHttpRpc = request.config.getoption("--httpRpc")
    installDependency = request.config.getoption("--installDependency")
    installSuperVisor = request.config.getoption("--installSuperVisor")
    plant_url = request.config.getoption("--platon_url")
    if plant_url:
        download_platon(plant_url)
    env = create_env_impl(settings.PLATON_BIN_FILE,nodeFile,'global', accountFile, initChain, startAll, isHttpRpc, installDependency, installSuperVisor)

    yield env

    #todo
    #env.shutdown()

@pytest.fixture(scope="function")
def custom_test_env():
    def _custom_test_env(conf):
        binFile = conf.get("binFile")
        nodeFile = conf.get("nodeFile")
        genesisFile = conf.get("genesisFile")
        staticNodeFile = conf.get("staticNodeFile")
        accountFile = conf.get("accountFile")
        initChain = conf.get("initChain")
        startAll = conf.get("startAll")
        isHttpRpc = conf.get("isHttpRpc")
        return create_env_impl(binFile, nodeFile,  genesisFile, staticNodeFile, accountFile, initChain, startAll, isHttpRpc)
    yield _custom_test_env
   # _custom_test_env.shutdown()




def create_env_impl(binfile,nodeFile,confdir, accountFile,initChain=True, startAll=True, isHttpRpc=True, installDependency=False, installSuperVisor=False):
    env = TestEnvironment(binfile,nodeFile,confdir,accountFile,initChain,startAll,isHttpRpc,installDependency,installSuperVisor)
    print(env.installDependency)
    print(env.installSuperVisor)
    env.deploy_all()
    env.start_all()
    return env


def download_platon(download_url: 'str', path=settings.PLATON_BIN_FILE):
    """

    :param download_url: 新包下载地址
    :param path: platon相对路径
    :return:

    """
    packge_name = download_url.split('/')[-1][:-7]
    platon_path = os.path.abspath(path)
    platon_tar_path = os.path.join(platon_path, 'platon.tar.gz')
    extractall_path = os.path.join(platon_path,packge_name)
    # 下载tar.gz压缩包
    resp = requests.get(url=download_url, headers={
                        'Authorization': 'Basic cGxhdG9uOlBsYXRvbjEyMyE='})
    data = resp.content
    with open(platon_tar_path, 'wb') as f:
        f.write(data)
    f.close()

    # 解压
    tar = tarfile.open(platon_tar_path)
    tar.extractall(path=platon_path)
    tar.close()
    for filename in os.listdir(extractall_path):
        print(filename)
        if filename == "linux":
            shutil.copyfile(os.path.join(extractall_path, 'linux', 'platon'),path)
    else:
        shutil.copyfile(os.path.join(extractall_path, 'platon'),path)
    # 删除下载、解压文件
    os.remove(platon_tar_path)
    print(extractall_path)
    try:
        shutil.rmtree(extractall_path)
    except:
        rmtree(extractall_path)

def rmtree(top):
    import stat
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)
