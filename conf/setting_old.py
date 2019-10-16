# 项目基本路径
import os

# 部署目录
from concurrent.futures.thread import ThreadPoolExecutor

DEPLOY_PATH = r"./trantor_test"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLATON_BIN_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/platon"))
GENESIS_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/genesis.json"))
CONFIG_JSON_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/config.json"))
STATIC_NODE_FILE = os.path.abspath(os.path.join(BASE_DIR, 'deploy/template/static-nodes.json'))
SUPERVISOR_FILE = os.path.abspath(os.path.join(BASE_DIR, "deploy/template/supervisor.conf"))
LOCAL_TMP_FILE_ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "deploy/tmp"))

ACCOUNT_FILE = os.path.abspath(
    os.path.join(BASE_DIR, 'deploy/template/UTC--2019-08-23T12-33-18.192329788Z--2e95e3ce0a54951eb9a99152a6d5827872dfb4fd'))
LOCAL_TMP_FILE_FOR_NODE = os.path.abspath(os.path.join(LOCAL_TMP_FILE_ROOT_DIR, "node"))
LOCAL_TMP_FILE_FOR_SERVER = os.path.abspath(os.path.join(LOCAL_TMP_FILE_ROOT_DIR, "server"))
LOCAL_TMP_FILE_FOR_ENV = os.path.abspath(os.path.join(LOCAL_TMP_FILE_ROOT_DIR, "env"))
LOCAL_TMP_FILE_FOR_GNENESIS = os.path.abspath(os.path.join(LOCAL_TMP_FILE_ROOT_DIR, "genesis.json"))


NODE_FILE=os.path.abspath(os.path.join(BASE_DIR, "../deploy/4_node.yml"))