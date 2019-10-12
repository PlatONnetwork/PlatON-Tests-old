import configparser
import json
import os
import shutil
import tarfile
import time
from concurrent.futures import ALL_COMPLETED, wait

from client_sdk_python.eth import Eth

from concurrent.futures.thread import ThreadPoolExecutor

from common.log import log
from common.connect import connect_web3, connect_linux, runCMDBySSH
from common.load_file import LoadFile
from global_var import getThreadPoolExecutor
from settings import CMD_FOR_HTTP, CMD_FOR_WS, DEPLOY_PATH, SUPERVISOR_TMP, SUPERVISOR_FILE, CONFIG_JSON_FILE, \
    STATIC_NODE_FILE, GENESIS_FILE, PLATON_DATA_TMP, PLATON_BIN_FILE

from hexbytes import HexBytes


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
        self.tmp_sub_dir = "node_" + str(port)    # 生成的各个节点的data/supervesor数据，存放子目录
        self.supervisor_service_id = "node-" + str(port)    # supervisor服务启停节点的 ID
        self.supervisor_conf_file_name = "node-" + str(port) + ".conf"  # 生成的各个节点的supervesor配置文件名称

    def initNode(self):
        self.deployDir = '{}/node-{}'.format(self.deployDir, self.port)
        self.dataDir = '{}/data'.format(self.deployDir)
        self.binFile = '{}/platon'.format(self.deployDir)
        self.genesisFile = '{}/genesis.json'.format(self.deployDir)
        self.configFile = '{}/config.json'.format(self.deployDir)
        self.staticNodesFile = '{}/static-nodes.json'.format(self.deployDir)

        # connect_ssh
        self.ssh, self.sftp, self.transport = connect_linux(self.host, self.username, self.password, 22)

    def deploy_supervisor(self):
        """
        部署supervisor
        :param node:
        :return:
        """
        tmpConf = self.genSupervisorConf()
        runCMDBySSH(self.ssh, "mkdir -p ./tmp")
        self.sftp.put(tmpConf, "./tmp/template.conf")
        supervisor_pid_str = runCMDBySSH(self.ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")

        if len(supervisor_pid_str) > 0:
            self.judge_restart_supervisor(supervisor_pid_str)
        else:
            runCMDBySSH(self.ssh, "sudo -S -p '' apt update", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' apt install -y supervisor", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' cp ./tmp/supervisord.conf /etc/supervisor/", self.password)
            supervisor_pid_str = runCMDBySSH(self.ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
            if len(supervisor_pid_str) > 0:
                self.judge_restart_supervisor(supervisor_pid_str)
            else:
                runCMDBySSH(self.ssh, "sudo -S -p '' /etc/init.d/supervisor start", self.password)

    def generate_supervisor_node_conf_file(self, isHttRpc=True):

        """
        生成supervisor部署platon的配置
        :param node:
        :return:
        """
        pwd_list = runCMDBySSH(self.ssh, "pwd")
        pwd = pwd_list[0].strip("\r\n")

        tmpDir = os.path.join(SUPERVISOR_TMP, self.tmp_sub_dir)
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)

        supervisorConfFile = tmpDir + "/" + self.supervisor_conf_file_name

        with open(supervisorConfFile, "w") as fp:
            fp.write("[program:" + self.supervisor_service_id + "]\n")
            if os.path.isabs(self.deployDir):
                cmd = "{}/platon --identity platon --datadir  {}".format(self.deployDir, self.dataDir)
                cmd = cmd + " --port {}".format(self.port)
            else:
                cmd = "{}/{}/platon --identity platon --datadir {}/{}".format(pwd, self.deployDir, pwd, self.dataDir)
                cmd = cmd + " --port {} ".format(self.port)


            cmd = cmd + " --syncmode '{}'".format(self.syncMode)
            # if self.netType:
            #     cmd = cmd + " --" + self.netType

            # if node.get("mpcactor", None):
            #     cmd = cmd + " --mpc --mpc.actor {}".format(node.get("mpcactor"))
            # if node.get("vcactor", None):
            #     cmd = cmd + \
            #           " --vc --vc.actor {} --vc.password 88888888".format(
            #               node.get("vcactor"))

            cmd = cmd + " --debug --verbosity 5"
            if isHttRpc:
                cmd = cmd + " --rpc --rpcaddr 0.0.0.0 --rpcport " + str(self.rpcport)
                cmd = cmd + " --rpcapi platon,debug,personal,admin,net,web3"
            else:
                cmd = cmd + " --ws --wsorigins '*' --wsaddr 0.0.0.0 --wsport " + str(self.rpcport)
                cmd = cmd + " --wsapi eth,debug,personal,admin,net,web3"

            cmd = cmd + " --txpool.nolocals"

            # 监控指标
            # if self.is_metrics:
            #     cmd = cmd + " --metrics"
            #     cmd = cmd + " --metrics.influxdb --metrics.influxdb.endpoint http://10.10.8.16:8086"
            #     cmd = cmd + " --metrics.influxdb.database platon"
            #     cmd = cmd + " --metrics.influxdb.host.tag {}:{}".format(self.host, str(self.port))

            if os.path.isabs(self.deployDir):
                cmd = cmd + " --gcmode archive --nodekey {}/nodekey".format(self.dataDir)
                cmd = cmd + " --config {}/config.json".format(self.deployDir)
                cmd = cmd + " --cbft.blskey {}/blskey".format(self.dataDir)

            else:
                cmd = cmd + " --gcmode archive --nodekey {}/{}/nodekey".format(pwd, self.dataDir)
                cmd = cmd + " --config {}/config.json".format(self.deployDir)
                cmd = cmd + " --cbft.blskey {}/{}/blskey".format(pwd, self.dataDir)

            fp.write("command=" + cmd + "\n")


            # go_fail_point = ""
            # if node.get("fail_point", None):
            #     go_fail_point = " GO_FAILPOINTS='{}' ".format(
            #         node.get("fail_point", None))
            # if go_fail_point:
            #     fp.write("environment=LD_LIBRARY_PATH={}/mpclib,{}\n".format(pwd, go_fail_point))
            # else:
            #     fp.write("environment=LD_LIBRARY_PATH={}/mpclib\n".format(pwd))

            fp.write("numprocs=1\n")
            fp.write("autostart=false\n")
            fp.write("startsecs=3\n")
            fp.write("startretries=3\n")
            fp.write("autorestart=unexpected\n")
            fp.write("exitcode=0\n")
            fp.write("stopsignal=TERM\n")
            fp.write("stopwaitsecs=10\n")
            fp.write("redirect_stderr=true\n")
            if os.path.isabs(self.deployDir):
                fp.write("stdout_logfile={}/log/platon.log\n".format(self.deployDir))
            else:
                fp.write("stdout_logfile={}/{}/log/platon.log\n".format(pwd, self.deployDir))
            fp.write("stdout_logfile_maxbytes=200MB\n")
            fp.write("stdout_logfile_backups=20\n")
            fp.close()


    def getEnodeUrl(self):
        return r"enode://" + self.id + "@" + self.host + ":" + str(self.port)

    def start(self, initChain, isHttRpc):
        if initChain:
            self.initPlatON()

        runCMDBySSH(self.ssh, "cd ./tmp/" + "; sudo -S -p '' cp " + self.supervisor_conf_file_name + " /etc/supervisor/conf.d", self.password)
        runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl update " + self.supervisor_service_id, self.password)
        runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl start " + self.supervisor_service_id, self.password)


    def clean(self):
        #time.sleep(0.5)
        runCMDBySSH(self.ssh, "sudo -S -p '' rm -rf {}".format(self.deployDir), self.password)
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.deployDir))
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.dataDir))

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

    def uploadAllFiles(self):
        self.uploadBinFile()
        self.uploadGenesisFile()
        self.uploadStaticNodeFile()
        self.uploadConfigFile()
        self.uploadKeyFiles()
        self.upload_supervisor_node_conf_file()

    def uploadBinFile(self):
        if PLATON_BIN_FILE and os.path.exists(PLATON_BIN_FILE):
            remoteFile = os.path.join(self.deployDir, "platon").replace("\\", "/")
            self.sftp.put(PLATON_BIN_FILE, remoteFile)
            runCMDBySSH(self.ssh, 'chmod +x {}'.format(remoteFile))
            log.info("platon bin file uploaded to node: {}".format(self.host))
        else:
            log.error("platon bin file not found: {}".format(PLATON_BIN_FILE))

    def uploadGenesisFile(self):
        if GENESIS_FILE and os.path.exists(GENESIS_FILE):
            remoteFile = os.path.join(self.deployDir, "genesis.json").replace("\\", "/")
            self.sftp.put(GENESIS_FILE, remoteFile)
            log.info("genesis.json uploaded to node: {}".format(self.host))
        else:
            log.warn("genesis.json not found: {}".format(GENESIS_FILE))


    def uploadStaticNodeFile(self):
        if STATIC_NODE_FILE and os.path.exists(STATIC_NODE_FILE):
            remoteFile = os.path.join(self.deployDir, "static-nodes.json").replace("\\", "/")
            self.sftp.put(STATIC_NODE_FILE, remoteFile)
            log.info("static-nodes.json uploaded to node: {}".format(self.host))
        else:
            log.warn("static-nodes.json not found: {}".format(STATIC_NODE_FILE))

    def uploadConfigFile(self):
        if CONFIG_JSON_FILE and os.path.exists(CONFIG_JSON_FILE):
            remoteFile = os.path.join(self.deployDir, "config.json").replace("\\", "/")
            self.sftp.put(CONFIG_JSON_FILE, remoteFile)
            log.info("config.json uploaded to node: {}".format(self.host))
        else:
            log.warn("config.json not found: {}".format(STATIC_NODE_FILE))

    def generateKeyFiles(self):
        data_dir = os.path.join(PLATON_DATA_TMP, self.tmp_sub_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        blskey_file = os.path.join(data_dir, "blskey")
        with open(blskey_file, 'w', encoding="utf-8") as f:
            f.write(self.blsprikey)
            f.close()

        nodekey_file = os.path.join(data_dir, "nodekey")
        with open(nodekey_file, 'w', encoding="utf-8") as f:
            f.write(self.nodekey)
            f.close()

    def uploadKeyFiles(self):
        src_file_dir_tmp = os.path.join(PLATON_DATA_TMP, self.tmp_sub_dir)
        blskey_file = os.path.join(src_file_dir_tmp, "blskey")
        if os.path.exists(blskey_file):
            remoteFile = os.path.join(self.dataDir, "blskey").replace("\\", "/")
            self.sftp.put(blskey_file, remoteFile)
            log.info("blskey uploaded to node: {}".format(self.host))

        nodekey_file = os.path.join(src_file_dir_tmp, "nodekey")
        if os.path.exists(nodekey_file):
            remoteFile = os.path.join(self.dataDir, "nodekey").replace("\\", "/")
            self.sftp.put(nodekey_file, remoteFile)
            log.info("nodekey_file uploaded to node: {}".format(self.host))

    def upload_supervisor_node_conf_file(self):
        tmpDir = os.path.join(SUPERVISOR_TMP, self.tmp_sub_dir)
        supervisorConfFile = tmpDir + "/" + self.supervisor_conf_file_name
        if os.path.exists(supervisorConfFile):
            runCMDBySSH(self.ssh, "rm -rf ./tmp/{}".format(self.supervisor_conf_file_name))
            self.sftp.put(supervisorConfFile, "./tmp/{}".format(self.supervisor_conf_file_name))
            log.info("supervisor startup config uploaded to node: {}".format(self.host))

    def backupLog(self):
        runCMDBySSH(self.ssh, "cd {};tar zcvf log.tar.gz ./log".format(self.deployDir))
        self.sftp.get("{}/log.tar.gz".format(self.deployDir), "{}/{}_{}.tar.gz".format(TMP_LOG, self.host, self.port))
        runCMDBySSH(self.ssh, "cd {};rm -rf ./log.tar.gz".format(self.deployDir))
        # self.transport.close()


    def genSupervisorConf(self):
        """
        更新supervisor配置
        :param node:
        :param sup_template:
        :param sup_tmp:
        :return:
        """
        template = configparser.ConfigParser()
        template.read(SUPERVISOR_FILE)
        template.set("inet_http_server", "username", self.username)
        template.set("inet_http_server", "password", self.password)
        template.set("supervisorctl", "username", self.username)
        template.set("supervisorctl", "password", self.password)

        tmpDir = os.path.join(SUPERVISOR_TMP, self.tmp_sub_dir)
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
        tmpConf = os.path.join(tmpDir, "supervisord.conf")
        with open(tmpConf, "w") as file:
            template.write(file)
            file.close()
        return tmpConf

    def judge_restart_supervisor(self, supervisor_pid_str):
        supervisor_pid = supervisor_pid_str[0].strip("\n")
        result = runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl stop {}".format(self.supervisor_service_id), self.password)
        if "node-{}".format(self.port) not in result[0]:
            runCMDBySSH(self.ssh, "sudo -S -p '' kill {}".format(supervisor_pid), self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' killall supervisord", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' sudo apt remove supervisor -y", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' apt update", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' apt install -y supervisor", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' cp ./tmp/supervisord.conf /etc/supervisor/", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' /etc/init.d/supervisor start", self.password)

    def install_dependency(self):
        """
        配置服务器依赖
        :param nodedict:
        :param file:
        :return:
        """
        runCMDBySSH(self.ssh, "sudo -S -p '' ntpdate 0.centos.pool.ntp.org", self.password)
        #pwd_list = runCMDBySSH(self.ssh, "pwd")
        #pwd = pwd_list[0].strip("\r\n")
        #cmd = r"sudo -S -p '' sed -i '$a /usr/local/lib' /etc/ld.so.conf".format(pwd)
        runCMDBySSH(self.ssh, "sudo -S -p '' apt install llvm g++ libgmp-dev libssl-dev -y", self.password)
        #runCMDBySSH(self.ssh, cmd, self.password)
        #runCMDBySSH(self.ssh, "sudo -S -p '' ldconfig", self.password)


    def initPlatON(self):
        cmd = '{} --datadir {} --config {} init {}'.format(self.binFile, self.dataDir, self.configFile, self.genesisFile)
        runCMDBySSH(self.ssh, cmd)


class Account:
    def __init__(self, accountFile,chainId):
        '''
           accounts 包含的属性: address,prikey,nonce,balance
        '''
        self.accounts = {}
        accounts = LoadFile(accountFile).get_data()
        self.chain_id = chainId
        for account in  accounts:
            self.accounts[account['address']] = account

    def get_all_accounts(self):
        accounts = []
        for account in self.accounts:
            accounts.append(account)
        return accounts

    def get_rand_account(self):
        #todo 实现随机
        for account in self.accounts:
            return account

    def sendTransaction(self, connect, data, from_address, to_address, gasPrice, gas, value):
        account = self.accounts[from_address]
        transaction_dict = {
            "to": to_address,
            "gasPrice": gasPrice,
            "gas": gas,
            "nonce": account['nonce'],
            "data": data,
            "chainId": self.chain_id,
            "value": value
        }
        platon = Eth(connect)
        signedTransactionDict =  platon.account.signTransaction(
            transaction_dict, account['prikey']
        )

        data = signedTransactionDict.rawTransaction
        result = HexBytes(platon.sendRawTransaction(data)).hex()
        res = platon.waitForTransactionReceipt(result)
        return res







# @singleton
class TestEnvironment:
    __slots__ = ('binFile', 'nodeFile', 'account', 'accountFile', 'collusionNodeList', 'normalNodeList', 'accountConfig', 'genesisConfig', 'initChain', 'startAll', 'isHttpRpc', 'installDependency', 'installSuperVisor')

    def __init__(self):
        self.account = Account(self.accountFile)

    def get_all_nodes(self):
        return self.collusionNodeList+self.normalNodeList

    def deploy_all(self):
        self.parseNodeFile()

        self.rewrite_genesisFile()
        self.rewrite_configJsonFile()
        self.rewrite_staticNodesFile()
        self.generateKeyFiles(self.get_all_nodes())
        self.deploy_nodes(self.get_all_nodes())
        self.generate_all_supervisor_node_conf_files(self.get_all_nodes())



    def start_all(self):
        self.start_nodes(self.get_all_nodes())

    def stop_all(self):
        self.stop_nodes(self.get_all_nodes())

    def reset_all(self):
        self.reset_nodes(self.get_all_nodes())

    def start_nodes(self, node_list):
        futureList = []
        for node in node_list:
            futureList.append(getThreadPoolExecutor().submit(lambda :node.start(self.initChain, self.isHttpRpc)))
        wait(futureList, return_when=ALL_COMPLETED)

    def deploy_nodes(self, node_list):
        futureList = []

        log.info("nodes init")
        for node in node_list:
            futureList.append(getThreadPoolExecutor().submit(lambda: node.initNode()))
        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)

        if self.installDependency:
            log.info("nodes install dependencies: {}".format(self.installDependency))
            futureList.clear()
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda: node.install_dependency()))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes clean env")
        futureList.clear()
        if self.initChain:
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda:node.clean()))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)

        log.info("nodes upload files")
        futureList.clear()
        for node in node_list:
            futureList.append(getThreadPoolExecutor().submit(lambda :node.uploadAllFiles()))

        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)

        log.info("all files uploaded")
        if self.installSuperVisor:
            log.info("nodes deploy supervisor")
            futureList.clear()
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda: node.deploy_supervisor()))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)
        log.info("SuperVisor installed")





    def stop_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(lambda :node.stop()))
        wait(tasks, return_when=ALL_COMPLETED)

    def reset_nodes(self, node_list):
        tasks = []
        for node in node_list:
            tasks.append(getThreadPoolExecutor().submit(lambda :node.stop()))
        wait(tasks, return_when=ALL_COMPLETED)

        tasks2 = []
        for node in node_list:
            tasks2.append(getThreadPoolExecutor().submit(lambda :node.start()))
        wait(tasks2, return_when=ALL_COMPLETED)

    def parseNodeFile(self):
        nodeConfig = LoadFile(self.nodeFile).get_data()
        self.collusionNodeList = []
        self.normalNodeList = []

        for node in nodeConfig.get("collusion", []):
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
        if not os.path.exists(GENESIS_FILE):
            raise Exception("模板文件没有找到：{}".format(GENESIS_FILE))

        self.genesisConfig = LoadFile(GENESIS_FILE).get_data()
        self.genesisConfig['config']['cbft']["initialNodes"] = self.getInitNodesForGenesis()

        accounts = self.account.get_all_accounts()
        for account in accounts:
            self.genesisConfig['alloc'][account['address']] = account['balance']

        log.info("重写genesis.json内容")
        with open(GENESIS_FILE, 'w', encoding='utf-8') as f:
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
        configJsonFile = CONFIG_JSON_FILE
        if not os.path.exists(configJsonFile):
            log.info("模板文件没有找到：{}".format(configJsonFile))
            return

        config_data = LoadFile(configJsonFile).get_data()
        config_data['node']['P2P']["BootstrapNodes"] = self.getStaticNodeList()

        with open(configJsonFile, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_data))
            f.close()

    def  rewrite_staticNodesFile(self):
        """
        生成节点互连文件
        :param static_nodes: 共识节点enode
        :return:
        """
        log.info("生成static-nodes.json")
        if not os.path.exists(os.path.dirname(STATIC_NODE_FILE)):
            os.makedirs(os.path.dirname(STATIC_NODE_FILE))

        num = 0
        static_nodes = self.getStaticNodeList()
        with open(STATIC_NODE_FILE, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i in static_nodes:
                num += 1
                if num < len(static_nodes):
                    f.write('\"' + i + '\",\n')
                else:
                    f.write('\"' + i + '\"\n')
            f.write(']')
            f.close()

    def generateKeyFiles(self, node_list):
        for node in node_list:
            node.generateKeyFiles()

    def generate_all_supervisor_node_conf_files(self, node_list):
        for node in node_list:
            node.generate_supervisor_node_conf_file(self.isHttpRpc)


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
    #env.genesisFile = genesisFile
    env.accountFile = accountFile
    #env.staticNodeFile = staticNodeFile
    env.initChain = initChain
    env.startAll = startAll
    env.isHttpRpc = isHttpRPC

    if not nodeFile:
        raise Exception("缺少node配置文件")

    if not genesisFile:
        raise Exception("缺少genesis block配置文件")

    if startAll:
        env.start_all()



