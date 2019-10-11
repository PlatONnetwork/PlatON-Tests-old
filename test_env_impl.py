import json
import os
import shutil
import tarfile
import time
from concurrent.futures import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor

from common.log import log
from common.connect import connect_web3, connect_linux, runCMDBySSH, ssh_remote, sftp_remote
from common.load_file import LoadFile
from global_var import getThreadPoolExecutor
from settings import CMD_FOR_HTTP, CMD_FOR_WS, DEPLOY_PATH

TMP_LOG = "./tmp_log"
LOG_PATH = "./bug_log"

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


class Node:
    def __init__(self, id=None, host=None, port=None, username=None, password=None, blsprikey=None, blspubkey=None, nodekey=None, rpcport=None, deployDir=None, syncMode=True):
        self.id = id
        self.host = host
        self.port = port
        self.rpcport = rpcport
        self.username = username
        self.password = password
        self.blsprikey = blsprikey
        self.blspubkey = blspubkey
        self.nodekey = nodekey
        self.syncMode = syncMode
        self.deployDir = deployDir

    def initNode(self):
        self.deployDir = '{}/node-{}'.format(self.deployDir, self.port)
        self.dataDir = '{}/data'.format(self.deployDir, self.port)

        self.binFile = '{}/platon'.format(self.deployDir, self.port)
        self.genesisFile = '{}/genesis.json'.format(self.deployDir, self.port)
        self.staticNodeFile = '{}/static-nodes.json'.format(self.dataDir, self.port)
        self.cbftFile = '{}/cbft.json'.format(self.dataDir, self.port)

        # connect_ssh
        #self.ssh, self.sftp, self.transport = connect_linux(self.host, self.username, self.password, 22)
        self.ssh = ssh_remote(self.host, self.username, self.password, 22)
        #self.sftp, self.transport = sftp_remote(self.host, self.username, self.password, 22)

    def getEnodeUrl(self):
        return r"enode://" + self.id + "@" + self.host + ":" + str(self.port)

    def start(self, isHttRpc):
        if isHttRpc:
            cmd = CMD_FOR_HTTP.format(self.deployDir, self.syncMode, self.dataDir, self.port, self.rpcport, self.deployDir)
        else:
            cmd = CMD_FOR_WS.format(self.deployDir, self.syncMode, self.dataDir, self.port, self.rpcport, self.deployDir)
        runCMDBySSH(self.ssh, cmd)

        if isHttRpc:
            self.rpcurl = "http:" + self.host + "://" + self.rpcport
        else:
            self.rpcurl = "ws:" + self.host + "://" + self.rpcport

        self.web3_connector = connect_web3(self.rpcurl)

    def clean(self):
        #time.sleep(0.5)
        log.info("clean node: rm {}".format(self.host))
        runCMDBySSH(self.ssh, "rm -rf {}".format(self.deployDir))

        log.info("clean node: mkdir1 {}".format(self.host))
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.deployDir))

        log.info("clean node: mkdir2 {}".format(self.deployDir))
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.host))
        log.info("clean node。。。。。。。: {}".format(self.host))


    """
    以kill的方式停止节点，关闭后节点可以重启
    """
    def stop(self):
        runCMDBySSH(self.ssh, "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}|xargs kill" % self.port)
        time.sleep(5)
        result = runCMDBySSH(self.ssh, "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}" % self.port)
        # self.transport.close()
        if result:
            raise Exception("进程关闭失败")

    """
    以kill -9的方式停止节点，关闭后节点无法重启，只能重新部署
    """
    def destroy(self):
        runCMDBySSH(self.ssh, "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}|xargs kill -9" % self.port)
        #self.transport.close()

    def uploadBinFile(self, srcFile):
        if srcFile and os.path.exists(srcFile):
            self.sftp.put(srcFile, self.binFile)
            log.info("bin uploaded to node: {}".format(self.host))

    def uploadGenesisFile(self, srcFile):
        if srcFile and os.path.exists(srcFile):
            self.sftp.put(srcFile, self.genesisFile)
            log.info("genesis uploaded to node: {}".format(self.host))

    def uploadStaticNodeFile(self, srcFile):
        if srcFile and os.path.exists(srcFile):
            self.sftp.put(srcFile, self.staticNodeFile)
        else:
            log.info("static-node source file not found.")

    def backupLog(self):
        runCMDBySSH(self.ssh, "cd {};tar zcvf log.tar.gz ./log".format(self.deployDir))
        self.sftp.get("{}/log.tar.gz".format(self.deployDir), "{}/{}_{}.tar.gz".format(TMP_LOG, self.ip, self.port))
        runCMDBySSH(self.ssh, "cd {};rm -rf ./log.tar.gz".format(self.deployDir))
        # self.transport.close()


class Account:
    def __init__(self, address, prikey, nonce=0, balance=0):
        self.id = id
        self.address = address
        self.prikey = prikey
        self.nonce = nonce
        self.balance = balance



# @singleton
class TestEnvironment:
    __slots__ = ('binFile', 'nodeFile',  'accountFile', 'genesisFile', 'staticNodeFile', 'collusionNodeList', 'normalNodeList', 'accountConfig', 'genesisConfig', 'initChain', 'startAll', 'isHttpRpc')

    def get_all_nodes(self):
        return self.collusionNodeList+self.normalNodeList

    def deploy_all(self):
        self.parseNodeFile()
        self.parseGenesisFile()
        self.parseAccountFile()

        self.deploy_nodes(self.get_all_nodes())

    def start_all(self):
        self.start_nodes(self.get_all_nodes())

    def stop_all(self):
        self.stop_nodes(self.get_all_nodes())

    def reset_all(self):
        self.reset_nodes(self.get_all_nodes())

    def start_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(node.start))
        wait(tasks, return_when=ALL_COMPLETED)

    def deploy_nodes(self, node_list):
        tasks0 = []
        log.info("nodes inited")

        for node in node_list:
            node.initNode()
        log.info("nodes inited...")

        tasks1 = []
        if self.initChain:
            for node in node_list:
                tasks1.append(getThreadPoolExecutor().submit(lambda:node.clean()))
            if len(tasks1) > 0:
                wait(tasks1, return_when=ALL_COMPLETED)
        log.info("nodes cleaned")

        tasks = []
        for node in node_list:
            log.info("start to uploading files to node: {}".format(node.host))
            tasks.append(getThreadPoolExecutor().submit(lambda :node.uploadBinFile(self.binFile)))
            tasks.append(getThreadPoolExecutor().submit(lambda :node.uploadGenesisFile(self.genesisFile)))
            tasks.append(getThreadPoolExecutor().submit(lambda :node.uploadStaticNodeFile(self.staticNodeFile)))
        wait(tasks, return_when=ALL_COMPLETED)
        log.info("nodes uploaded")

    def stop_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(node.stop))
        wait(tasks, return_when=ALL_COMPLETED)

    def reset_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(node.stop))
        wait(tasks, return_when=ALL_COMPLETED)

        tasks2 = []
        for node in node_list:
            tasks2.append(getThreadPoolExecutor().submit(node.start))
        wait(tasks2, return_when=ALL_COMPLETED)

    def upload_files(self, node_list):
        for node in node_list:
            node.uploadBinFile(self.binFile)
            node.uploadGenesisFile(self.genesisFile)
            node.uploadStaticNodeFile(self.staticNodeFile)
            node.start()

    def parseNodeFile(self):
        nodeConfig = LoadFile(self.nodeFile).get_data()
        self.collusionNodeList = []
        self.normalNodeList = []

        for node in nodeConfig.get("collusion", []):
            #colluNode = Node(node.get("id"), node.get("host"), node.get("port"), node.get("username"), node.get("password"), node.get("blsprikey"), node.get("blspubkey"), node.get("nodekey"), node.get("rpcport"))
            colluNode = Node()
            colluNode.id = node.get("id")
            colluNode.host = node.get("host")
            colluNode.port = node.get("port")
            colluNode.rpcport = node.get("rpcport")
            colluNode.username = node.get("username")
            colluNode.password = node.get("password")
            colluNode.blsprikey = node.get("blsprikey")
            colluNode.blspubkey = node.get("blspubkey")
            colluNode.nodekey = node.get("nodekey")
            colluNode.deployDir = node.get("deplayDir")
            if not colluNode.deployDir:
                colluNode.deployDir = DEPLOY_PATH


            self.collusionNodeList.append(colluNode)
            # todo: generate static-nodes.json if staticFile is None

        for node in nodeConfig.get("nocollusion", []):
            normalNode = Node()
            normalNode.id = node.get("id")
            normalNode.host = node.get("host")
            normalNode.port = node.get("port")
            normalNode.rpcport = node.get("rpcport")
            normalNode.username = node.get("username")
            normalNode.password = node.get("password")
            normalNode.blsprikey = node.get("blsprikey")
            normalNode.blspubkey = node.get("blspubkey")
            normalNode.nodekey = node.get("nodekey")
            normalNode.deployDir = node.get("deplayDir")
            if not normalNode.deployDir:
                normalNode.deployDir = DEPLOY_PATH

            self.normalNodeList.append(normalNode)

    def parseGenesisFile(self):
        self.genesisConfig = LoadFile(self.genesisFile).get_data()
        self.genesisConfig['config']['cbft']["initialNodes"] = self.getInitNodesForGenesis()
        self.rewriteGenesisFile()

    def parseAccountFile(self):
        self.accountConfig = LoadFile(self.accountFile).get_data()

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

    def rewriteGenesisFile(self):
        """
        生成创世文件
        :param genesis_json:创世文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        log.info("重写genesis.json内容")
        with open(self.genesisFile, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.genesisConfig))

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


def create_test_env(binFile, nodeFile, genesisFile, accountFile, staticNodeFile, initChain=True, startAll=True, isHttpRPC=True):
    env = TestEnvironment()
    env.binFile = binFile
    env.nodeFile = nodeFile
    env.genesisFile = genesisFile
    env.accountFile = accountFile
    env.staticNodeFile = staticNodeFile
    env.initChain = initChain
    env.startAll = startAll
    env.isHttpRpc = isHttpRPC

    if not nodeFile:
        raise Exception("缺少node配置文件")

    if not genesisFile:
        raise Exception("缺少genesis block配置文件")

    if startAll:
        env.start_all()



