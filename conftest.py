import os

import pytest

from common import log
from test_env_impl import TestEnvironment

# 项目基本路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD_FOR_HTTP = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --rpc --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --rpcport {} > {}/nohup.out 2>&1 &'''
CMD_FOR_WS = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --ws --wsorigins "*" --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --wsaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --wsport {} > {}/nohup.out 2>&1 &'''



def runCMDBySSH(ssh, cmd, password=None):
    try:
        stdin, stdout, _ = ssh.exec_command("source /etc/profile;%s" % cmd)
        if password:
            stdin.write(password+"\n")
        stdout_list = stdout.readlines()
        if len(stdout_list):
            log.info(stdout_list)
    except Exception as e:
        raise e
    return stdout_list



@pytest.fixture(scope="module")
def consensus_test_env(global_test_env):
    with open("/etc/passwd") as f:
        yield f.readlines()



@pytest.fixture(scope="session", autouse=True)
def global_test_env():
    with open("/etc/passwd") as f:
        yield f.readlines()


def create_env_impl(node_yml, genesis_json, config_json, start_all):
    # TestEnvironment.bin_url = binurl
    # TestEnvironment.node_cfg = opt.node
    # TestEnvironment.account_cfg = opt.accountCfg
    # TestEnvironment.genesis_Tmpl = opt.genesis
    # TestEnvironment.cbft_cfg = opt.cbft
    return TestEnvironment()

