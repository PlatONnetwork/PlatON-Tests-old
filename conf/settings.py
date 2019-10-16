# 项目基本路径
import os

BASE_DIR = os.path.abspath(os.getcwd())

# 部署目录
from concurrent.futures.thread import ThreadPoolExecutor

DEPLOY_PATH = r"lvxiaoyi_test"

# CMD_FOR_HTTP = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --rpc --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --rpcport {} > {}/nohup.out 2>&1 &'''
# CMD_FOR_WS = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --ws --wsorigins "*" --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --wsaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --wsport {} > {}/nohup.out 2>&1 &'''

PLATON_BIN_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/platon"))
GENESIS_TEMPLATE_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/genesis_template.json"))
# GENESIS_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/genesis.json"))

CONFIG_JSON_TEMPLATE_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/config_template.json"))
# STATIC_NODE_FILE = os.path.abspath(os.path.join(BASE_DIR, 'deploy/template/static-nodes.json'))
SUPERVISOR_TEMPLATE_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/supervisor_template.conf"))
# LOCAL_TMP_FILE_ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "deploy/tmp"))

class Conf:
    def __init__(self, dir):
        path = '{}/deploy/{}'.format(BASE_DIR, dir)
        if not os.path.exists(path):
            os.makedirs(path)
        self.GENESIS_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/{}/genesis.json".format(dir)))
        self.CONFIG_JSON_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/{}/config.json".format(dir)))
        self.STATIC_NODE_FILE = os.path.abspath(os.path.join(BASE_DIR, 'deploy/{}/static-nodes.json'.format(dir)))
        self.SUPERVISOR_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/{}/supervisor.conf".format(dir)))
        self.LOCAL_TMP_FILE_ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "deploy/{}/tmp".format(dir)))


NODE_FILE=os.path.abspath(os.path.join(BASE_DIR, "../deploy/4_node.yml"))