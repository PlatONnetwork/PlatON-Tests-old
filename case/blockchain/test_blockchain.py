'''
@Author: xiaoming
@Date: 2018-12-05 09:30:35
@LastEditors: xiaoming
@LastEditTime: 2019-02-01 16:26:09
@Description: 区块链自动化测试用例
'''
import time

import allure
from hexbytes import HexBytes

from common.connect import connect_linux, connect_web3, run_ssh
from common.load_file import get_node_info, get_node_list
from common.log import log
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton


class TestBuildBlockChain:
    node_yml = conf.NODE_YML
    collusion_list, nocollusion_list = get_node_list(node_yml)
    one_collusion_url = nocollusion_list[0]["url"]
    data = get_node_info(node_yml)
    rpc_urls, enode_list, nodeid_list, _, _ = data["collusion"]
    w3_list = [connect_web3(url) for url in rpc_urls]
    genesis_file = conf.GENESIS_TMP
    auto = AutoDeployPlaton()

    def setup(self):
        self.auto.start_all_node(self.node_yml)

    def setup_class(self):
        self.w3_list = [connect_web3(url) for url in self.rpc_urls]

    def teardown_class(self):
        self.auto.start_all_node(self.node_yml)

    @allure.title("区块增长")
    def test_blocknumber_increase(self):
        '''
        测试块高是否正常增长
        '''
        for w3 in self.w3_list:
            for i in range(91):
                if w3.eth.blockNumber > 0:
                    break
                time.sleep(1)
                if i == 90:
                    raise Exception('区块不增长,块高：{}'.format(w3.eth.blockNumber))

    # TODO: need fix python-sdk nonce bug
    # @allure.title("区块信息是否一致")
    # def test_block_synchronize(self):
    #     '''
    #     测试所有节点区块信息是否一致
    #     '''
    #     w3 = self.w3_list[0]
    #     blocknumber = w3.eth.blockNumber
    #     if blocknumber == 0:
    #         time.sleep(15)
    #         blocknumber = w3.eth.blockNumber
    #     blockinfo = w3.eth.getBlock(blocknumber)['hash']
    #     for w in self.w3_list[1:-1]:
    #         info = w.eth.getBlock(blocknumber)['hash']
    #         assert blockinfo == info, "不同节点的相同块高信息不一致区块号：{}".format(
    #             blocknumber)

    # TODO: need fix python-sdk nonce bug
    # @allure.title("区块连续性，验证hash")
    # def test_hash_continuous(self):
    #     """
    #     测试区块的连续性，验证一定数量的区块，区块哈希必须是连续的
    #     """
    #     w3 = self.w3_list[0]
    #     i = 0
    #     while True:
    #         if w3.eth.blockNumber >= 100:
    #             break
    #         time.sleep(10)
    #         i += 10
    #         if i >= 150:
    #             assert False, "出块不正常"
    #     block_hash = HexBytes(w3.eth.getBlock(1).get("hash")).hex()
    #     for i in range(2, 100):
    #         block = w3.eth.getBlock(i)
    #         parent_hash = HexBytes(block.get("parentHash")).hex()
    #         assert block_hash == parent_hash, "父区块哈希值错误"
    #         block_hash = HexBytes(block.get("hash")).hex()

    @allure.title("不初始化启动节点和不同创世文件的节点互连")
    def test_no_init_no_join_chain(self):
        '''
        不初始化启动节点
        '''
        self.auto.start_of_list(
            self.nocollusion_list[0:1], is_need_init=False, clean=True)
        time.sleep(1)
        w3 = connect_web3(self.one_collusion_url)
        start_block = w3.eth.blockNumber
        time.sleep(10)
        end_block = w3.eth.blockNumber
        assert start_block == end_block, "区块高度增长了，开始块高{}-结束块高{}".format(
            start_block, end_block)
        w3.admin.addPeer(self.enode_list[0])
        time.sleep(5)
        net_num = w3.net.peerCount
        assert net_num == 0, "连接节点数有增加"

    @allure.title("测试部署单节点私链")
    def test_build_one_node_privatechain(self):
        '''
        部署单节点私链
        '''
        auto = AutoDeployPlaton(genesis=conf.GENESIS_TEMPLATE2)
        auto.start_of_list(
            self.nocollusion_list[0:1], genesis_path=conf.GENESIS_TMP_OTHER)
        time.sleep(2)
        w3 = connect_web3(self.one_collusion_url)
        start_block = w3.eth.blockNumber
        log.info("start block number:{}".format(start_block))
        time.sleep(10)
        end_block = w3.eth.blockNumber
        log.info("end block number:{}".format(end_block))
        assert start_block < end_block, "区块高度没有增长"

    @allure.title("测试不同initnode创始文件之间节点互连")
    def test_init_diff_genesis_join_chain(self):
        '''
        使用不同genesis.json，addPeer
        '''
        self.auto.start_of_list(
            self.nocollusion_list[0:1], genesis_path=conf.GENESIS_TMP_OTHER)
        time.sleep(2)
        net_num_1 = self.w3_list[0].net.peerCount
        w3 = connect_web3(self.one_collusion_url)
        w3.admin.addPeer(self.enode_list[0])
        time.sleep(5)
        net_num_2 = self.w3_list[0].net.peerCount
        assert net_num_2 == net_num_1, "节点数有增加"
        peers = w3.net.peerCount
        log.info("加入其他链后，连接节点数{}".format(peers))
        assert peers is 0, "peers节点数不为空"

    @allure.title("测试相同创始文件之间节点互连")
    def test_init_same_genesis_join_chain(self):
        '''
        测试相同的genesis.json节点加入addPeer
        '''
        self.auto.start_of_list(
            self.nocollusion_list[0:1], genesis_file=self.genesis_file)
        time.sleep(2)
        w3 = connect_web3(self.one_collusion_url)
        w3.admin.addPeer(self.enode_list[0])
        time.sleep(5)
        assert w3.net.peerCount > 0, "加入链失败"

    @allure.title("测试区块同步")
    def test_deconsensus_block_synchronize(self):
        '''
        非共识节点块高同步
        '''
        w3 = connect_web3(self.one_collusion_url)
        log.info(w3.net.peerCount)
        time.sleep(10)
        block_number = w3.eth.blockNumber
        assert block_number > 0, "非共识节点同步区块失败，块高：{}".format(block_number)

    @allure.title("测试fast模式同步")
    def test_syncmode(self):
        """
        同步
        :return:
        """
        auto = AutoDeployPlaton(syncmode="fast")
        auto.start_of_list(
            self.nocollusion_list[0:1], genesis_file=self.genesis_file)
        time.sleep(2)
        w3 = connect_web3(self.one_collusion_url)
        w3.admin.addPeer(self.enode_list[0])
        time.sleep(5)
        collusion_w3 = self.w3_list[0]
        if collusion_w3.eth.blockNumber < 250:
            log.info("sleep,非共识节点需要229个块之后才会开始同步")
            time.sleep(250 - collusion_w3.eth.blockNumber)
        assert w3.net.peerCount > 0, "加入链失败"
        assert w3.eth.blockNumber >= 200, "区块同步失败,当前块高{}".format(
            w3.eth.blockNumber)
    # 目前没有测试网配置
    # @allure.title("测试种子节点")
    # def test_testnet(self):
    #     """
    #     测试testnet连接
    #     :return:
    #     """
    #     if conf.IS_TEST_NET:
    #         auto = AutoDeployPlaton(net_type="testnet")
    #         auto.start_all_node(conf.TEST_NET_NODE,
    #                             is_need_init=False, clean=True)
    #         collusion, nocollusion = get_node_list(conf.TEST_NET_NODE)
    #         time.sleep(10)
    #         block_list = []
    #         net_list = []
    #         for nodedict in collusion:
    #             url = nodedict["url"]
    #             w3 = connect_web3(url)
    #             block_list.append(w3.eth.blockNumber)
    #             net_list.append(w3.net.peerCount)
    #         log.info(block_list, net_list)
    #         assert min(block_list) > 0, "区块没有增长"
    #         for net in net_list:
    #             assert net >= len(collusion) - \
    #                 1, "共识节点连接节点数少于{}个".format(len(collusion) - 1)
    #         nocollusion_block_list = []
    #         nocollusion_net_list = []
    #         if max(block_list) < 250:
    #             time.sleep(250 - max(block_list) + 10)
    #         for nodedict in nocollusion:
    #             url = nodedict["url"]
    #             w3 = connect_web3(url)
    #             nocollusion_block_list.append(w3.eth.blockNumber)
    #             nocollusion_net_list.append(w3.net.peerCount)
    #         log.info(nocollusion_block_list, nocollusion_net_list)
    #         assert min(nocollusion_block_list) > 0, "区块没有增长"
    #         for net in nocollusion_net_list:
    #             assert net >= 1, "非共识节点没有连上测试网"
    #     else:
    #         pass

    @allure.title("测试platon文件的版本号")
    def test_platon_versions(self):
        collusion_list, _ = get_node_list(self.node_yml)
        node = collusion_list[0]
        ssh, sftp, t = connect_linux(
            node['host'], username=node['username'], password=node['password'])
        cmd_list = run_ssh(
            ssh, "{}/node-{}/platon version".format(conf.DEPLOY_PATH, node["port"]))
        versions = conf.VERSION
        assert versions in cmd_list[1], "版本号不正确"

    @allure.title("测试重启所有共识节点")
    def test_restart_all(self):
        current_block = self.w3_list[0].eth.blockNumber
        log.info("重启前块高:{}".format(current_block))
        self.auto.restart_list(self.collusion_list)
        log.info("重启所有共识节点成功")
        time.sleep(30)
        after_block = self.w3_list[0].eth.blockNumber
        log.info("重启后块高为:{}".format(after_block))
        assert after_block - current_block >= 10, "重启后区块没有正常增长"
