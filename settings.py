# 项目基本路径
import os

# 部署目录
from concurrent.futures.thread import ThreadPoolExecutor

DEPLOY_PATH = r"./lvxiaoyi_test"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CMD_FOR_HTTP = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --rpc --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --rpcport {} > {}/nohup.out 2>&1 &'''
CMD_FOR_WS = '''nohup {}/platon --identity "platon" --verbosity 5 --debug --ws --wsorigins "*" --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --wsaddr 0.0.0.0 --syncmode "{}" --datadir {} --port {} --wsport {} > {}/nohup.out 2>&1 &'''

PLATON_BIN_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/platon"))
GENESIS_TEMPLATE_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/genesis_template.json"))
GENESIS_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/genesis.json"))

CONFIG_JSON_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/config.json"))
STATIC_NODE_FILE = os.path.abspath(os.path.join(BASE_DIR, 'deploy/template/static-nodes.json'))
SUPERVISOR_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/supervisor.conf"))
LOCAL_TMP_FILE_ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "deploy/tmp"))

