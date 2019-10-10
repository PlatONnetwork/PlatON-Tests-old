import json
import os
import shutil
import tarfile
import threading
import time
from concurrent.futures import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor

from common import log
from common.load_file import LoadFile
from common.connect import connect_web3, connect_linux
from conftest import CMD_FOR_HTTP, CMD_FOR_WS, runCMDBySSH


TMP_LOG = "./tmp_log"
LOG_PATH = "./bug_log"


threadPool = ThreadPoolExecutor(max_workers=30)

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner




class Node:
    def __init__(self, id, host, port, username, password, blsprikey, blspubkey, nodekey, rpcport, wsport, deployDir, syncMode):
        self.id = id
        self.host = host
        self.port = port
        self.rpcport = rpcport
        self.wsport = wsport
        self.username = username
        self.password = password
        self.blsprikey = blsprikey
        self.blspubkey = blspubkey
        self.nodekey = nodekey
        self.syncMode = syncMode

    def iniNode(self):
        self.deployDir = '{}/node-{}'.format(self.deployDir, self.port)
        self.dataDir = '{}/data'.format(self.deployDir, self.port)

        if not os.path.exists(self.deployDir):
            os.makedirs(self.deployDir)
        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        self.binFile = '{}/platon'.format(self.deployDir, self.port)
        self.genesisFile = '{}/genesis.json'.format(self.deployDir, self.port)
        self.staticNodeFile = '{}/static-nodes.json'.format(self.dataDir, self.port)
        self.cbftFile = '{}/cbft.json'.format(self.dataDir, self.port)

        # connect_ssh
        self.ssh, self.sfpt, self.transport = connect_linux(self.host, self.username, self.password, 22)

    def getEnodeUrl(self):
        return r"enode://" + self.id + "@" + self.host + ":" + str(self.port)

    def start(self, isHttRpc):
        if isHttRpc:
            cmd = CMD_FOR_HTTP.format(self.deployDir, self.syncMode, self.dataDir, self.port, self.rpcport, self.deployDir)
        else:
            cmd = CMD_FOR_WS.format(self.deployDir, self.syncMode, self.dataDir, self.port, self.wsport, self.deployDir)
        runCMDBySSH(self.ssh, cmd)

        if isHttRpc:
            self.rpcurl = "http:" + self.host + "://" + self.rpcport
        else:
            self.rpcurl = "ws:" + self.host + "://" + self.rpcport

        self.web3_connector = connect_web3(self.rpcurl)

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
        self.sfpt.put(srcFile, self.binFile)
    def uploadGenesisFile(self, srcFile):
        self.sfpt.put(srcFile, self.genesisFile)
    def uploadStaticNodeFile(self, srcFile):
        self.sfpt.put(srcFile, self.staticNodeFile)
    def uploadCbftFile(self, srcFile):
        self.sfpt.put(srcFile, self.cbftFile)

    def backupLog(self):
        runCMDBySSH(self.ssh, "cd {};tar zcvf log.tar.gz ./log".format(self.deployDir))
        self.sftp.get("{}/log.tar.gz".format(self.deployDir), "{}/{}_{}.tar.gz".format(TMP_LOG, self.ip, self.port))
        runCMDBySSH(self.ssh, "cd {};rm -rf ./log.tar.gz".format(self.deployDir))
        # self.transport.close()


class Account:
    def __init__(self, address, prikey, balance):
        self.id = id
        self.address = address
        self.prikey = prikey
        self.balance = balance

@singleton
class TestEnvironment:
    __slots__ = ('binFile', 'nodeConfigFile', 'collusionNodeList', 'bootstrapNodeList', 'normalNodeList', 'cbftConfigFile', 'cbftConfig', 'accountConfigFile', 'accountConfig', 'genesisFile', 'genesisConfig', 'staticNodeFile', 'initChain', 'startAll', 'isHttpRpc')

    def get_all_nodes(self):
        allNodes = []
        allNodes.append(self.collusionNodeList)
        allNodes.append(self.bootstrapNodeList)
        allNodes.append(self.normalNodeList)
        return allNodes

    def deploy_all(self):
        self.parseNodeConfig()
        self.parseGenesisFile()
        self.parseCbftConfigFile()
        self.parseAccountConfigFile()

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
            tasks.append(threadPool.submit(node.start))
        wait(tasks, return_when=ALL_COMPLETED)

    def deploy_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(threadPool.submit(node.uploadBinFile, self.binFile))
            tasks.append(threadPool.submit(node.uploadGenesisFile, self.genesisFile))
            tasks.append(threadPool.submit(node.uploadCbftFile, self.cbftConfigFile))
            tasks.append(threadPool.submit(node.uploadStaticNodeFile, self.staticNodeFile))
        wait(tasks, return_when=ALL_COMPLETED)

    def stop_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(threadPool.submit(node.stop))
        wait(tasks, return_when=ALL_COMPLETED)

    def reset_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(threadPool.submit(node.stop))
        wait(tasks, return_when=ALL_COMPLETED)

        tasks2 = []
        for node in node_list:
            tasks2.append(threadPool.submit(node.start))
        wait(tasks2, return_when=ALL_COMPLETED)

    def upload_files(self, node_list):
        for node in node_list:
            node.uploadBinFile(self.binFile)
            node.uploadGenesisFile(self.genesisFile)
            node.uploadStaticNodeFile(self.staticNodeFile)
            node.uploadCbftFile(self.cbftConfigFile)
            node.start()

    def parseNodeConfig(self):
        nodeConfig = LoadFile(self.nodeConfigFile).get_data()
        for node in nodeConfig.get["collusion"]:
            colluNode = Node()
            colluNode.id = node.get["id"]
            colluNode.host = node.get["host"]
            colluNode.port = node.get["port"]
            colluNode.rpcport = node.get["rpcport"]
            colluNode.username = node.get["username"]
            colluNode.password = node.get["password"]
            colluNode.blsprikey = node.get["blsprikey"]
            colluNode.blspubkey = node.get["blspubkey"]
            colluNode.nodekey = node.get["nodekey"]
            colluNode.url = node.get["url"]
            self.collusionNodeList.append(colluNode)

        for node in nodeConfig.get["nocollusion"]:
            normalNode = Node()
            normalNode.id = node.get["id"]
            normalNode.host = node.get["host"]
            normalNode.port = node.get["port"]
            normalNode.rpcport = node.get["rpcport"]
            normalNode.username = node.get["username"]
            normalNode.password = node.get["password"]
            normalNode.blsprikey = node.get["blsprikey"]
            normalNode.blspubkey = node.get["blspubkey"]
            normalNode.nodekey = node.get["nodekey"]
            normalNode.url = node.get["url"]
            self.normalNodeList.append(normalNode)

    def parseGenesisFile(self):
        self.genesisConfig = LoadFile(self.genesisFile).get_data()
        self.genesisConfig['config']['cbft']["initialNodes"] = self.getInitNodesForGenesis()
        self.rewriteGenesisFile()

    def parseCbftConfigFile(self):
        self.cbftConfig = LoadFile(self.cbftConfigFile).get_data()

    def parseAccountConfigFile(self):
        self.accountConfig = LoadFile(self.accountConfigFile).get_data()

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
        self.backupLogs(self.bootstrapNodeList)
        self.backupLogs(self.normalNodeList)

    def backupLogs(self, node_list):
        self.checkLogPath()
        for node in node_list:
            node.backupLog()
        self.zipAllLog(self)

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
        tar = tarfile.open("{}/{}_{}_log.tar.gz".format(LOG_PATH, self.nodeConfigFile, t), "w:gz")
        tar.add(TMP_LOG)
        tar.close()
        print("压缩完成")
        print("开始删除缓存.....")
        shutil.rmtree(TMP_LOG)
        print("删除缓存完成")


def create_test_env(binFile, nodeConfigFile, cbftConfigFile, genesisFile, accountConfigFile, staticNodeFile, initChain=True, startAll=True, isHttpRPC=True):
    env = TestEnvironment()
    env.binFile = binFile
    env.nodeConfigFile = nodeConfigFile
    env.cbftConfigFile = cbftConfigFile
    env.genesisFile = genesisFile
    env.accountConfigFile = accountConfigFile
    env.staticNodeFile = staticNodeFile
    env.initChain = initChain
    env.startAll = startAll
    env.isHttpRpc = isHttpRPC

    if not nodeConfigFile:
        raise Exception("缺少node配置文件")

    if not genesisFile:
        raise Exception("缺少genesis block配置文件")

    if startAll:
        env.start_all()



