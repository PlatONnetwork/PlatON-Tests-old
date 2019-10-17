import pytest
from common import download
from environment.env import create_env


def pytest_addoption(parser):
    parser.addoption("--platon_url", action="store",  help="platon_url: url to download platon bin")
    parser.addoption("--nodeFile", action="store",  help="nodeFile: the node config file")
    parser.addoption("--accountFile", action="store", help="accountFile: the accounts file")
    parser.addoption("--initChain", action="store_true", default=True, dest="initChain", help="nodeConfig: default to init chain data")
    parser.addoption("--installDependency", action="store_true", default=False, dest="installDependency", help="installDependency: default do not install dependencies")
    parser.addoption("--installSuperVisor", action="store_true", default=False, dest="installSuperVisor", help="installSuperVisor: default do not install supervisor service")

# py.test test_start.py -s --concmode=asyncnet --nodeFile "deploy/4_node.yml" --accountFile "deploy/accounts.yml" --initChain
# py.test 'tests/chain/test_chaininfo.py' --nodeFile "deploy/node/test_chaininfo.yml" --accountFile "deploy/accounts.yml --alluredir="report/allure"
@pytest.fixture(scope="session", autouse=False)
def global_test_env(request):
    node_file = request.config.getoption("--nodeFile")
    account_file = request.config.getoption("--accountFile")
    init_chain = request.config.getoption("--initChain")
    install_dependency = request.config.getoption("--installDependency")
    install_supervisor = request.config.getoption("--installSuperVisor")
    plant_url = request.config.getoption("--platon_url")
    if plant_url:
        download.download_platon(plant_url)
    env = create_env(node_file, account_file, init_chain, install_dependency, install_supervisor)

    yield env

    # todo
    env.shutdown()


