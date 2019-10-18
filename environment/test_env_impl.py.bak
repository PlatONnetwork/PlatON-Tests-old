import configparser
import json
import os
import shutil
import tarfile
import time
from concurrent.futures import ALL_COMPLETED, wait


from concurrent.futures.thread import ThreadPoolExecutor

from common.log import log
from common.load_file import LoadFile
from common.global_var import getThreadPoolExecutor, default_thread_pool_callback

from conf.settings import DEPLOY_PATH, PLATON_BIN_FILE,GENESIS_TEMPLATE_FILE,Conf,CONFIG_JSON_TEMPLATE_FILE,SUPERVISOR_TEMPLATE_FILE

from environment.account import Account

from environment.node import Node


TMP_LOG = "./tmp_log"
LOG_PATH = "./bug_log"

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


# @singleton
class TestEnvironment:

    def __init__(self, node_file, bin_file=None, confdir='temp', account_file=None, init_chain=True, startAll=True, install_dependency=True, install_supervisor=True):
        self.bin_file = bin_file
        self.node_file = node_file
        self.account_file = account_file
        self.init_chain = init_chain
        self.startAll = startAll
        self.install_dependency = install_dependency
        self.install_supervisor = install_supervisor
        self.collusion_node_list = []
        self.normal_node_list = []
        self.conf = Conf(confdir)
        self.parse_node_file()
        self.init_nodes(self.get_all_nodes())
        if not os.path.exists(GENESIS_TEMPLATE_FILE):
            raise Exception("模板文件没有找到：{}".format(GENESIS_TEMPLATE_FILE))
        self.genesis_config = LoadFile(GENESIS_TEMPLATE_FILE).get_data()
        self.account = None
        if self.account_file:
            self.account = Account(self.account_file, self.genesis_config['config']['chainId'])
        self.rewrite_genesisFile()

    def get_all_nodes(self):
        return self.collusion_node_list + self.normal_node_list

    def get_rand_node(self)->Node:
        return self.collusion_node_list[0]


    def deploy_all(self):
        self.rewrite_configJsonFile()
        self.rewrite_staticNodesFile()

        self.generate_key_files(self.get_all_nodes())

        self.generate_all_supervisor_node_conf_files(self.get_all_nodes())

        self.deploy_nodes(self.get_all_nodes())

    def start_all(self):
        self.start_nodes(self.get_all_nodes())

    def stop_all(self):
        self.stop_nodes(self.get_all_nodes())

    def reset_all(self):
        self.reset_nodes(self.get_all_nodes())

    def start_nodes(self, node_list):
        futureList = []
        for node in node_list:
            future = getThreadPoolExecutor().submit(lambda: node.start(self.init_chain))
            future.add_done_callback(default_thread_pool_callback)
            futureList.append(future)
        wait(futureList, return_when=ALL_COMPLETED)

    def init_nodes(self, node_list):
        log.info("init nodes...")
        futureList = []
        for node in node_list:
            future = getThreadPoolExecutor().submit(lambda: node.initNode())
            future.add_done_callback(default_thread_pool_callback)
            futureList.append(future)

        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)

    def deploy_nodes(self, node_list):
        futureList = []
        if self.install_dependency:
            log.info("nodes install dependencies: {}".format(self.install_dependency))
            futureList.clear()
            for node in node_list:
                future = getThreadPoolExecutor().submit(lambda: node.install_dependency())
                future.add_done_callback(default_thread_pool_callback)
                futureList.append(future)
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes clean env")
        futureList.clear()
        if self.init_chain:
            for node in node_list:
                future = getThreadPoolExecutor().submit(lambda: node.clean())
                future.add_done_callback(default_thread_pool_callback)
                futureList.append(future)
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes upload files")
        futureList.clear()
        for node in node_list:
            future = getThreadPoolExecutor().submit(lambda :node.uploadAllFiles())
            future.add_done_callback(default_thread_pool_callback)
            futureList.append(future)
        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)
        log.info("all files uploaded")


        if self.install_supervisor:
            log.info("nodes deploy supervisor")
            futureList.clear()
            for node in node_list:
                future = getThreadPoolExecutor().submit(lambda :node.deploy_supervisor())
                future.add_done_callback(default_thread_pool_callback)
                futureList.append(future)
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)
            log.info("SuperVisor installed")

    # def thread_pool_callback(self, worker):
    #     log.info("called thread pool executor callback function")
    #     worker_exception = worker.exception()
    #     if worker_exception:
    #         log.exception("Worker return exception: {}".format(worker_exception))

    def stop_nodes(self, node_list):
        futureList = []
        for node in node_list:
            future =getThreadPoolExecutor().submit(lambda: node.stop())
            future.add_done_callback(default_thread_pool_callback)
            futureList.append(future)
        wait(futureList, return_when=ALL_COMPLETED)

    def reset_nodes(self, node_list):
        self.stop_nodes(node_list)
        self.stop_nodes(node_list)

    def parse_node_file(self):
        nodeConfig = LoadFile(self.node_file).get_data()

        for node in nodeConfig.get("collusion", []):
            colluNode = Node(self.conf, node)
            self.collusion_node_list.append(colluNode)

        for node in nodeConfig.get("nocollusion", []):
            normalNode = Node(self.conf, node)
            self.normal_node_list.append(normalNode)

    def get_init_nodes_for_genesis(self):
        initNodeList = []
        for node in self.collusion_node_list:
            initNodeList.append({"node": node.getEnodeUrl(), "blsPubKey": node.blspubkey})
        return initNodeList

    def get_static_node_list(self):
        staticNodeList = []
        for node in self.collusion_node_list:
            staticNodeList.append(node.getEnodeUrl())
        return staticNodeList

    def rewrite_genesisFile(self):
        """
        生成创世文件
        :param genesis_json:创世文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        self.genesis_config['config']['cbft']["initialNodes"] = self.get_init_nodes_for_genesis()

        if self.account:
            accounts = self.account.get_all_accounts()
            for account in accounts:
                self.genesis_config['alloc'][account['address']] = { "balance":   str(account['balance']) }

        log.info("重写genesis.json内容")
        with open(self.conf.GENESIS_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.genesis_config, indent=4))
            f.close()

    def rewrite_configJsonFile(self):
        """
        修改启动配置文件
        :param config_json:ppos配置文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        log.info("增加种子节点到config.json配置文件")
        configJsonFile = CONFIG_JSON_TEMPLATE_FILE
        if not os.path.exists(configJsonFile):
            log.info("模板文件没有找到：{}".format(configJsonFile))
            return

        config_data = LoadFile(configJsonFile).get_data()
        config_data['node']['P2P']["BootstrapNodes"] = self.get_static_node_list()

        with open(self.conf.CONFIG_JSON_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_data, indent=4))
            f.close()

    def  rewrite_staticNodesFile(self):
        """
        生成节点互连文件
        :param static_nodes: 共识节点enode
        :return:
        """
        log.info("生成static-nodes.json")
        static_nodes = self.get_static_node_list()
        with open(self.conf.STATIC_NODE_FILE, 'w', encoding='utf-8') as f:
            f.write( json.dumps(static_nodes, indent=4))
            f.close()

    def generate_key_files(self, node_list):
        for node in node_list:
            node.generateKeyFiles()

    def generate_all_supervisor_node_conf_files(self, node_list):
        for node in node_list:
            node.generate_supervisor_node_conf_file()


    def backupAllLogs(self):
        self.backupLogs(self.collusion_node_list)
        self.backupLogs(self.normal_node_list)

    def backupLogs(self, node_list):
        self.checkLogPath()
        for node in node_list:
            node.backupLog()
        self.zipAllLog()

    def checkLogPath(self):
        if not os.path.exists(TMP_LOG):
            os.mkdir(TMP_LOG)
        else:
            shutil.rmtree(TMP_LOG)
            os.mkdir(TMP_LOG)
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

    def zipAllLog(self):
        print("开始压缩.....")
        t = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        tar = tarfile.open("{}/{}_{}_log.tar.gz".format(LOG_PATH, self.node_file, t), "w:gz")
        tar.add(TMP_LOG)
        tar.close()
        print("压缩完成")
        print("开始删除缓存.....")
        shutil.rmtree(TMP_LOG)
        print("删除缓存完成")




