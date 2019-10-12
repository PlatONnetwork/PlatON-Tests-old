import configparser
import json
import os
import shutil
import tarfile
import time
from concurrent.futures import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor

from common.log import log
from common.connect import connect_web3, connect_linux, runCMDBySSH
from common.load_file import LoadFile
from global_var import getThreadPoolExecutor
from settings import CMD_FOR_HTTP, CMD_FOR_WS, DEPLOY_PATH, LOCAL_TMP_FILE_ROOT_DIR, SUPERVISOR_FILE, CONFIG_JSON_FILE, \
    STATIC_NODE_FILE, GENESIS_FILE, PLATON_BIN_FILE

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
    def __init__(self, id=None, host=None, port=None, username=None, password=None, blsprikey=None, blspubkey=None, nodekey=None, rpcport=None, deployDir=None, syncMode="full"):
        self.data_tmp_dir = None
        self.remoteBlskeyFile = None
        self.remoteConfigFile = None
        self.remoteNodekeyFile = None
        self.remoteDataDir = None
        self.supervisor_service_id = None
        self.supervisor_conf_file_name = None
        self.supervisor_tmp_dir = None
        self.id = id
        self.host = host
        self.port = port
        self.rpcport = rpcport
        self.username = username
        self.password = password
        self.blsprikey = blsprikey
        self.blspubkey = blspubkey
        self.nodekey = nodekey
        self.remoteDeployDir = deployDir
        self.syncMode = syncMode

    def getEnodeUrl(self):
        return r"enode://" + self.id + "@" + self.host + ":" + str(self.port)


    def generate_supervisor_node_conf_file(self, isHttRpc=True):
        """
        生成supervisor部署platon的配置
        :param node:
        :return:
        """
        if not os.path.exists(self.supervisor_tmp_dir):
            os.makedirs(self.supervisor_tmp_dir)

        supervisorConfFile = self.supervisor_tmp_dir + "/" + self.supervisor_conf_file_name

        with open(supervisorConfFile, "w") as fp:
            fp.write("[program:" + self.supervisor_service_id + "]\n")
            cmd = "{}/platon --identity platon --datadir {}".format(self.remoteDeployDir, self.remoteDataDir)
            cmd = cmd + " --port {}".format(self.port)

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

            cmd = cmd + " --gcmode archive --nodekey {}".format(self.remoteNodekeyFile)
            #cmd = cmd + " --config {}".format(self.remoteConfigFile)
            cmd = cmd + " --cbft.blskey {}".format(self.remoteBlskeyFile)

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
            fp.write("stdout_logfile={}/log/platon.log\n".format(self.remoteDeployDir))
            fp.write("stdout_logfile_maxbytes=200MB\n")
            fp.write("stdout_logfile_backups=20\n")
            fp.close()

    def generateKeyFiles(self):
        if not os.path.exists(self.data_tmp_dir):
            os.makedirs(self.data_tmp_dir)
        blskey_file = os.path.join(self.data_tmp_dir, "blskey")
        with open(blskey_file, 'w', encoding="utf-8") as f:
            f.write(self.blsprikey)
            f.close()

        nodekey_file = os.path.join(self.data_tmp_dir, "nodekey")
        with open(nodekey_file, 'w', encoding="utf-8") as f:
            f.write(self.nodekey)
            f.close()


    def initNode(self):
        self.remoteDeployDir = '{}/node-{}'.format(self.remoteDeployDir, self.port)
        self.remoteDataDir = '{}/data'.format(self.remoteDeployDir)
        self.remoteBinFile = '{}/platon'.format(self.remoteDeployDir)
        self.remoteGenesisFile = '{}/genesis.json'.format(self.remoteDeployDir)
        self.remoteConfigFile = '{}/config.json'.format(self.remoteDeployDir)
        self.remoteBlskeyFile = '{}/blskey'.format(self.remoteDataDir)
        self.remoteNodekeyFile = '{}/nodekey'.format(self.remoteDataDir)
        self.remoteStaticNodesFile = '{}/static-nodes.json'.format(self.remoteDeployDir)

        self.tmp_root_dir = os.path.join(LOCAL_TMP_FILE_ROOT_DIR, "{}_{}".format(self.host, self.port))    # 生成的各个节点的data/supervesor数据，存放子目录
        self.supervisor_tmp_dir = os.path.join(self.tmp_root_dir, "supervisor")
        self.data_tmp_dir = os.path.join(self.tmp_root_dir, "data")

        self.supervisor_service_id = "node-" + str(self.port)    # supervisor服务启停节点的 ID
        self.supervisor_conf_file_name = "node-" + str(self.port) + ".conf"  # 生成的各个节点的supervesor配置文件名称

        # connect_ssh
        self.ssh, self.sftp, self.transport = connect_linux(self.host, self.username, self.password, 22)

        pwd_list = runCMDBySSH(self.ssh, "pwd")
        pwd = pwd_list[0].strip("\r\n")

        if not os.path.isabs(self.remoteDeployDir):
            self.remoteDeployDir = pwd + "/" + self.remoteDeployDir
            self.remoteDataDir = pwd + "/" + self.remoteDataDir
            self.remoteBinFile = pwd + "/" + self.remoteBinFile
            self.remoteNodekeyFile = pwd + "/" + self.remoteNodekeyFile
            self.remoteBlskeyFile = pwd + "/" + self.remoteBlskeyFile


    def start(self, initChain):
        if initChain:
            log.info("to init PlatON chain....")
            self.initPlatON()

        log.info("::::copy supervisor_conf_file_name :{} to /etc/supervisor/conf.d".format(self.supervisor_conf_file_name))

        runCMDBySSH(self.ssh, "cd ./tmp/" + "; sudo -S -p '' cp " + self.supervisor_conf_file_name + " /etc/supervisor/conf.d", self.password)
        runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl update " + self.supervisor_service_id, self.password)
        runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl start " + self.supervisor_service_id, self.password)


    def clean(self):
        #time.sleep(0.5)
        runCMDBySSH(self.ssh, "sudo -S -p '' rm -rf {}".format(self.remoteDeployDir), self.password)
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.remoteDeployDir))
        runCMDBySSH(self.ssh, "mkdir -p {}".format(self.remoteDataDir))
        runCMDBySSH(self.ssh, 'mkdir -p {}/log'.format(self.remoteDeployDir))

    def clean_log(self):
        runCMDBySSH(self.ssh, "rm -rf {}/nohup.out".format(self.remoteDeployDir))
        runCMDBySSH(self.ssh, "rm -rf {}/log".format(self.remoteDeployDir))
        runCMDBySSH(self.ssh, 'mkdir -p {}/log'.format(self.remoteDeployDir))


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
        log.info("uploadAllFiles:::::::::: {}".format(self.host))
        self.uploadBinFile()
        self.uploadGenesisFile()
        self.uploadStaticNodeFile()
        self.uploadConfigFile()
        self.uploadKeyFiles()
        self.upload_supervisor_node_conf_file()

    def uploadBinFile(self):
        if PLATON_BIN_FILE and os.path.exists(PLATON_BIN_FILE):
            remoteFile = os.path.join(self.remoteDeployDir, "platon").replace("\\", "/")
            self.sftp.put(PLATON_BIN_FILE, remoteFile)
            runCMDBySSH(self.ssh, 'chmod +x {}'.format(remoteFile))
            log.info("platon bin file uploaded to node: {}".format(self.host))
        else:
            log.error("platon bin file not found: {}".format(PLATON_BIN_FILE))

    def uploadGenesisFile(self):
        if GENESIS_FILE and os.path.exists(GENESIS_FILE):
            remoteFile = os.path.join(self.remoteDeployDir, "genesis.json").replace("\\", "/")
            self.sftp.put(GENESIS_FILE, remoteFile)
            log.info("genesis.json uploaded to node: {}".format(self.host))
        else:
            log.warn("genesis.json not found: {}".format(GENESIS_FILE))


    def uploadStaticNodeFile(self):
        if STATIC_NODE_FILE and os.path.exists(STATIC_NODE_FILE):
            remoteFile = os.path.join(self.remoteDeployDir, "static-nodes.json").replace("\\", "/")
            self.sftp.put(STATIC_NODE_FILE, remoteFile)
            log.info("static-nodes.json uploaded to node: {}".format(self.host))
        else:
            log.warn("static-nodes.json not found: {}".format(STATIC_NODE_FILE))

    def uploadConfigFile(self):
        if CONFIG_JSON_FILE and os.path.exists(CONFIG_JSON_FILE):
            remoteFile = os.path.join(self.remoteDeployDir, "config.json").replace("\\", "/")
            self.sftp.put(CONFIG_JSON_FILE, remoteFile)
            log.info("config.json uploaded to node: {}".format(self.host))
        else:
            log.warn("config.json not found: {}".format(STATIC_NODE_FILE))



    def uploadKeyFiles(self):
        blskey_file = os.path.join(self.data_tmp_dir, "blskey")
        if os.path.exists(blskey_file):
            remoteFile = os.path.join(self.remoteDataDir, "blskey").replace("\\", "/")
            self.sftp.put(blskey_file, remoteFile)
            log.info("blskey uploaded to node: {}".format(self.host))

        nodekey_file = os.path.join(self.data_tmp_dir, "nodekey")
        if os.path.exists(nodekey_file):
            remoteFile = os.path.join(self.remoteDataDir, "nodekey").replace("\\", "/")
            self.sftp.put(nodekey_file, remoteFile)
            log.info("nodekey_file uploaded to node: {}".format(self.host))

    def upload_supervisor_node_conf_file(self):
        supervisorConfFile = self.supervisor_tmp_dir + "/" + self.supervisor_conf_file_name
        if os.path.exists(supervisorConfFile):
            runCMDBySSH(self.ssh, "rm -rf ./tmp/{}".format(self.supervisor_conf_file_name))
            self.sftp.put(supervisorConfFile, "./tmp/{}".format(self.supervisor_conf_file_name))
            log.info("supervisor startup config uploaded to node: {}".format(self.host))

    def backupLog(self):
        runCMDBySSH(self.ssh, "cd {};tar zcvf log.tar.gz ./log".format(self.remoteDeployDir))
        self.sftp.get("{}/log.tar.gz".format(self.remoteDeployDir), "{}/{}_{}.tar.gz".format(TMP_LOG, self.host, self.port))
        runCMDBySSH(self.ssh, "cd {};rm -rf ./log.tar.gz".format(self.remoteDeployDir))
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

        if not os.path.exists(self.supervisor_tmp_dir):
            os.makedirs(self.supervisor_tmp_dir)
        tmpConf = os.path.join(self.supervisor_tmp_dir, "supervisord.conf")
        with open(tmpConf, "w") as file:
            template.write(file)
            file.close()
        return tmpConf

    def judge_restart_supervisor(self, supervisor_pid_str):
        supervisor_pid = supervisor_pid_str[0].strip("\n")
        log.info("judge_restart_supervisor......2222222222..........{}".format(supervisor_pid))

        result = runCMDBySSH(self.ssh, "sudo -S -p '' supervisorctl stop {}".format(self.supervisor_service_id), self.password)
        log.info("judge_restart_supervisor......2222222222..........result={}, port={}".format(result, self.port))
        if "node-{}".format(self.port) not in result[0]:
            log.info("judge_restart_supervisor......2222222222..........")
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
        cmd = '{} --datadir {} --config {} init {}'.format(self.remoteBinFile, self.remoteDataDir, self.remoteConfigFile, self.remoteGenesisFile)
        runCMDBySSH(self.ssh, cmd)


    def deploy_supervisor(self):
        """
        部署supervisor
        :param node:
        :return:
        """
        log.info("call deploy_supervisor() for node: {}".format(self.host))
        tmpConf = self.genSupervisorConf()
        runCMDBySSH(self.ssh, "mkdir -p ./tmp")
        self.sftp.put(tmpConf, "./tmp/supervisord.conf")

        supervisor_pid_str = runCMDBySSH(self.ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")

        log.info("supervisor_pid_str: {}".format(supervisor_pid_str))

        if len(supervisor_pid_str) > 0:
            self.judge_restart_supervisor(supervisor_pid_str)
        else:
            log.info("judge_restart_supervisor......1111111111..........")
            runCMDBySSH(self.ssh, "sudo -S -p '' apt update", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' apt install -y supervisor", self.password)
            runCMDBySSH(self.ssh, "sudo -S -p '' cp ./tmp/supervisord.conf /etc/supervisor/", self.password)
            supervisor_pid_str = runCMDBySSH(self.ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
            if len(supervisor_pid_str) > 0:
                log.info("judge_restart_supervisor......3333333333..........")
                self.judge_restart_supervisor(supervisor_pid_str)
            else:
                runCMDBySSH(self.ssh, "sudo -S -p '' /etc/init.d/supervisor start", self.password)


class Account:
    def __init__(self, address, prikey, nonce=0, balance=0):
        self.id = id
        self.address = address
        self.prikey = prikey
        self.nonce = nonce
        self.balance = balance



# @singleton
class TestEnvironment:
    __slots__ = ('binFile', 'nodeFile',  'accountFile', 'collusionNodeList', 'normalNodeList', 'accountConfig', 'genesisConfig', 'initChain', 'startAll', 'isHttpRpc', 'installDependency', 'installSuperVisor')

    def get_all_nodes(self):
        return self.collusionNodeList+self.normalNodeList

    def deploy_all(self):
        self.parseNodeFile()
        self.parseAccountFile()
        self.rewrite_genesisFile()
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
        for node in node_list:
            log.info("node:::::::::: {}".format(node.host))
            futureList.append(getThreadPoolExecutor().submit(lambda :node.uploadAllFiles()))
            #futureList.append(getThreadPoolExecutor().submit(uploadAllFiles,node))

        if len(futureList) > 0:
            wait(futureList, return_when=ALL_COMPLETED)
        log.info("all files uploaded")


        if self.installSuperVisor:
            log.info("nodes deploy supervisor")
            futureList.clear()
            for node in node_list:
                futureList.append(getThreadPoolExecutor().submit(lambda :node.deploy_supervisor()))
                #futureList.append(getThreadPoolExecutor().submit(deploy_supervisor, node))
            if len(futureList) > 0:
                wait(futureList, return_when=ALL_COMPLETED)
            log.info("SuperVisor installed")

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
            colluNode.syncMode = node.get("syncmode")

            colluNode.remoteDeployDir = node.get("deplayDir")
            if not colluNode.remoteDeployDir:
                colluNode.remoteDeployDir = DEPLOY_PATH

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
            normalNode.syncMode = node.get("syncmode")

            normalNode.remoteDeployDir = node.get("deplayDir")
            if not normalNode.remoteDeployDir:
                normalNode.remoteDeployDir = DEPLOY_PATH

            self.normalNodeList.append(normalNode)

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




