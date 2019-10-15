import pytest
from environment.test_env_impl import TestEnvironment, create_env_impl
import requests
from conf.settings import PLATON_BIN_FILE
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
@pytest.fixture(scope="session", autouse=False)
def global_test_env(request):
    nodeFile = request.config.getoption("--nodeFile")
    accountFile = request.config.getoption("--accountFile")
    initChain = request.config.getoption("--initChain")
    _ = request.config.getoption("--startAll")
    _ = request.config.getoption("--httpRpc")
    installDependency = request.config.getoption("--installDependency")
    installSuperVisor = request.config.getoption("--installSuperVisor")
    plant_url = request.config.getoption("--platon_url")
    if plant_url:
        download_platon(plant_url)
    env = create_env_impl(nodeFile, accountFile, init_chain=initChain, install_supervisor=installDependency, install_dependency=installSuperVisor)

    yield env

    #todo
    #env.shutdown()

 def custom_test_env():
    def _custom_test_env(conf):
        _ = conf.get("binFile")
        nodeFile = conf.get("nodeFile")
        genesisFile = conf.get("genesisFile")
        accountFile = conf.get("accountFile")
        initChain = conf.get("initChain")
        _ = conf.get("startAll")
        _ = conf.get("isHttpRpc")
        return create_env_impl(node_file=nodeFile,  genesis_file=genesisFile, account_file=accountFile, init_chain=initChain)
    yield _custom_test_env
   # _custom_test_env.shutdown()


def download_platon(download_url: 'str', path=PLATON_BIN_FILE):
    """
    :param download_url: 新包下载地址
    :param path: platon放置目录
    :return:
    """

    packge_name = download_url.split('/')[-1][:-7]
    platon_path = os.path.abspath(path)
    platon_tar_file = os.path.join(platon_path, 'platon.tar.gz')
    extractall_path = os.path.join(platon_path, packge_name)

    if not os.path.exists(platon_path):
        os.makedirs(platon_path)

    # download 
    resp = requests.get(url=download_url)
    with open(platon_tar_file, 'wb') as f:
        f.write(resp.content)
    f.close()

    # Extract files
    tar = tarfile.open(platon_tar_file)
    tar.extractall(path=platon_path)
    tar.close()

    # copy file
    shutil.copy(os.path.join(extractall_path, 'platon'), platon_path)
        
    # remove directory and file
    for root, dirs, files in os.walk(extractall_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(extractall_path) 
    os.remove(platon_tar_file)



if __name__ == "__main__":
    download_platon("http://192.168.18.31:8085/ci/packages/PlatON/495/platon-ubuntu-amd64-0.7.2.2.tar.gz")