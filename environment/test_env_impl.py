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
from common.global_var import getThreadPoolExecutor

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

    def __init__(self, binFile, nodeFile,confdir, accountFile, initChain, startAll, installDependency, installSuperVisor):
        self.binFile = binFile
        self.nodeFile = nodeFile
        self.accountFile = accountFile
        self.initChain = initChain
        self.startAll = startAll
        self.installDependency = installDependency
        self.installSuperVisor = installSuperVisor
        self.collusionNodeList = []
        self.conf = Conf(confdir)
        self.parseNodeFile()
        if not os.path.exists(GENESIS_TEMPLATE_FILE):
            raise Exception("模板文件没有找到：{}".format(GENESIS_TEMPLATE_FILE))
        self.genesisConfig = LoadFile(GENESIS_TEMPLATE_FILE).get_data()
        self.account = Account(self.accountFile, self.genesisConfig['config']['chainId'])
        self.rewrite_genesisFile()

    def get_all_nodes(self):
        return self.collusionNodeList+self.normalNodeList

    def get_rand_node(self):
        return self.collusionNodeList[0]


    def deploy_all(self):
        self.rewrite_configJsonFile()
        self.rewrite_staticNodesFile()

        self.initNodes(self.get_all_nodes())

        self.generateKeyFiles(self.get_all_nodes())

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
            futureList.append(getThreadPoolExecutor().submit(lambda :node.start(self.initChain)))
            #futureList.append(getThreadPoolExecutor().submit(start, node, self.initChain))
        wait(futureList, return_when=ALL_COMPLETED)

    def initNodes(self, node_list):
        log.info("init nodes...")
        futureList = []
        for node in node_list:
            futureList.append(getThreadPoolExecutor().submit(lambda: node.initNode()))
            #futureList.append(getThreadPoolExecutor().submit(initNode, node))
        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)

    def deploy_nodes(self, node_list):
        futureList = []
        if self.installDependency:
            log.info("nodes install dependencies: {}".format(self.installDependency))
            futureList.clear()
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda: node.install_dependency()))
                #futureList.append(getThreadPoolExecutor().submit(install_dependency, node))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes clean env")
        futureList.clear()
        if self.initChain:
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda:node.clean()))
                #futureList.append(getThreadPoolExecutor().submit(clean, node))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes upload files")
        futureList.clear()
        tmp = ThreadPoolExecutor(max_workers=40)
        for node in node_list:
            log.info("node:::::::::: {}".format(node.host))
            thread_pool_exc = tmp.submit(lambda :node.uploadAllFiles())
           # thread_pool_exc = getThreadPoolExecutor().submit(lambda :node.uploadAllFiles())
            thread_pool_exc.add_done_callback(self.thread_pool_callback)
            futureList.append(thread_pool_exc)
            #futureList.append(getThreadPoolExecutor().submit(uploadAllFiles,node))

        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)
        log.info("all files uploaded")


        if self.installSuperVisor:
            log.info("nodes deploy supervisor")
            futureList.clear()
            for node in node_list:
                thread_pool_exc = getThreadPoolExecutor().submit(lambda :node.deploy_supervisor())
                thread_pool_exc.add_done_callback(self.thread_pool_callback)
                futureList.append(thread_pool_exc)
                #futureList.append(getThreadPoolExecutor().submit(deploy_supervisor, node))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)
            log.info("SuperVisor installed")

    def thread_pool_callback(self, worker):
        log.info("called thread pool executor callback function")
        worker_exception = worker.exception()
        if worker_exception:
            log.exception("Worker return exception: {}".format(worker_exception))

    def stop_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(lambda :node.stop()))
            #tasks.append(getThreadPoolExecutor().submit(stop, node))
        wait(tasks, return_when=ALL_COMPLETED)

    def reset_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(lambda :node.stop()))
            #tasks.append(getThreadPoolExecutor().submit(stop, node))
        wait(tasks, return_when=ALL_COMPLETED)

        tasks2 = []
        for node in node_list:
            tasks2.append(getThreadPoolExecutor().submit(lambda :node.start()))
            #tasks2.append(getThreadPoolExecutor().submit(start, node))
        wait(tasks2, return_when=ALL_COMPLETED)

    def parseNodeFile(self):
        nodeConfig = LoadFile(self.nodeFile).get_data()
        self.collusionNodeList = []
        self.normalNodeList = []

        for node in nodeConfig.get("collusion", []):
            colluNode = Node(self.conf, node)
            self.collusionNodeList.append(colluNode)

        for node in nodeConfig.get("nocollusion", []):
            normalNode = Node(self.conf, node)
            self.normalNodeList.append(normalNode)

    def parseAccountFile(self):
        if self.account_file:
            self.account = Account(self.account_file, self.genesis_config['config']['chainId'])

    def getInitNodesForGenesis(self):
        initNodeList = []
        for node in self.collusionNodeList:
            initNodeList.append({"node": node.getEnodeUrl(), "blsPubKey": node.blspubkey})
        return initNodeList

    def getStaticNodeList(self):
        staticNodeList = []
        for node in self.collusionNodeList:
            staticNodeList.append(node.getEnodeUrl())
        return staticNodeList

    def rewrite_genesisFile(self):
        """
        生成创世文件
        :param genesis_json:创世文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        self.genesisConfig['config']['cbft']["initialNodes"] = self.getInitNodesForGenesis()

        accounts = self.account.get_all_accounts()
        for account in accounts:
            self.genesisConfig['alloc'][account['address']] = { "balance":   str(account['balance']) }

        log.info("重写genesis.json内容")
        with open(self.conf.GENESIS_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.genesisConfig))
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
        config_data['node']['P2P']["BootstrapNodes"] = self.getStaticNodeList()

        with open(self.conf.CONFIG_JSON_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_data))
            f.close()

    def  rewrite_staticNodesFile(self):
        """
        生成节点互连文件
        :param static_nodes: 共识节点enode
        :return:
        """
        log.info("生成static-nodes.json")
        static_nodes = self.getStaticNodeList()
        with open(self.conf.STATIC_NODE_FILE, 'w', encoding='utf-8') as f:
            f.write( json.dumps(static_nodes))
            f.close()

    def generateKeyFiles(self, node_list):
        for node in node_list:
            node.generateKeyFiles()

    def generate_all_supervisor_node_conf_files(self, node_list):
        for node in node_list:
            node.generate_supervisor_node_conf_file()


    def backupAllLogs(self):
        self.backupLogs(self.collusionNodeList)
        self.backupLogs(self.normalNodeList)

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
        tar = tarfile.open("{}/{}_{}_log.tar.gz".format(LOG_PATH, self.nodeFile, t), "w:gz")
        tar.add(TMP_LOG)
        tar.close()
        print("压缩完成")
        print("开始删除缓存.....")
        shutil.rmtree(TMP_LOG)
        print("删除缓存完成")




