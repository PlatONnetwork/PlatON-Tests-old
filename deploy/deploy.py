"""
platon 部署脚本，包括nohup管理进程和supervisor管理进程

BaseDeploy：
    包括基本的方法和nohup启动节点
AutoDeployPlaton：
    使用supervisor启动或关闭节点
"""
import configparser
import json
import os
import threading
import time
from urllib import parse

from ruamel import yaml

from common import log
from common.abspath import abspath
from common.connect import connect_linux, run_ssh, connect_web3
from common.key import generate_key
from common.load_file import LoadFile, get_node_list
from conf import setting as conf

lock = threading.Lock()


def run_thread(data: list, func, *args):
    """
    多线程运行封装
    :param data: 数据列表
    :param func: 方法
    :param args: 参数
    :return:
    """
    threads = []
    i = 0
    for d in data:
        param = [p for p in args]
        param.insert(0, d)
        param = tuple(param)
        t = threading.Thread(target=func, args=param)
        t.start()
        threads.append(t)
        i += 1
    for t2 in threads:
        t2.join()


def file_exists(*args):
    """
    检查本地文件是否存在
    :param args:
    :return:
    """
    for i in args:
        if not os.path.exists(os.path.abspath(i)):
            raise Exception("文件{}不存在".format(i))


def gen_node_tmp(basepath, host, port):
    return os.path.join(basepath, host + "_" + str(port))


def generate_init_node(collusion_list):
    """
    根据共识节点列表
    :param collusion_list:
    :return:
    """
    static_nodes = []
    nodeid_list = []
    for nodedict in collusion_list:
        public_value = r"enode://" + \
                       nodedict["id"] + "@" + \
                       nodedict["host"] + ":" + \
                       str(nodedict.get("port", 16789))
        static_nodes.append(public_value)
        nodeid_list.append(public_value)
    return static_nodes, nodeid_list


class BaseDeploy:
    def __init__(self,
                 platon=conf.PLATON_BIN,
                 cbft=conf.CBFT,
                 keystore=conf.KEYSTORE,
                 genesis=conf.GENESIS_TEMPLATE,
                 deploy_path=conf.DEPLOY_PATH,
                 net_type=None,
                 syncmode="full"):
        """
        部署节点
        :param platon:本地platon二进制文件路径
        :param cbft: 本地cbft.json文件路径
        :param keystore: 本地钱包文件路径
        :param genesis: 本地genesis.json模板路径
        :param deploy_path: 远程服务器部署目录可以使用登录用户的相对路径./path，也可使用/path绝对路径
        """
        self.platon = platon
        self.cbft = cbft
        self.keystore = keystore
        self.genesis = genesis
        self.deploy_path = deploy_path
        self.net_type = net_type
        self.syncmode = syncmode
        try:
            file_exists(platon, cbft, keystore, genesis)
        except Exception as e:
            log.error(e)
            raise e

    def run_ssh(self, ssh, cmd, password=None):
        """
        执行ssh命令，sudo -S -p '' cmd 时，可以添加password字段
        :param ssh: 连接对象
        :param cmd: 需要执行的命令
        :param password: 密码，或者后续输入
        :return:
        """
        return run_ssh(ssh, cmd, password)

    def start(self,
              ssh,
              url,
              port=16789,
              rpcport=6789,
              cmd=None,
              mpcactor=None,
              vcactor=None) -> bool:
        """
        启动一个节点;
        :param ssh:ssh连接对象
        :param url: 配置文件中的url
        :param port: p2p端口
        :param rpcport: rpc端口或ws端口
        :param cmd: 启动命令
        :param mpcactor: mpc账户，不需要0x
        :return:
            bool
        """
        if not cmd:
            base_ws = '--identity "platon" --verbosity 4 --debug --ws --wsorigins "*" --txpool.nolocals --wsapi "db,platon,net,web3,miner,admin,personal" --wsaddr 0.0.0.0'
            base_http = '--identity "platon" --verbosity 4 --debug --rpc --txpool.nolocals --rpcapi "db,platon,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0'
            base_ws += ' --syncmode "{}"'.format(self.syncmode)
            base_http += ' --syncmode "{}"'.format(self.syncmode)
            if self.net_type:
                base_http = base_http + " --" + self.net_type
                base_ws = base_ws + " --" + self.net_type
            if parse.splittype(url)[0] == "ws":
                if mpcactor:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --wsport {} --mpc --mpc.actor {} > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_ws, self.deploy_path,
                        port, port, rpcport, "0x" + str(mpcactor),
                        self.deploy_path, port)
                elif vcactor:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --wsport {} --vc --vc.actor {} --vc.password 88888888 > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_ws, self.deploy_path,
                        port, port, rpcport, "0x" + str(vcactor),
                        self.deploy_path, port)
                else:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --wsport {} > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_ws, self.deploy_path,
                        port, port, rpcport, self.deploy_path, port)
            elif parse.splittype(url)[0] == "http":
                if mpcactor:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --rpcport {} --mpc --mpc.actor {} > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_http, self.deploy_path,
                        port, port, rpcport, "0x" + str(mpcactor),
                        self.deploy_path, port)
                elif vcactor:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --rpcport {} --vc --vc.actor {} --vc.password 88888888 > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_http, self.deploy_path,
                        port, port, rpcport, "0x" + str(vcactor),
                        self.deploy_path, port)
                else:
                    cmd = '''nohup {}/node-{}/platon {} --datadir {}/node-{}/data --port {} --rpcport {} > {}/node-{}/nohup.out 2>&1 &'''.format(
                        self.deploy_path, port, base_http, self.deploy_path,
                        port, port, rpcport, self.deploy_path, port)
            else:
                raise Exception("url连接类型不正确")
        self.run_ssh(ssh, cmd)
        result = self.run_ssh(
            ssh, "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}" %
            str(rpcport))
        if not result:
            return False
        else:
            return True

    def init(self, ssh, port):
        """
        初始化
        :param ssh:
        :param port:
        :param cmd:
        :return:
        """
        cmd = '{}/node-{}/platon --datadir {}/node-{}/data  --config {}/node-{}/config.json init {}/node-{}/genesis.json '.format(
            self.deploy_path, port, self.deploy_path, port, self.deploy_path,port,self.deploy_path,port)
        s = self.run_ssh(ssh, cmd)
        return s

    def clean_blockchain(self, ssh, port, password):
        """
        清空节点目录信息
        :param ssh:
        :param port:
        :return:
        """
        self.run_ssh(
            ssh,
            "sudo -S -p '' rm -rf {}/node-{}".format(self.deploy_path,
                                                     port), password)
        self.run_ssh(ssh, "mkdir -p {}/node-{}".format(self.deploy_path, port))

    def clean_log(self, ssh, port):
        """
        清空日志信息
        :param ssh:
        :param port:
        :return:
        """
        self.run_ssh(
            ssh, "rm -rf {}/node-{}/nohup.out".format(self.deploy_path, port))
        self.run_ssh(ssh,
                     "rm -rf {}/node-{}/log".format(self.deploy_path, port))
        self.run_ssh(ssh,
                     'mkdir -p {}/node-{}/log'.format(self.deploy_path, port))

    def upload_platon(self, ssh, sftp, port):
        """
        上传platon二进制文件
        :param ssh:
        :param sftp:
        :param port:
        :return:
        """
        self.run_ssh(ssh,
                     "rm -rf {}/node-{}/platon".format(self.deploy_path, port))
        sftp.put(self.platon,
                 '{}/node-{}/platon'.format(self.deploy_path, port))
        self.run_ssh(
            ssh, 'chmod +x {}/node-{}/platon'.format(self.deploy_path, port))

    def upload_nodekey(self, ssh, sftp, nodekey, ip, port):
        """
        上传nodekey
        :param ssh:
        :param sftp:
        :param nodekey:
        :param ip:
        :param port:
        :return:
        """
        nodekey_dir = gen_node_tmp(conf.NODEKEY, str(ip), str(port))
        if not os.path.exists(nodekey_dir):
            os.makedirs(nodekey_dir)
        nodekey_file = os.path.join(nodekey_dir, "nodekey")
        with open(nodekey_file, 'w', encoding="utf-8") as f:
            f.write(nodekey)
        self.run_ssh(
            ssh, 'mkdir -p {}/node-{}/data/'.format(self.deploy_path, port))
        remote_nodekey_path = '{}/node-{}/data/nodekey'.format(
            self.deploy_path, port)
        sftp.put(nodekey_file, remote_nodekey_path)

    def upload_keystore(self, ssh, sftp, port):
        """
        上传钱包文件
        :param ssh:
        :param sftp:
        :param port:
        :return:
        """
        self.run_ssh(
            ssh,
            'mkdir -p {}/node-{}/data/keystore'.format(self.deploy_path, port))
        remote_keystore = '{}/node-{}/data/keystore/UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821'.format(
            self.deploy_path, port)
        sftp.put(self.keystore, remote_keystore)

    def create_keystore(self, ssh, port, password="88888888"):
        """
        创建钱包文件
        :param ssh:
        :param port:
        :param password:
        :return:
        """
        cmd = "{}/node-{}/platon account new --datadir {}/node-{}/data".format(
            self.deploy_path, port, self.deploy_path, port)
        stdin, stdout, _ = ssh.exec_command("source /etc/profile;%s" % cmd)
        stdin.write(str(password) + "\n")
        stdin.write(str(password) + "\n")
        log.info(stdout.readlines())

    def upload_static_json(self, sftp, port, static_node_file):
        """
        上传static_node.json
        :param sftp:
        :param port:
        :param static_node_file:
        :return:
        """
        remote_static_path = '{}/node-{}/data/static-nodes.json'.format(
            self.deploy_path, port)
        sftp.put(static_node_file, remote_static_path)

    def upload_genesis_json(self, sftp, port, genesis_file):
        """
        上传genesis.json
        :param sftp:
        :param port:
        :param genesis_file:
        :return:
        """
        remote_genesis_path = '{}/node-{}/genesis.json'.format(
            self.deploy_path, port)
        sftp.put(genesis_file, remote_genesis_path)

    def upload_config_json(self, sftp, port, config_file):
        """
        上传genesis.json
        :param sftp:
        :param port:
        :param genesis_file:
        :return:
        """
        remote_config_path = '{}/node-{}/config.json'.format(
            self.deploy_path, port)
        sftp.put(config_file, remote_config_path)

    def upload_cbft_json(self, sftp, port):
        """
        上传cbft.json
        :param sftp:
        :param port:
        :return:
        """
        remote_cbft_path = '{}/node-{}/data/cbft.json'.format(
            self.deploy_path, port)
        sftp.put(self.cbft, remote_cbft_path)

    def check_deploy_status(self, node_list):
        """
        校验部署结果
        :param node_list:
        :return:
        """
        fail_list = []
        time.sleep(10)
        for node in node_list:
            w3 = connect_web3(node["url"])
            if not w3.isConnected():
                fail_info = str(node["host"]) + ":" + str(node["port"])
                fail_list.append(fail_info)
        if len(fail_list) > 0:
            raise Exception("部署失败：启动失败的节点如下{}".format(fail_list))
        else:
            log.info("所有节点启动成功")

    def stop_of_yml(self, node_yml: str):
        """
        根据配置文件，关闭节点，关闭后节点无法重启，只能重新部署链
        :param node_yml: 节点配置文件路径
        :return:
        """
        collusion_list, nocollusion_list = get_node_list(node_yml)
        node_list = collusion_list + nocollusion_list
        self.stop_of_list(node_list)

    def stop_of_list(self, node_list: list):
        """
        根据节点列表，以kill -9 的方式关闭节点
        :param node_list: 节点列表
        :return:
        """
        run_thread(node_list, self.stop)

    def stop(self, nodedict):
        """
        以kill -9的方式停止一个节点，关闭后节点无法重启，只能重新部署链
        :param nodedict:
        :return:
        """
        ip = nodedict['host']
        sshport = nodedict.get("sshport", 22)
        username = nodedict['username']
        password = nodedict['password']
        port = nodedict.get("port", "6789")
        ssh, _, t = connect_linux(ip, username, password, sshport)
        self.run_ssh(
            ssh,
            "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}|xargs kill -9"
            % port)
        t.close()

    def kill_of_yaml(self, node_yaml):
        """
        根据节点配置文件，以kill方式关闭节点,关闭后，节点还能被重启
        :param node_yaml: 节点配置文件路径
        :return:
        """
        collusion_list, nocollusion_list = get_node_list(node_yaml)
        node_list = collusion_list + nocollusion_list
        self.kill_of_list(node_list)

    def kill_of_list(self, node_list):
        """
        根据节点列表，以kill方式关闭节点
        :param node_list:节点列表
        :param wait_time:kill超时时间
        :return:
        """
        run_thread(node_list, self.kill)

    def kill(self, nodedict):
        """
        以kill方式关闭一个节点,关闭后，节点还能被重启
        :param nodedict: 连接对象
        :return:
        """
        ip = nodedict['host']
        sshport = nodedict.get("sshport", 22)
        username = nodedict['username']
        password = nodedict['password']
        port = nodedict.get("port", "16789")
        ssh, _, t = connect_linux(ip, username, password, sshport)
        self.run_ssh(
            ssh,
            "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}|xargs kill"
            % port)
        time.sleep(5)
        result = self.run_ssh(
            ssh,
            "ps -ef|grep platon|grep %s|grep -v grep|awk {'print $2'}" % port)
        t.close()
        if result:
            raise Exception("进程关闭失败")

    def booms(self, node_yaml):
        """
        根据节点配置文件，关闭节点机器所有platon进程，关闭后节点无法重启
        :param node_yaml: 节点配置文件路径
        :return:
        """
        collusion_list, nocollusion_list = get_node_list(node_yaml)
        node_list = collusion_list + nocollusion_list
        self.booms_of_list(node_list)

    def booms_of_list(self, node_list):
        """
        根据节点列表，关闭节点机器所有platon进程
        :param node_list:节点列表
        :return:
        """
        run_thread(node_list, self.boom)

    def boom(self, nodedict):
        """
        关闭机器所有platon进程
        :param nodedict:
        :return:
        """
        ip = nodedict.get('host')
        sshport = nodedict.get("sshport", 22)
        username = nodedict.get('username')
        password = nodedict.get('password')
        ssh, _, t = connect_linux(ip, username, password, sshport)
        self.run_ssh(ssh, "killall -9 platon")
        t.close()

    def dependency(self, node_list):
        """
        配置服务器依赖
        :param node_list:
        :return:
        cmd:sudo -S -p '' sed -i '$a # value' file
        """
        run_thread(node_list, self.install_dependency, conf.MPCLIB)

    def install_dependency(self, nodedict, file=conf.MPCLIB):
        """
        配置服务器依赖
        :param nodedict:
        :param file:
        :return:
        """
        global lock
        lock.acquire()
        try:
            ssh, sftp, t = connect_linux(nodedict["host"],
                                         nodedict["username"],
                                         nodedict["password"],
                                         nodedict.get("sshport", 22))
        except Exception as e:
            raise e
        self.run_ssh(ssh, "sudo -S -p '' ntpdate 0.centos.pool.ntp.org",
                     nodedict["password"])
        pwd_list = self.run_ssh(ssh, "pwd")
        pwd = pwd_list[0].strip("\r\n")
        cmd = r"sudo -S -p '' sed -i '$a export LD_LIBRARY_PATH={}/mpclib' /etc/profile".format(
            pwd)
        is_have_mpclib = self.run_ssh(ssh, 'ls|grep "mpclib"')

        # self.run_ssh(
        #     ssh,
        #     "sudo -S -p '' apt-get install libgmpxx4ldbl libgmp-dev libprocps4-dev",
        #     nodedict["password"])

        if not is_have_mpclib:
            sftp.put(file, os.path.basename(file))
            self.run_ssh(ssh, "tar -zxvf ./{}".format(os.path.basename(file)))
            self.run_ssh(ssh, "mv ./platon-mpc-ubuntu-amd64-0.5.0/ ./mpclib")
            self.run_ssh(ssh, cmd, nodedict["password"])
            self.run_ssh(ssh, "rm -rf ./{}".format(os.path.basename(file)))
            # self.run_ssh(
            #     ssh, "sudo -S -p '' apt-get install libboost-all-dev -y", nodedict["password"])
            # self.run_ssh(
            #     ssh, "sudo -S -p '' apt-get install llvm-6.0-dev llvm-6.0 libclang-6.0-dev -y", nodedict["password"])
            self.run_ssh(
                ssh,
                "sudo -S -p '' apt-get install libgmpxx4ldbl libgmp-dev libprocps4-dev",
                nodedict["password"])
        t.close()
        lock.release()

    def generate_genesis_json(self, genesis_json, init_node):
        """
        生成创世文件
        :param genesis_json:创世文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        log.info("生成genesis.json")
        genesis_file = genesis_json
        genesis_data = LoadFile(self.genesis).get_data()
        genesis_data['config']['cbft']["initialNodes"] = init_node
        if not os.path.exists(os.path.dirname(genesis_file)):
            os.makedirs(os.path.dirname(genesis_file))
        with open(genesis_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(genesis_data))
        return genesis_file

    def generate_config_json(self, config_json, init_node):
        """
        修改启动配置文件
        :param config_json:ppos配置文件保存路径
        :param init_node: 初始出块节点enode
        :return:
        """
        log.info("增加种子节点到config.json配置文件")
        config_file = config_json
        config_data = LoadFile(self.config).get_data()
        config_data['node']['P2P']["BootstrapNodes"] = init_node
        if not os.path.exists(os.path.dirname(config_file)):
            os.makedirs(os.path.dirname(config_file))
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_data))
        return config_file

    def generate_static_node_json(self,
                                  static_nodes,
                                  static_node_file=conf.STATIC_NODE_FILE):
        """
        生成节点互连文件
        :param static_nodes: 共识节点enode
        :return:
        """
        log.info("生成static-node.json")
        num = 0
        with open(static_node_file, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i in static_nodes:
                num += 1
                if num < len(static_nodes):
                    f.write('\"' + i + '\",\n')
                else:
                    f.write('\"' + i + '\"\n')
            f.write(']')
        return static_node_file

    def check_node_yml(self, node_yml):
        """
        校验配置文件，补充必要的字段
        :param node_yml:节点配置文件路径
        :return:
         -  host: 10.10.8.237
            port: 16789
            rpcport: 6789
            username: juzhen
            password: Platon123!
            id: 0afbd5564f886966493c2f4efb25d...df67474ff3bd6ce
            nodekey: 0b304c9e039b62269be...1adef94e8e114d7d
            url: http://10.10.8.237:6789
        """
        collusion_list, nocollusion_list = get_node_list(node_yml)
        result = {}
        result_collusion_list = []
        result_nocollusion_list = []
        update = 0
        if len(collusion_list) >= 1:
            for nodedict in collusion_list:
                nodedict, update = self.handle_nodedict(nodedict, update)
                result_collusion_list.append(nodedict)
            result["collusion"] = result_collusion_list
        if len(nocollusion_list) >= 1:
            for nodedict in nocollusion_list:
                nodedict, update = self.handle_nodedict(nodedict, update)
                result_nocollusion_list.append(nodedict)
            result["nocollusion"] = result_nocollusion_list
        if update == 1:
            with open(node_yml, encoding="utf-8", mode="w") as f:
                yaml.dump(result, f, Dumper=yaml.RoundTripDumper)

    def handle_nodedict(self, nodedict, update):
        """
        校验节点信息，对必要参数进行补充
        :param nodedict: 节点信息
        :return:
        """
        if not nodedict.get("id") or not nodedict.get("nodekey"):
            update = 1
            nodekey, id = generate_key()
            nodedict["id"] = id
            nodedict["nodekey"] = nodekey
        if not nodedict.get("port"):
            update = 1
            nodedict["port"] = 16789
        if not nodedict.get("rpcport"):
            update = 1
            nodedict["rpcport"] = 6789
        if not nodedict.get("url"):
            update = 1
            if nodedict.get("protocol") == "ws":
                nodedict["url"] = "ws://{}:{}".format(nodedict["host"],
                                                      nodedict["rpcport"])
            else:
                nodedict["url"] = "http://{}:{}".format(
                    nodedict["host"], nodedict["rpcport"])
        return nodedict, update

    def start_of_list(self,
                      collusion_list,
                      nocollusion_list=None,
                      genesis_file=None,
                      static_node_file=None,
                      is_need_init=True,
                      genesis_path=conf.GENESIS_TMP,
                      clean=False):
        """
        根据节点列表，启动节点
        :param collusion_list: 共识节点列表，当共识节点为空且is_need_init=True，genesis_file不能为空
        :param nocollusion_list: 非共识节点列表
        :param genesis_file: genesis.json文件路径，is_need_init=True时且genesis_file为空时，会根据共识节点列表生成
        :param static_node_file: 共识节点互连文件，为空时会根据共识节点生成
        :param is_need_init: 是否需要初始化，初始化会删除原platon部署目录的所有数据,is_need_init=Flase时，会使用kill方式关闭节点
        :param genesis_path: 新生成的genesis.json保存路径
        :param clean: 是否删除platon部署目录的数据，is_need_init=True时，该参数无效
        :return:
        """
        if nocollusion_list is None and collusion_list is None:
            raise Exception("节点为None")
        elif nocollusion_list is None:
            node_list = collusion_list
        elif collusion_list is None:
            node_list = nocollusion_list
        else:
            node_list = collusion_list + nocollusion_list
        static_nodes, init_node = generate_init_node(collusion_list)
        if is_need_init:
            if not genesis_file:
                genesis_file = self.generate_genesis_json(
                    genesis_path, init_node)
            if not static_node_file:
                static_node_file = self.generate_static_node_json(static_nodes)
        log.info("关闭当前机器中使用配置端口的platon进程")
        if is_need_init:
            self.stop_of_list(node_list)
        else:
            self.kill_of_list(node_list)
        run_thread(node_list, self.start_node, genesis_file, static_node_file,
                   is_need_init, clean)
        self.check_deploy_status(node_list)

    def start_all_node(self,
                       node_yml,
                       genesis_file=None,
                       static_node_file=None,
                       is_need_init=True,
                       genesis_path=conf.GENESIS_TMP,
                       clean=False):
        """
        根据节点配置文件，启动节点
        :param node_yml: 节点配置文件
        :param genesis_file: genesis.json文件路径，is_need_init=True时且genesis_file为空时，会根据共识节点列表生成
        :param static_node_file: 共识节点互连文件，为空时会根据共识节点生成
        :param is_need_init: 是否需要初始化，初始化会删除原platon部署目录的所有数据
        :param genesis_path: 新生成的genesis.json保存路径
        :param clean: 是否删除platon部署目录的数据，is_need_init=True时，该参数无效
        :return:
        """
        self.check_node_yml(node_yml)
        collusion_list, nocollusion_list = get_node_list(node_yml)
        self.start_of_list(collusion_list,
                           nocollusion_list,
                           genesis_file=genesis_file,
                           static_node_file=static_node_file,
                           is_need_init=is_need_init,
                           genesis_path=genesis_path,
                           clean=clean)

    def start_node(self,
                   nodedict,
                   genesis_file,
                   static_node_file,
                   is_init=True,
                   clean=False):
        """
        启动节点
        :param nodedict: 节点信息
        :param genesis_file: genesis.json文件路径
        :param static_node_file: 共识节点互连文件
        :param is_init: 是否需要初始化，初始化会删除原platon部署目录的所有数据
        :param clean: 是否删除platon部署目录的数据，is_init=True时，该参数无效
        :return:
        """
        ip = nodedict['host']
        port = nodedict.get("port", "16789")
        rpcport = nodedict.get("rpcport", "6789")
        sshport = nodedict.get("sshport", 22)
        username = nodedict["username"]
        password = nodedict["password"]
        mpcactor = nodedict.get("mpcactor", None)
        vcactor = nodedict.get("vcactor", None)
        ppos = nodedict.get("ppos", None)
        url = nodedict["url"]
        ssh, sftp, t = connect_linux(ip, username, password, sshport)
        if clean or is_init:
            self.clean_blockchain(ssh, port, password)
        self.clean_log(ssh, port)
        self.upload_platon(ssh, sftp, port)
        if is_init:
            sftp.put(conf.SPLIT_LOG_SCRIPT,
                     "{}/node-{}/split_log.py".format(self.deploy_path, port))
            if genesis_file is None:
                raise Exception("需要初始化时，genesis_file不能为空")
            self.upload_genesis_json(sftp, port, genesis_file)
            _ = self.init(ssh, port=port)
            self.upload_cbft_json(sftp, port)
            if static_node_file:
                self.upload_static_json(sftp, port, static_node_file)
        nodekey = nodedict["nodekey"]
        self.upload_nodekey(ssh, sftp, nodekey, ip, port)
        self.upload_keystore(ssh, sftp, port)
        self.start(ssh,
                   url,
                   port=port,
                   rpcport=rpcport,
                   cmd=nodedict.get("cmd", None),
                   mpcactor=mpcactor,
                   vcactor=vcactor)
        t.close()


class AutoDeployPlaton(BaseDeploy):
    def __init__(
            self,
            platon=conf.PLATON_BIN,
            cbft=conf.CBFT,
            keystore=conf.KEYSTORE,
            genesis=conf.GENESIS_TEMPLATE,
            deploy_path=conf.DEPLOY_PATH,
            net_type=None,
            syncmode="full",
            sup_template=conf.SUP_TEMPLATE,
            sup_tmp=conf.SUP_TMP,
            is_metrics=False,
            config=conf.PLATON_CONFIG_PATH,
    ):
        super(AutoDeployPlaton, self).__init__(platon, cbft, keystore, genesis, deploy_path, net_type, syncmode)
        self.sup_template = sup_template
        self.sup_tmp = sup_tmp
        self.is_metrics = is_metrics
        self.config = config
        if self.is_metrics:
            import requests
            url = "http://10.10.8.16:8086/query"
            del_platon = {"q": "DROP DATABASE platon"}
            create_platon = {"q": "CREATE DATABASE platon"}
            requests.post(url=url, data=del_platon)
            requests.post(url=url, data=create_platon)

    def deploy_all_supervisor(self, node_list):
        """
        根据节点列表部署或启动supervisor
        :param node_list:
        :return:
        """
        for node in node_list:
            self.deploy_supervisor(node)

    def deploy_supervisor(self, node):
        """
        部署supervisor
        :param node:
        :return:
        """
        tmp_dir = gen_node_tmp(self.sup_tmp, node["host"], str(node["port"]))
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        tmp = os.path.join(tmp_dir, "supervisord.conf")
        self.update_conf(node, self.sup_template, tmp)
        ssh, sftp, t = connect_linux(node["host"], node["username"],
                                     node["password"], node.get("sshport", 22))
        self.run_ssh(ssh, "mkdir -p ./tmp")
        sftp.put(tmp, "./tmp/supervisord.conf")
        supervisor_pid_str = self.run_ssh(
            ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
        if len(supervisor_pid_str) > 0:
            self.judge_restart_supervisor(ssh, supervisor_pid_str, node)
        else:
            self.run_ssh(ssh, "sudo -S -p '' apt update", node["password"])
            self.run_ssh(ssh, "sudo -S -p '' apt install -y supervisor",
                         node["password"])
            self.run_ssh(
                ssh,
                "sudo -S -p '' cp ./tmp/supervisord.conf /etc/supervisor/",
                node["password"])
            supervisor_pid_str = self.run_ssh(
                ssh, "ps -ef|grep supervisord|grep -v grep|awk {'print $2'}")
            if len(supervisor_pid_str) > 0:
                self.judge_restart_supervisor(ssh, supervisor_pid_str, node)
            else:
                self.run_ssh(ssh, "sudo -S -p '' /etc/init.d/supervisor start",
                             node["password"])
        t.close()

    def judge_restart_supervisor(self, ssh, supervisor_pid_str, node):
        supervisor_pid = supervisor_pid_str[0].strip("\n")
        result = self.run_ssh(
            ssh,
            "sudo -S -p '' supervisorctl stop node-{}".format(node["port"]),
            node["password"])
        if "node-{}".format(node["port"]) not in result[0]:
            self.run_ssh(ssh, "sudo -S -p '' kill {}".format(supervisor_pid),
                         node["password"])
            self.run_ssh(ssh, "sudo -S -p '' killall supervisord",
                         node["password"])
            self.run_ssh(ssh, "sudo -S -p '' sudo apt remove supervisor -y",
                         node["password"])
            self.run_ssh(ssh, "sudo -S -p '' apt update", node["password"])
            self.run_ssh(ssh, "sudo -S -p '' apt install -y supervisor",
                         node["password"])
            self.run_ssh(
                ssh,
                "sudo -S -p '' cp ./tmp/supervisord.conf /etc/supervisor/",
                node["password"])
            self.run_ssh(ssh, "sudo -S -p '' /etc/init.d/supervisor start",
                         node["password"])

    def update_conf(self, node, sup_template, sup_tmp):
        """
        更新supervisor配置
        :param node:
        :param sup_template:
        :param sup_tmp:
        :return:
        """
        conf = configparser.ConfigParser()
        conf.read(sup_template)
        conf.set("inet_http_server", "username", node["username"])
        conf.set("inet_http_server", "password", node["password"])
        conf.set("supervisorctl", "username", node["username"])
        conf.set("supervisorctl", "password", node["password"])
        with open(sup_tmp, "w") as file:
            conf.write(file)

    def gen_deploy_conf(self, node):
        """
        生成supervisor部署platon的配置
        :param node:
        :return:
        """
        port = str(node["port"])
        node_name = "node-" + port
        ssh, sftp, t = connect_linux(node["host"], node["username"],
                                     node["password"], node.get("sshport", 22))
        pwd_list = self.run_ssh(ssh, "pwd")
        pwd = pwd_list[0].strip("\r\n")
        with open(
                gen_node_tmp(self.sup_tmp, node["host"], port) + "/" +
                node_name + ".conf", "w") as fp:
            fp.write("[program:" + node_name + "]\n")
            if not os.path.isabs(self.deploy_path):
                cmd = "{}/{}/{}/platon --identity platon --datadir".format(
                    pwd, self.deploy_path, node_name)
                cmd = cmd + \
                    " {}/{}/{}/data --port ".format(pwd,
                                                    self.deploy_path, node_name) + port
            else:
                cmd = "{}/{}/platon --identity platon --datadir".format(
                    self.deploy_path, node_name)
                cmd = cmd + \
                    " {}/{}/data --port ".format(self.deploy_path,
                                                 node_name) + port
            cmd = cmd + " --syncmode '{}'".format(self.syncmode)
            if self.net_type:
                cmd = cmd + " --" + self.net_type
            if node.get("mpcactor", None):
                cmd = cmd + \
                    " --mpc --mpc.actor {}".format(node.get("mpcactor"))
            if node.get("vcactor", None):
                cmd = cmd + \
                    " --vc --vc.actor {} --vc.password 88888888".format(
                        node.get("vcactor"))
            cmd = cmd + " --debug --verbosity 4"
            # cmd = cmd + " --pprof --pprofaddr 0.0.0.0 --pprofport " + \
            #       node["pprof_port"]
            if parse.splittype(node["url"])[0] == "ws":
                cmd = cmd + " --ws --wsorigins '*' --wsaddr 0.0.0.0 --wsport " + \
                    str(node["rpcport"])
                cmd = cmd + " --wsapi eth,debug,personal,admin,net,web3"
            else:
                cmd = cmd + " --rpc --rpcaddr 0.0.0.0 --rpcport " + str(
                    node["rpcport"])
                cmd = cmd + " --rpcapi platon,debug,personal,admin,net,web3"
            cmd = cmd + " --txpool.nolocals"
            if self.is_metrics:
                cmd = cmd + " --metrics"
                cmd = cmd + " --metrics.influxdb --metrics.influxdb.endpoint http://10.10.8.16:8086"
                cmd = cmd + " --metrics.influxdb.database platon"
                cmd = cmd + \
                    " --metrics.influxdb.host.tag {}:{}".format(
                        node["host"], str(node["port"]))
            if os.path.isabs(self.deploy_path):
                cmd = cmd + " --gcmode archive --nodekey " + \
                    node["path"] + \
                    "{}/{}/data/nodekey".format(self.deploy_path, node_name)
                cmd = cmd + " --config {}/{}/config.json".format (self.deploy_path, node_name)
            else:
                cmd = cmd + " --gcmode archive --nodekey " + \
                    "{}/{}/{}/data/nodekey".format(pwd,
                                                   self.deploy_path, node_name)
                cmd = cmd + " --config {}/{}/{}/config.json".format (pwd,self.deploy_path, node_name)
            fp.write("command=" + cmd + "\n")
            fp.write("environment=LD_LIBRARY_PATH={}/mpclib\n".format(pwd))
            fp.write("numprocs=1\n")
            fp.write("autostart=false\n")
            fp.write("startsecs=3\n")
            fp.write("startretries=3\n")
            fp.write("autorestart=unexpected\n")
            fp.write("exitcode=0\n")
            fp.write("stopsignal=TERM\n")
            fp.write("stopwaitsecs=10\n")
            fp.write("redirect_stderr=true\n")
            if os.path.isabs(self.deploy_path):
                fp.write("stdout_logfile={}/{}/log/platon.log\n".format(
                    self.deploy_path, node_name))
            else:
                fp.write("stdout_logfile={}/{}/{}/log/platon.log\n".format(
                    pwd, self.deploy_path, node_name))
            fp.write("stdout_logfile_maxbytes=200MB\n")
            fp.write("stdout_logfile_backups=20\n")
        t.close()

    def start_node_conf(self, ssh, sftp, port, node, node_name):
        """
        更新supervisor 的conf启动一个节点
        :param ssh:
        :param sftp:
        :param port:
        :param node:
        :param node_name:
        :return:
        """
        global lock
        self.run_ssh(ssh, "rm -rf ./tmp/{}.conf".format(node_name))
        sftp.put(
            gen_node_tmp(self.sup_tmp, node["host"], str(port)) + "/" +
            node_name + ".conf", "./tmp/" + node_name + ".conf")
        lock.acquire()
        try:
            self.run_ssh(
                ssh, "cd ./tmp/" + "; sudo -S -p '' cp " + node_name +
                ".conf /etc/supervisor/conf.d", node["password"])
            self.run_ssh(ssh,
                         "sudo -S -p '' supervisorctl update " + node_name,
                         node["password"])
            self.run_ssh(ssh, "sudo -S -p '' supervisorctl start " + node_name,
                         node["password"])
        finally:
            lock.release()

    def kill(self, nodedict):
        """
        使用supervisor关闭platon进程
        :param nodedict:
        :param value:
        :param wait_time:
        :return:
        """
        ip = nodedict['host']
        username = nodedict['username']
        password = nodedict['password']
        sshport = nodedict.get('sshport', 22)
        ssh, _, t = connect_linux(ip, username, password, sshport)
        log.info("stop node-{}-{}".format(ip, nodedict["port"]))
        self.run_ssh(ssh,
                     "supervisorctl stop node-{}".format(nodedict["port"]))
        t.close()

    def supervisor_deploy_platon(self,
                                 node,
                                 genesis_file,
                                 static_node_file,
                                 is_init=True,
                                 clean=False):
        """
        使用supervisor部署platon，灵活部署
        :param node:
        :param genesis_file:
        :param static_node_file:
        :param is_init:
        :param clean:
        :return:
        """
        self.gen_deploy_conf(node)
        ip = node['host']
        port = str(node.get("port", "16789"))
        username = node["username"]
        password = node["password"]
        sshport = node.get('sshport', 22)
        ssh, sftp, t = connect_linux(ip, username, password, sshport)
        node_name = "node-" + str(port)
        if clean or is_init:
            self.clean_blockchain(ssh, port, password)
        self.clean_log(ssh, port)
        self.upload_platon(ssh, sftp, port)
        self.upload_config_json (sftp, port, self.config)
        if is_init:
            if genesis_file is None:
                raise Exception("需要初始化时，genesis_file不能为空")
            self.upload_genesis_json(sftp, port, genesis_file)
            _ = self.init(ssh, port=port)
            self.upload_cbft_json(sftp, port)
            if static_node_file:
                self.upload_static_json(sftp, port, static_node_file)
        nodekey = node["nodekey"]
        self.upload_nodekey(ssh, sftp, nodekey, ip, port)
        self.upload_keystore(ssh, sftp, port)
        self.start_node_conf(ssh, sftp, port, node, node_name)
        t.close()

    def start_of_list(self,
                      collusion_list,
                      nocollusion_list=None,
                      genesis_file=None,
                      config_file = None,
                      static_node_file=None,
                      is_need_init=True,
                      genesis_path=conf.GENESIS_TMP,
                      clean=False):
        """
        根据节点列表，启动节点
        :param collusion_list: 共识节点列表，当共识节点为空且is_need_init=True，genesis_file不能为空
        :param nocollusion_list: 非共识节点列表
        :param genesis_file: genesis.json文件路径，is_need_init=True时且genesis_file为空时，会根据共识节点列表生成
        :param static_node_file: 共识节点互连文件，为空时会根据共识节点生成
        :param is_need_init: 是否需要初始化，初始化会删除原platon部署目录的所有数据,is_need_init=Flase时，会使用kill方式关闭节点
        :param genesis_path: 新生成的genesis.json保存路径
        :param clean: 是否删除platon部署目录的数据，is_need_init=True时，该参数无效
        :return:
        """
        if nocollusion_list is None and collusion_list is None:
            raise Exception("节点为None")
        elif nocollusion_list is None:
            node_list = collusion_list
        elif collusion_list is None:
            node_list = nocollusion_list
        else:
            node_list = collusion_list + nocollusion_list
        self.stop_of_list(node_list)
        self.deploy_all_supervisor(node_list)
        self.dependency(node_list)
        static_nodes, init_node = generate_init_node(collusion_list)
        if is_need_init:
            if not genesis_file:
                genesis_file = self.generate_genesis_json(
                    genesis_path, init_node)
            if not static_node_file:
                static_node_file = self.generate_static_node_json(static_nodes)
        self.generate_config_json(self.config, static_nodes)
        # for node in node_list:
        #     self.supervisor_deploy_platon(node, genesis_file, static_node_file, is_need_init, clean)
        run_thread(node_list, self.supervisor_deploy_platon, genesis_file,
                   static_node_file, is_need_init, clean)
        self.check_deploy_status(node_list)

    def restart(self, node):
        """
        重启一个节点
        :param node: 节点信息
        :return:
        """
        ip = node['host']
        port = str(node.get("port", "16789"))
        username = node["username"]
        password = node["password"]
        sshport = node.get("sshport", 22)
        ssh, sftp, t = connect_linux(ip, username, password, sshport)
        node_name = "node-" + str(port)
        self.run_ssh(ssh, "supervisorctl stop {}".format(node_name))
        self.run_ssh(ssh, "supervisorctl start {}".format(node_name))
        t.close()

    def restart_list(self, node_list):
        """
        根据节点列表，重启节点
        :param node_list: 节点列表信息
        :return:
        """
        run_thread(node_list, self.restart)
        self.check_deploy_status(node_list)

    def restart_yml(self, node_yml):
        """
        根据配置文件重启节点
        :param node_yml: 节点配置文件
        :return:
        """
        self.check_node_yml(node_yml)
        collusion_list, nocollusion_list = get_node_list(node_yml)
        node_list = collusion_list + nocollusion_list
        self.restart_list(node_list)

    def update_node(self, node):
        """
        根据节点信息更新节点，替换二进制文件
        :param node: 节点信息
        :return:
        """
        ip = node['host']
        port = str(node.get("port", "16789"))
        username = node["username"]
        password = node["password"]
        sshport = node.get("sshport", 22)
        ssh, sftp, t = connect_linux(ip, username, password, sshport)
        self.upload_platon(ssh, sftp, port)
        node_name = "node-" + str(port)
        self.run_ssh(ssh, "supervisorctl restart {}".format(node_name))
        t.close()

    def update_node_list(self, node_list):
        """
        根据节点列表，更新节点
        :param node_list: 节点信息列表
        :return:
        """
        run_thread(node_list, self.update_node)
        self.check_deploy_status(node_list)

    def update_node_yml(self, node_yml):
        """
        根据节点配置文件，更新节点
        :param node_yml: 节点配置文件
        :return:
        """
        self.check_node_yml(node_yml)
        collusion_list, nocollusion_list = get_node_list(node_yml)
        node_list = collusion_list + nocollusion_list
        self.update_node_list(node_list)

    def deploy_default(self, node):
        """
        使用默认参数部署节点（不初始化）
        :param node: 节点信息
        :return:
        """
        self.gen_deploy_conf(node)
        ip = node['host']
        port = str(node.get("port", "16789"))
        username = node["username"]
        password = node["password"]
        sshport = node.get("sshport", 22)
        ssh, sftp, t = connect_linux(ip, username, password, sshport)
        node_name = "node-" + str(port)
        self.clean_blockchain(ssh, port, password)
        self.clean_log(ssh, port)
        self.upload_platon(ssh, sftp, port)
        nodekey = node["nodekey"]
        self.upload_nodekey(ssh, sftp, nodekey, ip, port)
        self.upload_keystore(ssh, sftp, port)
        self.start_node_conf(ssh, sftp, port, node, node_name)
        t.close()

    def deploy_default_list(self, node_list):
        """
        根据节点列表，使用默认参数部署节点
        :param node_list: 节点列表
        :return:
        """
        self.kill_of_list(node_list)
        self.stop_of_list(node_list)
        self.deploy_all_supervisor(node_list)
        run_thread(node_list, self.deploy_default)
        self.check_deploy_status(node_list)

    def deploy_default_yml(self, node_yml):
        """
        根据节点配置文件，使用默认参数部署节点
        :param node_yml: 节点配置文件
        :return:
        """
        self.check_node_yml(node_yml)
        collusion_list, nocollusion_list = get_node_list(node_yml)
        node_list = collusion_list + nocollusion_list
        self.deploy_default_list(node_list)


if __name__ == "__main__":
    s = AutoDeployPlaton()
    # s.deploy_default_yml(abspath("./deploy/node/25_cbft.yml"))
    # s.kill_of_yaml(abspath("./deploy/node/cbft_4.yml"))
    # s.start_all_node(abspath("./deploy/node/cbft_4.yml"))
    # s.kill_of_yaml(abspath("./deploy/node/ppos_7.yml"))
    # s.start_all_node(abspath("./deploy/node/ppos_7.yml"))

    s.kill_of_yaml(abspath("./deploy/node/govern_node_4.yml"))
    s.start_all_node(abspath("./deploy/node/govern_node_4.yml"))

