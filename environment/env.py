"""
结合新老框架的特性，结合新老部署脚步的优秀特性结合
当前属于旧用例迁移到新框架的时间点，两个部署脚本会共存一段时间，最后以哪个脚本为准根据表现而定
"""
import configparser
import json
import os
import time
import random
import shutil
import socket
import tarfile
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import copy
from common.load_file import get_f
from client_sdk_python import Web3
from client_sdk_python.admin import Admin
from client_sdk_python.debug import Debug
from client_sdk_python.eth import Eth
from client_sdk_python.personal import Personal
from ruamel import yaml

from common.abspath import abspath
from common.connect import run_ssh, connect_linux, connect_web3
from common.key import generate_key
from common.load_file import LoadFile
from common.log import log
from conf import setting_merge as conf
from environment.account import Account


def check_file_exists(*args):
    """
    检查本地文件是否存在
    :param args:
    :return:
    """
    for arg in args:
        if not os.path.exists(os.path.abspath(arg)):
            raise Exception("文件{}不存在".format(arg))


class TestConfig:
    def __init__(self, install_supervisor=True, install_dependency=True, init_chain=True, is_need_static=True):
        # 本地必须文件
        self.platon_bin_file = conf.PLATON_BIN_FILE
        self.genesis_file = conf.GENESIS_FILE
        self.static_node_file = conf.STATIC_NODE_FILE
        self.supervisor_file = conf.SUPERVISOR_FILE
        self.node_file = conf.NODE_FILE
        self.address_file = conf.ADDRESS_FILE
        self.account_file = conf.ACCOUNT_FILE
        # 本地缓存目录
        self.root_tmp = conf.LOCAL_TMP_FILE_ROOT_DIR
        self.node_tmp = conf.LOCAL_TMP_FILE_FOR_NODE
        self.server_tmp = conf.LOCAL_TMP_FILE_FOR_SERVER
        self.env_tmp = conf.LOCAL_TMP_FILE_FOR_ENV
        self.genesis_tmp = conf.LOCAL_TMP_FILE_FOR_GNENESIS

        # 服务器依赖安装
        self.install_supervisor = install_supervisor
        self.install_dependency = install_dependency

        # 链部署定制
        self.init_chain = init_chain
        self.is_need_static = is_need_static
        self.log_level = 4
        self.syncmode = "full"
        self.append_cmd = ""

        # 最大线程数
        self.max_worker = 30

        # 环境id
        self.env_id = None

        # 服务器远程目录
        self.deploy_path = conf.DEPLOY_PATH
        self.remote_supervisor_tmp = "{}/tmp/supervisor/".format(self.deploy_path)
        self.remote_compression_tmp_path = "{}/tmp/env/".format(self.deploy_path)

        # 日志相关
        self.bug_log = abspath("./bug_log")
        self.tmp_log = abspath("./tmp_log")


class Server:
    def __init__(self, server_conf, cfg: TestConfig):
        self.cfg = cfg
        self.host = server_conf["host"]
        self.username = server_conf["username"]
        self.password = server_conf["password"]
        self.ssh_port = server_conf.get("sshport", 22)
        self.ssh, self.sftp, self.t = connect_linux(self.host, self.username, self.password, self.ssh_port)

        self.remote_supervisor_conf = "{}/supervisord.conf".format(self.cfg.remote_supervisor_tmp)

    def run_ssh(self, cmd, need_password=False):
        if need_password:
            return run_ssh(self.ssh, cmd, self.password)
        return run_ssh(self.ssh, cmd)

    def put_compression(self):
        try:
            ls = self.run_ssh("cd {};ls".format(self.cfg.remote_compression_tmp_path))
            gz_name = self.cfg.env_id + ".tar.gz"
            if (gz_name + "\n") in ls:
                return True, "need not upload"
            local_gz = os.path.join(self.cfg.env_tmp, gz_name)
            self.run_ssh("rm -rf {};mkdir -p {}".format(self.cfg.remote_compression_tmp_path,
                                                        self.cfg.remote_compression_tmp_path))
            self.sftp.put(local_gz, self.cfg.remote_compression_tmp_path + "/" + os.path.basename(local_gz))
            self.run_ssh("tar -zxvf {}/{}.tar.gz -C {}".format(self.cfg.remote_compression_tmp_path, self.cfg.env_id,
                                                               self.cfg.remote_compression_tmp_path))
        except Exception as e:
            return False, "{}-upload __compression failed:{}".format(self.host, e)
        return True, "upload __compression success"

    def install_dependency(self):
        try:
            self.run_ssh("rm -rf {} bn bn.tar.gz tmp")
            self.run_ssh("sudo -S -p '' ntpdate 0.centos.pool.ntp.org", True)
            self.run_ssh("sudo -S -p '' apt install llvm g++ libgmp-dev libssl-dev -y", True)
        except Exception as e:
            return False, "{}-install dependency failed:{}".format(self.host, e)
        return True, "install dependency success"

    def install_supervisor(self):
        try:
            test_name = "test-node"
            result = self.run_ssh("sudo -S -p '' supervisorctl stop {}".format(test_name), True)
            if test_name not in result[0]:
                tmp_dir = os.path.join(self.cfg.server_tmp, self.host)
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                tmp = os.path.join(tmp_dir, "supervisord.conf")
                self.__rewrite_supervisor_conf(tmp)
                self.run_ssh("mkdir -p {}".format(self.cfg.remote_supervisor_tmp))
                self.sftp.put(tmp, self.remote_supervisor_conf)
                supervisor_pid_str = self.run_ssh("ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
                if len(supervisor_pid_str) > 0:
                    self.__reload_supervisor(supervisor_pid_str)
                else:
                    self.run_ssh("sudo -S -p '' apt update", True)
                    self.run_ssh("sudo -S -p '' apt install -y supervisor", True)
                    self.run_ssh("sudo -S -p '' cp {} /etc/supervisor/".format(self.remote_supervisor_conf), True)
                    supervisor_pid_str = self.run_ssh("ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
                    if len(supervisor_pid_str) > 0:
                        self.__reload_supervisor(supervisor_pid_str)
                    else:
                        self.run_ssh("sudo -S -p '' /etc/init.d/supervisor start", True)
        except Exception as e:
            return False, "{}-install supervisor failed:{}".format(self.host, e)
        return True, "install supervisor success"

    def __reload_supervisor(self, supervisor_pid_str):
        supervisor_pid = supervisor_pid_str[0].strip("\n")
        self.run_ssh("sudo -S -p '' kill {}".format(supervisor_pid), True)
        self.run_ssh("sudo -S -p '' killall supervisord", True)
        self.run_ssh("sudo -S -p '' sudo apt remove supervisor -y", True)
        self.run_ssh("sudo -S -p '' apt update", True)
        self.run_ssh("sudo -S -p '' apt install -y supervisor", True)
        self.run_ssh("sudo -S -p '' cp {} /etc/supervisor/".format(self.remote_supervisor_conf), True)
        self.run_ssh("sudo -S -p '' /etc/init.d/supervisor start", True)

    def __rewrite_supervisor_conf(self, sup_tmp):
        con = configparser.ConfigParser()
        con.read(self.cfg.supervisor_file)
        con.set("inet_http_server", "username", self.username)
        con.set("inet_http_server", "password", self.password)
        con.set("supervisorctl", "username", self.username)
        con.set("supervisorctl", "password", self.password)
        with open(sup_tmp, "w") as file:
            con.write(file)


class Node:
    def __init__(self, node_conf, cfg: TestConfig):
        self.cfg = cfg
        # 节点身份参数
        self.blspubkey = node_conf["blspubkey"]
        self.blsprikey = node_conf["blsprikey"]
        self.node_id = node_conf["id"]
        self.nodekey = node_conf["nodekey"]
        # 节点启动必要参数
        self.p2p_port = str(node_conf["port"])
        self.rpc_port = str(node_conf["rpcport"])
        # 节点启动非必要参数
        self.wsport = node_conf.get("wsport")
        self.wsurl = node_conf.get("wsurl")
        self.pprofport = node_conf.get("pprofport")
        self.fail_point = node_conf.get("fail_point")
        # 节点服务器信息
        self.host = node_conf["host"]
        self.username = node_conf["username"]
        self.password = node_conf["password"]
        self.ssh_port = node_conf.get("sshport", 22)
        self.ssh, self.sftp, self.t = connect_linux(self.host, self.username, self.password, self.ssh_port)

        # 节点标识信息
        self.url = node_conf["url"]
        self.node_name = "node-" + self.p2p_port
        self.node_mark = self.host + ":" + self.p2p_port
        # 节点远程目录信息
        self.remote_node_path = "{}/{}".format(self.cfg.deploy_path, self.node_name)

        self.remote_log_dir = '{}/log'.format(self.remote_node_path)
        self.remote_bin_file = self.remote_node_path + "/platon"
        self.remote_genesis_file = self.remote_node_path + "/genesis.json"
        self.remote_data_dir = self.remote_node_path + "/data"

        self.remote_blskey_file = '{}/blskey'.format(self.remote_data_dir)
        self.remote_nodekey_file = '{}/nodekey'.format(self.remote_data_dir)
        self.remote_static_nodes_file = '{}/static-nodes.json'.format(self.remote_data_dir)
        self.remote_db_dir = '{}/platon'.format(self.remote_data_dir)

        self.remote_supervisor_node_file = '{}/{}.conf'.format(self.cfg.remote_supervisor_tmp, self.node_name)

        # RPC连接
        self.__is_connected = False
        self.__rpc = None

        # node local tmp
        self.local_node_tmp = self.gen_node_tmp()

    def gen_node_tmp(self):
        tmp = os.path.join(self.cfg.node_tmp, self.host + "_" + self.p2p_port)
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        return tmp

    @property
    def enode(self):
        return r"enode://" + self.node_id + "@" + self.host + ":" + self.p2p_port

    def init(self):
        try:
            cmd = '{} --datadir {} init {}'.format(self.remote_bin_file, self.remote_data_dir, self.remote_genesis_file)
            result = self.run_ssh(cmd)
        except Exception as e:
            raise Exception("{}-init failed:{}".format(self.node_mark, e))
        if len(result) > 0:
            log.error("{}-init failed:{}".format(self.node_mark, result[0]))
            raise Exception("{}-init failed:{}".format(self.node_mark, result[0]))

    def run_ssh(self, cmd, need_password=False):
        if need_password:
            return run_ssh(self.ssh, cmd, self.password)
        return run_ssh(self.ssh, cmd)

    def clean(self):
        try:
            self.stop()
            self.run_ssh("sudo -S -p '' rm -rf {};mkdir -p {}".format(self.remote_node_path, self.remote_node_path),
                         True)
        except Exception as e:
            return False, "{}-clean failed:{}".format(self.node_mark, e)
        return True, "{}-clean success".format(self.node_mark)

    def clean_db(self):
        try:
            self.stop()
            self.run_ssh("sudo -S -p '' rm -rf {}".format(self.remote_db_dir), True)
        except Exception as e:
            return False, "{}-clean db failed:{}".format(self.node_mark, e)
        return True, "{}-clean db success".format(self.node_mark)

    def clean_log(self):
        try:
            self.stop()
            self.run_ssh("rm -rf {}".format(self.remote_log_dir))
            self.append_log_file()
        except Exception as e:
            raise Exception("{}-clean log failed:{}".format(self.node_mark, e))

    def append_log_file(self):
        try:
            self.run_ssh("mkdir -p {};echo {} >> {}/platon.log".format(self.remote_log_dir, self.cfg.env_id, self.remote_log_dir))
        except Exception as e:
            raise Exception("{}-clean log failed:{}".format(self.node_mark, e))

    def stop(self):
        try:
            self.__is_connected = False
            if not self.running:
                return True, "{}-node is not running".format(self.node_mark)
            self.run_ssh("sudo -S -p '' supervisorctl stop {}".format(self.node_name), True)
        except Exception as e:
            return False, "{}-close node failed:{}".format(self.node_mark, e)
        return True, "{}-stop node success".format(self.node_mark)

    def start(self, is_init=False) -> tuple:
        try:
            self.stop()
            if is_init:
                self.init()
            self.append_log_file()
            result = self.run_ssh("sudo -S -p '' supervisorctl start " + self.node_name, True)
            for r in result:
                if "ERROR" in r:
                    raise Exception("{}-start failed:{}".format(self.node_mark, r.strip("\n")))
        except Exception as e:
            return False, "{}-start failed:{}".format(self.node_mark, e)
        return True, "{}-start success".format(self.node_mark)

    def restart(self) -> tuple:
        try:
            self.append_log_file()
            result = self.run_ssh("sudo -S -p '' supervisorctl restart " + self.node_name, True)
            for r in result:
                if "ERROR" in r:
                    raise Exception("{}-restart failed:{}".format(self.node_mark, r.strip("\n")))
        except Exception as e:
            return False, "{}-restart failed:{}".format(self.node_mark, e)
        return True, "{}-restart success".format(self.node_mark)

    def update(self) -> tuple:
        try:
            self.stop()
            self.put_bin()
            self.start()
        except Exception as e:
            return False, "{}-update failed:{}".format(self.node_mark, e)
        return True, "{}-update success".format(self.node_mark)

    def close(self):
        is_success = True
        msg = "close success"
        try:
            self.clean()
            self.run_ssh("sudo -S -p '' rm -rf /etc/supervisor/conf.d/{}.conf".format(self.node_name), True)
        except Exception as e:
            is_success = False
            msg = "{}-close failed:{}".format(self.node_mark, e)
        finally:
            self.t.close()
            return is_success, msg

    def put_bin(self):
        try:
            self.run_ssh("rm -rf {}".format(self.remote_bin_file))
            self.sftp.put(self.cfg.platon_bin_file, self.remote_node_path)
            self.run_ssh('chmod +x {}'.format(self.remote_bin_file))
        except Exception as e:
            raise Exception("{}-upload platon failed:{}".format(self.node_mark, e))

    def put_nodekey(self):
        try:
            nodekey_file = os.path.join(self.local_node_tmp, "nodekey")
            with open(nodekey_file, 'w', encoding="utf-8") as f:
                f.write(self.nodekey)
            self.run_ssh('mkdir -p {}'.format(self.remote_data_dir))
            self.sftp.put(nodekey_file, self.remote_nodekey_file)
        except Exception as e:
            raise "{}-upload nodekey failed:{}".format(self.node_mark, e)

    def put_blskey(self):
        try:
            blskey_file = os.path.join(self.local_node_tmp, "blskey")
            with open(blskey_file, 'w', encoding="utf-8") as f:
                f.write(self.blsprikey)
            self.run_ssh('mkdir -p {}'.format(self.remote_data_dir))
            self.sftp.put(blskey_file, self.remote_blskey_file)
        except Exception as e:
            raise Exception("{}-upload blskey failed:{}".format(self.node_mark, e))

    def create_keystore(self, password="88888888"):
        try:
            cmd = "{} account new --datadir {}".format(self.remote_bin_file, self.remote_data_dir)
            stdin, stdout, _ = self.ssh.exec_command("source /etc/profile;%s" % cmd)
            stdin.write(str(password) + "\n")
            stdin.write(str(password) + "\n")
        except Exception as e:
            raise Exception("{}-create keystore failed:{}".format(self.node_mark, e))

    def put_genesis(self, genesis_file):
        try:
            self.sftp.put(genesis_file, self.remote_genesis_file)
        except Exception as e:
            raise Exception("{}-upload genesis failed:{}".format(self.node_mark, e))

    def put_static(self):
        try:
            self.sftp.put(self.cfg.static_node_file, self.remote_static_nodes_file)
        except Exception as e:
            raise Exception("{}-upload static nodes json failed:{}".format(self.node_mark, e))

    def put_deploy_conf(self):
        try:
            log.debug("{}-generate supervisor deploy conf...".format(self.node_mark))
            supervisor_tmp_file = os.path.join(self.local_node_tmp, "{}.conf".format(self.node_name))
            self.__gen_deploy_conf(supervisor_tmp_file)
            log.debug("{}-upload supervisor deploy conf...".format(self.node_mark))
            self.run_ssh("rm -rf {}".format(self.remote_supervisor_node_file))
            self.run_ssh("mkdir -p {}".format(self.cfg.remote_supervisor_tmp))
            self.sftp.put(supervisor_tmp_file, self.remote_supervisor_node_file)
            self.run_ssh("sudo -S -p '' cp {} /etc/supervisor/conf.d".format(self.remote_supervisor_node_file), True)
        except Exception as e:
            raise Exception("{}-upload deploy conf failed:{}".format(self.node_mark, e))

    def __gen_deploy_conf(self, sup_tmp_file):
        pwd_list = self.run_ssh("pwd")
        pwd = pwd_list[0].strip("\r\n")
        with open(sup_tmp_file, "w") as fp:
            fp.write("[program:" + self.node_name + "]\n")
            go_fail_point = ""
            if self.fail_point:
                go_fail_point = " GO_FAILPOINTS='{}' ".format(self.fail_point)
            if not os.path.isabs(self.cfg.deploy_path):
                cmd = "{}/{} --identity platon --datadir".format(pwd, self.remote_bin_file)
                cmd = cmd + " {}/{} --port ".format(pwd, self.remote_data_dir) + self.p2p_port
                cmd = cmd + " --gcmode archive --nodekey " + "{}/{}".format(pwd, self.remote_nodekey_file)
                cmd = cmd + " --cbft.blskey " + "{}/{}".format(pwd, self.remote_blskey_file)
            else:
                cmd = "{} --identity platon --datadir".format(self.remote_bin_file)
                cmd = cmd + " {} --port ".format(self.remote_data_dir) + self.p2p_port
                cmd = cmd + " --gcmode archive --nodekey " + self.remote_nodekey_file
                cmd = cmd + " --cbft.blskey " + self.remote_blskey_file
            cmd = cmd + " --syncmode '{}'".format(self.cfg.syncmode)
            cmd = cmd + " --debug --verbosity {}".format(self.cfg.log_level)
            if self.pprofport:
                cmd = cmd + " --pprof --pprofaddr 0.0.0.0 --pprofport " + str(self.pprofport)
            if self.wsport:
                cmd = cmd + " --ws --wsorigins '*' --wsaddr 0.0.0.0 --wsport " + str(self.wsport)
                cmd = cmd + " --wsapi platon,debug,personal,admin,net,web3"
            cmd = cmd + " --rpc --rpcaddr 0.0.0.0 --rpcport " + str(self.rpc_port)
            cmd = cmd + " --rpcapi platon,debug,personal,admin,net,web3"
            cmd = cmd + " --txpool.nolocals --nodiscover"
            if self.cfg.append_cmd:
                cmd = cmd + " " + self.cfg.append_cmd
            fp.write("command=" + cmd + "\n")
            if go_fail_point:
                fp.write("environment={}\n".format(go_fail_point))
            supervisor_default_conf = "numprocs=1\n" + "autostart=false\n" + "startsecs=3\n" + "startretries=3\n" + \
                                      "autorestart=unexpected\n" + "exitcode=0\n" + "stopsignal=TERM\n" + \
                                      "stopwaitsecs=10\n" + "redirect_stderr=true\n" + \
                                      "stdout_logfile_maxbytes=200MB\n" + "stdout_logfile_backups=20\n"
            fp.write(supervisor_default_conf)
            if os.path.isabs(self.cfg.deploy_path):
                fp.write("stdout_logfile={}/platon.log\n".format(self.remote_log_dir))
            else:
                fp.write("stdout_logfile={}/{}/platon.log\n".format(pwd, self.remote_log_dir))

    def deploy_me(self, genesis_file) -> tuple:
        try:
            log.debug("{}-clean node path...".format(self.node_mark))
            is_success, msg = self.clean()
            if not is_success:
                return is_success, msg
            self.clean_log()
            ls = self.run_ssh("cd {};ls".format(self.cfg.remote_compression_tmp_path))
            tar = self.cfg.env_id + ".tar.gz\n"
            if tar in ls:
                log.debug("{}-copy bin...".format(self.remote_node_path))
                cmd = "cp -r {}/{}/* {}".format(self.cfg.remote_compression_tmp_path, self.cfg.env_id,
                                                self.remote_node_path)
                self.run_ssh(cmd)
                self.run_ssh("chmod +x {};mkdir {}".format(self.remote_bin_file, self.remote_log_dir))
            else:
                return False, "{}-The server is missing a compressed package".format(self.node_mark)
            if self.cfg.init_chain:
                log.debug("{}-upload genesis...".format(self.node_mark))
                self.put_genesis(genesis_file)
            log.debug("{}-upload blskey...".format(self.node_mark))
            self.put_blskey()
            log.debug("{}-upload nodekey...".format(self.node_mark))
            self.put_nodekey()
            self.put_deploy_conf()
            log.debug("{}-use supervisor start node...".format(self.node_mark))
            log.debug("{}".format(self.run_ssh("cd {};ls".format(self.remote_log_dir))))
            self.run_ssh("sudo -S -p '' supervisorctl update " + self.node_name, True)
            return self.start(self.cfg.init_chain)
        except Exception as e:
            return False, "{}-deploy failed:{}".format(self.node_mark, e)

    def backup_log(self):
        try:
            self.run_ssh("cd {};tar zcvf log.tar.gz ./log".format(self.remote_node_path))
            self.sftp.get("{}/log.tar.gz".format(self.remote_node_path),
                          "{}/{}_{}.tar.gz".format(self.cfg.tmp_log, self.host, self.p2p_port))
            self.run_ssh("cd {};rm -rf ./log.tar.gz".format(self.remote_node_path))
        except Exception as e:
            return False, "{}-backup log failed:{}".format(self.node_mark, e)
        return True, "{}-backup log success".format(self.node_mark)

    @property
    def running(self) -> bool:
        p_id = self.run_ssh("ps -ef|grep platon|grep port|grep %s|grep -v grep|awk {'print $2'}" % self.p2p_port)
        if len(p_id) == 0:
            return False
        return True

    @property
    def web3(self) -> Web3:
        if not self.__is_connected:
            self.__rpc = connect_web3(self.url)
            self.__is_connected = True
        return self.__rpc

    @property
    def eth(self) -> Eth:
        return Eth(self.web3)

    @property
    def admin(self) -> Admin:
        return Admin(self.web3)

    @property
    def debug(self) -> Debug:
        return Debug(self.web3)

    @property
    def personal(self) -> Personal:
        return Personal(self.web3)

    @property
    def block_number(self) -> int:
        return self.eth.blockNumber


class TestEnvironment:
    def __init__(self, cfg: TestConfig, environment_id=None):
        # env config
        self.cfg = cfg

        # these file must be exist
        check_file_exists(self.cfg.platon_bin_file, self.cfg.genesis_file, self.cfg.supervisor_file,
                          self.cfg.node_file, self.cfg.address_file)
        if not os.path.exists(self.cfg.root_tmp):
            os.mkdir(self.cfg.root_tmp)

        # env info
        if not environment_id:
            self.cfg.env_id = self.__reset_env()
        else:
            self.cfg.env_id = environment_id

        # node config
        self.__is_update_node_file = False
        self.node_config = LoadFile(self.cfg.node_file).get_data()
        self.collusion_node_config_list = self.node_config.get("collusion")
        self.nocollusion_node_config_list = self.node_config.get("nocollusion")
        self.__rewrite_node_file()
        self.node_config_list = self.collusion_node_config_list + self.nocollusion_node_config_list
        self.collusion_node_list = []
        self.normal_node_list = []

        # servers
        self.server_list = self.__parse_servers()

        # node
        self.__parse_node()

        # genesis
        self.genesis_config = LoadFile(self.cfg.genesis_file).get_data()
        # accounts
        self.account = Account(self.cfg.account_file, self.genesis_config["config"]["chainId"])

    def __reset_env(self) -> str:
        if os.path.exists(self.cfg.env_tmp):
            shutil.rmtree(self.cfg.env_tmp)
        os.makedirs(self.cfg.env_tmp)
        return socket.getfqdn(socket.gethostname()) + str(int(time.time()))

    def get_init_nodes(self) -> list:
        init_node_list = []
        for node in self.collusion_node_list:
            init_node_list.append({"node": node.enode, "blsPubKey": node.blspubkey})
        return init_node_list

    def get_static_nodes(self) -> list:
        static_node_list = []
        for node in self.get_all_nodes():
            static_node_list.append(node.enode)
        return static_node_list

    @property
    def version(self):
        return ""

    @property
    def running(self):
        for node in self.get_all_nodes():
            if not node.running:
                return False
        return True

    @property
    def max_byzantium(self):
        return get_f(self.collusion_node_config_list)

    @property
    def block_interval(self) -> int:
        period = self.genesis_config["config"]["cbft"].get("period")
        amount = self.genesis_config["config"]["cbft"].get("amount")
        return int(period/1000/amount)

    def get_all_nodes(self) -> list:
        return self.collusion_node_list + self.normal_node_list

    def get_rand_node(self) -> Node:
        return random.choice(self.collusion_node_list)

    def get_a_normal_node(self) -> Node:
        return self.normal_node_list[0]

    def __executor(self, func, data_list, *args) -> bool:
        with ThreadPoolExecutor(max_workers=self.cfg.max_worker) as exe:
            futures = [exe.submit(func, pair, *args) for pair in data_list]
            done, unfinished = wait(futures, timeout=30, return_when=ALL_COMPLETED)
        result = []
        for d in done:
            is_success, msg = d.result()
            if not is_success:
                result.append(msg)
        if len(result) > 0:
            raise Exception("__executor {} failed:{}".format(func.__name__, result))
        return True

    def deploy_all(self, static_file=None, genesis_file=None):
        log.info("deploy all node")
        if genesis_file:
            log.info("new genesis")
            self.deploy_nodes(self.get_all_nodes(), static_file, genesis_file)
        else:
            log.info("default genesis")
            self.deploy_nodes(self.get_all_nodes(), static_file, self.cfg.genesis_tmp)
        log.info("deploy success")

    def start_all(self):
        log.info("start all node")
        self.start_nodes(self.get_all_nodes())

    def stop_all(self):
        log.info("stop all node")
        self.stop_nodes(self.get_all_nodes())

    def reset_all(self):
        log.info("restart all node")
        self.reset_nodes(self.get_all_nodes())

    def clean_all(self):
        log.info("clean all node")
        self.clean_nodes(self.get_all_nodes())

    def clean_db_all(self):
        log.info("clean db all node")
        self.clean_db_nodes(self.get_all_nodes())

    def shutdown(self):
        log.info("shutdown all node")

        def close(node: Node):
            return node.close()

        return self.__executor(close, self.get_all_nodes())

    def start_nodes(self, node_list, init_chain=True):
        def start(node: Node, need_init_chain):
            return node.start(need_init_chain)

        return self.__executor(start, node_list, init_chain)

    def deploy_nodes(self, node_list, static_file=None, genesis_file=None):
        log.info("deploy node")
        self.stop_nodes(node_list)
        # self.parseAccountFile()
        self.__rewrite_genesis_file()
        self.__rewrite_static_nodes()
        if not self.cfg.is_need_static:
            self.__compression(None)
        elif static_file:
            self.__compression(static_file)
        else:
            self.__compression(self.cfg.static_node_file)
        if self.cfg.install_supervisor:
            self.install_all_supervisor()
            self.cfg.install_supervisor = False
        if self.cfg.install_dependency:
            self.install_all_dependency()
            self.cfg.install_dependency = False
        self.put_all_compression()

        def deploy(node: Node):
            return node.deploy_me(genesis_file)

        return self.__executor(deploy, node_list)

    def stop_nodes(self, node_list):
        def stop(node: Node):
            return node.stop()

        return self.__executor(stop, node_list)

    def reset_nodes(self, node_list):
        def restart(node: Node):
            return node.restart()

        return self.__executor(restart, node_list)

    def clean_nodes(self, node_list):
        def clean(node: Node):
            return node.clean()

        return self.__executor(clean, node_list)

    def clean_db_nodes(self, node_list):
        def clean_db(node: Node):
            return node.clean_db()

        return self.__executor(clean_db, node_list)

    def __parse_node(self):

        def init(node_config):
            return Node(node_config, self.cfg)

        log.info("parse node to node object")
        with ThreadPoolExecutor(max_workers=self.cfg.max_worker) as executor:
            futures = [executor.submit(init, pair) for pair in self.collusion_node_config_list]
            done, unfinished = wait(futures, timeout=30, return_when=ALL_COMPLETED)
        for do in done:
            self.collusion_node_list.append(do.result())

        with ThreadPoolExecutor(max_workers=self.cfg.max_worker) as executor:
            futures = [executor.submit(init, pair) for pair in self.nocollusion_node_config_list]
            done, unfinished = wait(futures, timeout=30, return_when=ALL_COMPLETED)
        for do in done:
            self.normal_node_list.append(do.result())

    def put_all_compression(self):
        log.info("upload compression")

        def uploads(server: Server):
            return server.put_compression()

        return self.__executor(uploads, self.server_list)

    def install_all_dependency(self):
        log.info("install rely")

        def install(server: Server):
            return server.install_dependency()

        return self.__executor(install, self.server_list)

    def install_all_supervisor(self):
        log.info("install supervisor")

        def install(server: Server):
            return server.install_supervisor()

        return self.__executor(install, self.server_list)

    def __parse_servers(self) -> list:
        server_config_list, server_list = [], []

        def check_in(_ip, nodes):
            for n in nodes:
                if _ip == n["host"]:
                    return True
            return False

        for node_config in self.node_config_list:
            ip = node_config["host"]
            if check_in(ip, server_config_list):
                continue
            server_config_list.append(node_config)

        def init(config):
            return Server(config, self.cfg)

        with ThreadPoolExecutor(max_workers=self.cfg.max_worker) as executor:
            futures = [executor.submit(init, pair) for pair in server_config_list]
            done, unfinished = wait(futures, timeout=30, return_when=ALL_COMPLETED)
        for do in done:
            server_list.append(do.result())
        return server_list

    def block_numbers(self, node_list=None) -> dict:
        if not node_list:
            node_list = self.get_all_nodes()
        result = {}
        for node in node_list:
            result[node.node_mark] = node.block_number
        return result

    def check_block(self, need_number=10, multiple=3, node_list=None):
        if not node_list:
            node_list = self.get_all_nodes()
        use_time = int(need_number * self.block_interval * multiple)
        while use_time:
            if max(self.block_numbers(node_list).values()) < need_number:
                time.sleep(1)
                use_time -= 1
                continue
            return
        raise Exception("环境无法正常出块")

    def backup_all_logs(self):
        self.backup_logs(self.get_all_nodes())

    def backup_logs(self, node_list):
        self.__check_log_path()

        def backup(node: Node):
            return node.backup_log()

        self.__executor(backup, node_list)
        self.__zip_all_log()

    def __check_log_path(self):
        if not os.path.exists(self.cfg.tmp_log):
            os.mkdir(self.cfg.tmp_log)
        else:
            shutil.rmtree(self.cfg.tmp_log)
            os.mkdir(self.cfg.tmp_log)
        if not os.path.exists(self.cfg.bug_log):
            os.mkdir(self.cfg.bug_log)

    def __zip_all_log(self):
        log.info("Start compressing.....")
        t = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        tar = tarfile.open("{}/{}_{}_log.tar.gz".format(self.cfg.bug_log, os.path.basename(self.cfg.node_file), t),
                           "w:gz")
        tar.add(self.cfg.tmp_log, arcname=os.path.basename(self.cfg.tmp_log))
        tar.close()
        log.info("Compression completed")
        log.info("Start deleting the cache.....")
        shutil.rmtree(self.cfg.tmp_log)
        log.info("Delete cache complete")

    def __rewrite_genesis_file(self):
        log.info("rewrite genesis.json")
        self.genesis_config['config']['cbft']["initialNodes"] = self.get_init_nodes()
        # with open(self.cfg.address_file, "r", encoding="UTF-8") as f:
        #     key_dict = json.load(f)
        # account = key_dict["address"]
        # self.genesis_config['alloc'][account] = {"balance": str(99999999999999999999999999)}
        accounts = self.account.get_all_accounts()
        for account in accounts:
            self.genesis_config['alloc'][account['address']] = {"balance": str(account['balance'])}
        with open(self.cfg.genesis_tmp, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.genesis_config, indent=4))

    def __rewrite_static_nodes(self):
        log.info("rewrite static-nodes.json")
        num = 0
        static_nodes = self.get_static_nodes()
        with open(self.cfg.static_node_file, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i in static_nodes:
                num += 1
                if num < len(static_nodes):
                    f.write('\"' + i + '\",\n')
                else:
                    f.write('\"' + i + '\"\n')
            f.write(']')

    def __fill_node_config(self, node_config):
        if not node_config.get("id") or not node_config.get("nodekey"):
            self.__is_update_node_file = True
            node_config["nodekey"], node_config["id"] = generate_key()
        if not node_config.get("port"):
            self.__is_update_node_file = True
            node_config["port"] = 16789
        if not node_config.get("rpcport"):
            self.__is_update_node_file = True
            node_config["rpcport"] = 6789
        if not node_config.get("url"):
            self.__is_update_node_file = True
            node_config["url"] = "http://{}:{}".format(node_config["host"], node_config["rpcport"])
        if node_config.get("wsport"):
            self.__is_update_node_file = True
            node_config["wsurl"] = "ws://{}:{}".format(node_config["host"], node_config["wsport"])
        return node_config

    def __rewrite_node_file(self):
        log.info("rewrite node file")
        result, result_collusion_list, result_nocollusion_list = {}, [], []
        if len(self.collusion_node_config_list) >= 1:
            for node_config in self.collusion_node_config_list:
                result_collusion_list.append(self.__fill_node_config(node_config))
            result["collusion"] = result_collusion_list
        if len(self.nocollusion_node_config_list) >= 1:
            for node_config in self.nocollusion_node_config_list:
                result_nocollusion_list.append(self.__fill_node_config(node_config))
            result["nocollusion"] = result_nocollusion_list
        if self.__is_update_node_file:
            self.collusion_node_config_list = result_collusion_list
            self.nocollusion_node_config_list = result_nocollusion_list
            with open(self.cfg.node_file, encoding="utf-8", mode="w") as f:
                yaml.dump(result, f, Dumper=yaml.RoundTripDumper)

    def __compression(self, static):
        log.info("__compression data")
        env_gz = os.path.join(self.cfg.env_tmp, self.cfg.env_id)
        if os.path.exists(env_gz):
            return
        os.makedirs(env_gz)
        data_dir = os.path.join(env_gz, "data")
        os.makedirs(data_dir)
        keystore_dir = os.path.join(data_dir, "keystore")
        os.makedirs(keystore_dir)
        keystore = os.path.join(keystore_dir, os.path.basename(self.cfg.address_file))
        shutil.copyfile(self.cfg.address_file, keystore)
        shutil.copyfile(self.cfg.platon_bin_file, os.path.join(env_gz, "platon"))
        if static:
            shutil.copyfile(static, os.path.join(data_dir, "static-nodes.json"))
        t = tarfile.open(env_gz + ".tar.gz", "w:gz")
        t.add(env_gz, arcname=os.path.basename(env_gz))
        t.close()


def create_env(node_file=None, account_file=None, init_chain=True,
               install_dependency=False, install_supervisor=False) -> TestEnvironment:
    cfg = TestConfig(install_supervisor=install_supervisor, install_dependency=install_dependency, init_chain=init_chain)
    if node_file:
        cfg.node_file = node_file
    if account_file:
        cfg.account_file = account_file
    return TestEnvironment(cfg)


if __name__ == "__main__":
    cfg = TestConfig()
    cfg.node_file = abspath("deploy/node/25_cbft.yml")
    env = TestEnvironment(cfg)
    # new_cfg = copy.copy(env.cfg)
    # new_cfg.syncmode = "fast"
    # print(env.cfg.syncmode)
    log.info("测试部署")
    env.deploy_all()
    env.deploy_all()
    # d = env.block_numbers()
    # print(d)
    # node = env.get_rand_node()
    # node.create_keystore()
    # print(node.node_mark)
    # time.sleep(80)
    # log.info("测试关闭")
    # env.stop_all()
    # time.sleep(30)
    # log.info("测试不初始化启动")
    # env.cfg.init_chain = False
    # env.start_all()
    # time.sleep(60)
    # d = env.block_numbers()
    # print(d)
    # log.info("测试重启")
    # env.reset_all()
    # time.sleep(60)
    # d = env.block_numbers()
    # print(d)
    # log.info("测试删除数据库")
    # env.clean_db_all()
    # log.info("删除数据库成功")
    # time.sleep(60)
    # env.cfg.init_chain = True
    # env.start_all()
    # time.sleep(30)
    # d = env.block_numbers()
    # print(d)
    # log.info("测试删除所有数据")
    # env.clean_all()
    # log.info("删除数据成功")
    # log.info("重新部署")
    # env.deploy_all()
    # d = env.block_numbers()
    # print(d)
    # time.sleep(60)
    # d = env.block_numbers()
    # print(d)
    env.shutdown()
