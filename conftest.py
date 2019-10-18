import pytest
from common import download
from environment.env import create_env
from common.log import log


@pytest.fixture(scope="module")
def consensus_test_env(global_test_env):
    with open("/etc/passwd") as f:
        yield f.readlines()


def pytest_addoption(parser):
    parser.addoption("--tmpDir", action="store", help="tmpDir: tmp dir, default in deploy/tmp/global")
    parser.addoption("--platonUrl", action="store",  help="platonUrl: url to download platon bin")
    parser.addoption("--nodeFile", action="store",  help="nodeFile: the node config file")
    parser.addoption("--accountFile", action="store", help="accountFile: the accounts file")
    parser.addoption("--initChain", action="store_true", default=True, dest="initChain", help="nodeConfig: default to init chain data")
    parser.addoption("--installDependency", action="store_true", default=False, dest="installDependency", help="installDependency: default do not install dependencies")
    parser.addoption("--installSupervisor", action="store_true", default=False, dest="installSuperVisor", help="installSupervisor: default do not install supervisor service")

# py.test test_start.py -s --concmode=asyncnet --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain
# py.test 'tests/chain/test_chain_deploy.py' --nodeFile "deploy/node/test_chaininfo.yml" --accountFile "deploy/accounts.yml" --alluredir="report/allure" -s -v
@pytest.fixture(scope="session", autouse=False)
def global_test_env(request):
    log.info("global_test_env>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    tmp_dir = request.config.getoption("--tmpDir")
    node_file = request.config.getoption("--nodeFile")
    account_file = request.config.getoption("--accountFile")
    init_chain = request.config.getoption("--initChain")
    install_dependency = request.config.getoption("--installDependency")
    install_supervisor = request.config.getoption("--installSupervisor")
    plant_url = request.config.getoption("--platonUrl")
    if plant_url:
        download.download_platon(plant_url)
    env = create_env(tmp_dir, node_file, account_file, init_chain, install_dependency, install_supervisor)

    yield env

    # todo
    env.shutdown()


