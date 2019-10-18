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
from ruamel import yaml
from environment.node import Node
from environment.server import Server
from common.abspath import abspath
from common.key import generate_key
from common.load_file import LoadFile
from common.log import log
from environment.account import Account
from environment.config import TestConfig
from conf.settings import DEFAULT_CONF_TMP_DIR


def check_file_exists(*args):
    """
    检查本地文件是否存在
    :param args:
    :return:
    """
    for arg in args:
        if not os.path.exists(os.path.abspath(arg)):
            raise Exception("文件{}不存在".format(arg))


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
        """
        新的环境
        :return: env_id
        """
        if os.path.exists(self.cfg.env_tmp):
            shutil.rmtree(self.cfg.env_tmp)
        os.makedirs(self.cfg.env_tmp)
        return socket.getfqdn(socket.gethostname()) + str(int(time.time()))

    def get_init_nodes(self) -> list:
        """
        获取init node列表
        :return: list
        """
        init_node_list = []
        for node in self.collusion_node_list:
            init_node_list.append({"node": node.enode, "blsPubKey": node.blspubkey})
        return init_node_list

    def get_static_nodes(self) -> list:
        """
        获取static节点enode列表
        :return: list
        """
        static_node_list = []
        for node in self.get_all_nodes():
            static_node_list.append(node.enode)
        return static_node_list

    @property
    def version(self):
        return ""

    @property
    def running(self) -> bool:
        """
        判断所有节点是否在运行
        :return: bool
        """
        for node in self.get_all_nodes():
            if not node.running:
                return False
        return True

    @property
    def max_byzantium(self) -> int:
        """
        最大拜占庭节点数
        :return:
        """
        return get_f(self.collusion_node_config_list)

    @property
    def block_interval(self) -> int:
        """
        出块间隔
        :return:
        """
        period = self.genesis_config["config"]["cbft"].get("period")
        amount = self.genesis_config["config"]["cbft"].get("amount")
        return int(period/1000/amount)

    def get_all_nodes(self) -> list:
        """
        获取所有节点
        :return:
        """
        return self.collusion_node_list + self.normal_node_list

    def get_rand_node(self) -> Node:
        """
        随机获取一个共识节点
        :return:
        """
        return random.choice(self.collusion_node_list)

    def get_a_normal_node(self) -> Node:
        """
        获取第一个普通节点
        :return:
        """
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
        """
        部署所有节点并启动
        1.当传入genesis文件时，使用传入genesis文件部署，不传入使用生成的genesis文件部署
        :param static_file: 指定静态文件，不传默认使用tmp中生成的
        :param genesis_file: 指定genesis， 不传默认使用tmp中生成的
        :return:
        """
        log.info("deploy all node")
        if genesis_file:
            log.info("new genesis")
            self.deploy_nodes(self.get_all_nodes(), static_file, genesis_file)
        else:
            log.info("default genesis")
            self.deploy_nodes(self.get_all_nodes(), static_file, self.cfg.genesis_tmp)
        log.info("deploy success")

    def start_all(self):
        """
        启动所有节点，根据cfg的init_chain的值，判断是否初始化
        :return:
        """
        log.info("start all node")
        self.start_nodes(self.get_all_nodes(), self.cfg.init_chain)

    def stop_all(self):
        """
        停止所有节点
        :return:
        """
        log.info("stop all node")
        self.stop_nodes(self.get_all_nodes())

    def reset_all(self):
        """
        重启所有节点
        :return:
        """
        log.info("restart all node")
        self.reset_nodes(self.get_all_nodes())

    def clean_all(self):
        """
        关闭所有节点，并删除部署节点的目录
        :return:
        """
        log.info("clean all node")
        self.clean_nodes(self.get_all_nodes())

    def clean_db_all(self):
        """
        关闭所有节点，并删除数据库
        :return:
        """
        log.info("clean db all node")
        self.clean_db_nodes(self.get_all_nodes())

    def shutdown(self):
        """
        关闭所有节点，并删除节点部署目录，supervisor节点配置
        :return:
        """
        log.info("shutdown all node")

        def close(node: Node):
            return node.close()

        return self.__executor(close, self.get_all_nodes())

    def start_nodes(self, node_list: list, init_chain=True):
        """
        启动节点
        :param node_list:
        :param init_chain:
        :return:
        """
        def start(node: Node, need_init_chain):
            return node.start(need_init_chain)

        return self.__executor(start, node_list, init_chain)

    def deploy_nodes(self, node_list: list, static_file=None, genesis_file=None):
        """
        部署节点
        1.关闭所有节点，避免相同genesis节点互相影响
        2.重写genesis，static，config
        3.判断是否需要上传static，根据其逻辑压缩本次部署环境的必要信息
        4.依赖安装
        5.上传压缩吧
        6.执行部署节点的逻辑
        :param node_list:
        :param static_file:
        :param genesis_file:
        :return:
        """
        log.info("deploy node")
        self.stop_nodes(node_list)
        # self.parseAccountFile()
        self.rewrite_genesis_file()
        self.rewrite_static_nodes()
        self.rewrite_config_json()
        if not self.cfg.is_need_static:
            self.__compression(None)
        elif static_file:
            self.__compression(static_file)
        else:
            self.__compression(self.cfg.static_node_tmp)
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

    def stop_nodes(self, node_list: list):
        """
        关闭节点
        :param node_list:
        :return:
        """
        def stop(node: Node):
            return node.stop()

        return self.__executor(stop, node_list)

    def reset_nodes(self, node_list: list):
        """
        重启节点
        :param node_list:
        :return:
        """
        def restart(node: Node):
            return node.restart()

        return self.__executor(restart, node_list)

    def clean_nodes(self, node_list: list):
        """
        关闭节点，删除节点数据
        :param node_list:
        :return:
        """
        def clean(node: Node):
            return node.clean()

        return self.__executor(clean, node_list)

    def clean_db_nodes(self, node_list: list):
        """
        关闭节点，清空节点数据库
        :param node_list:
        :return:
        """
        def clean_db(node: Node):
            return node.clean_db()

        return self.__executor(clean_db, node_list)

    def __parse_node(self):
        """
        实例化所有节点
        :return:
        """
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
        """
        上传压缩文件
        :return:
        """
        log.info("upload compression")

        def uploads(server: Server):
            return server.put_compression()

        return self.__executor(uploads, self.server_list)

    def install_all_dependency(self):
        """
        安装依赖
        :return:
        """
        log.info("install rely")

        def install(server: Server):
            return server.install_dependency()

        return self.__executor(install, self.server_list)

    def install_all_supervisor(self):
        """
        安装supervisor
        :return:
        """
        log.info("install supervisor")

        def install(server: Server):
            return server.install_supervisor()

        return self.__executor(install, self.server_list)

    def __parse_servers(self) -> list:
        """
        实例化所有server
        :return:
        """
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
        """
        获取传入节点的块高
        :param node_list:
        :return:
        """
        if not node_list:
            node_list = self.get_all_nodes()
        result = {}
        for node in node_list:
            result[node.node_mark] = node.block_number
        return result

    def check_block(self, need_number=10, multiple=3, node_list=None):
        """
        校验当前链最高区块
        :param need_number:
        :param multiple:
        :param node_list:
        :return:
        """
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
        """
        下载所有节点日志，未测试
        :return:
        """
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

    def rewrite_genesis_file(self):
        """
        重写genesis
        :return:
        """
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

    def rewrite_static_nodes(self):
        """
        重写static
        :return:
        """
        log.info("rewrite static-nodes.json")
        num = 0
        static_nodes = self.get_static_nodes()
        with open(self.cfg.static_node_tmp, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i in static_nodes:
                num += 1
                if num < len(static_nodes):
                    f.write('\"' + i + '\",\n')
                else:
                    f.write('\"' + i + '\"\n')
            f.write(']')

    def rewrite_config_json(self):
        """
        重写config
        :return:
        """
        log.info("rewrite config.json")
        config_data = LoadFile(self.cfg.config_json_file).get_data()
        config_data['node']['P2P']["BootstrapNodes"] = self.get_static_nodes()
        with open(self.cfg.config_json_tmp, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_data, indent=4))

    def __fill_node_config(self, node_config):
        """
        填充node file一些必要的值
        :param node_config:
        :return:
        """
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
        """
        压缩文件
        :param static:
        :return:
        """
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
        shutil.copyfile(self.cfg.config_json_tmp, os.path.join(env_gz, "config.json"))
        if static:
            shutil.copyfile(static, os.path.join(data_dir, "static-nodes.json"))
        t = tarfile.open(env_gz + ".tar.gz", "w:gz")
        t.add(env_gz, arcname=os.path.basename(env_gz))
        t.close()


def create_env(conf_tmp=None, node_file=None, account_file=None, init_chain=True,
               install_dependency=False, install_supervisor=False) -> TestEnvironment:
    if not conf_tmp:
        conf_tmp = DEFAULT_CONF_TMP_DIR
    cfg = TestConfig(conf_tmp=conf_tmp, install_supervisor=install_supervisor, install_dependency=install_dependency, init_chain=init_chain)
    if node_file:
        cfg.node_file = node_file
    if account_file:
        cfg.account_file = account_file
    return TestEnvironment(cfg)


if __name__ == "__main__":
    node_filename = abspath("deploy/node/25_cbft.yml")
    env = create_env(node_file=node_filename)
    # new_cfg = copy.copy(env.cfg)
    # new_cfg.syncmode = "fast"
    # print(env.cfg.syncmode)
    log.info("测试部署")
    env.deploy_all()
    env.deploy_all()
    d = env.block_numbers()
    print(d)
    node = env.get_rand_node()
    node.create_keystore()
    print(node.node_mark)
    time.sleep(80)
    log.info("测试关闭")
    env.stop_all()
    time.sleep(30)
    log.info("测试不初始化启动")
    env.cfg.init_chain = False
    env.start_all()
    time.sleep(60)
    d = env.block_numbers()
    print(d)
    log.info("测试重启")
    env.reset_all()
    time.sleep(60)
    d = env.block_numbers()
    print(d)
    log.info("测试删除数据库")
    env.clean_db_all()
    log.info("删除数据库成功")
    time.sleep(60)
    env.cfg.init_chain = True
    env.start_all()
    time.sleep(30)
    d = env.block_numbers()
    print(d)
    log.info("测试删除所有数据")
    env.clean_all()
    log.info("删除数据成功")
    log.info("重新部署")
    env.deploy_all()
    d = env.block_numbers()
    print(d)
    time.sleep(60)
    d = env.block_numbers()
    print(d)
    env.shutdown()
