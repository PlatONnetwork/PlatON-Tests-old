import os

# 项目基本路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 节点配置文件路径
NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/ppos2_10.yml"))

# FOUR_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/cbft_4.yml"))

GOVERN_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/govern_node_7.yml"))

# vc节点配置文件路径
VC_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/vc_node.yml"))

# Alice节点配置文件路径
ALICE_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/alice.yml"))

# Bob节点配置文件路径
BOB_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/bob.yml"))

PPOS_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/ppos_wyq.yml"))

PPOS_NODE_TEST_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/ppos2_10.yml"))

# ppos系统参数配置文件
PLATON_CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "deploy/config.json"))

# 节点创世文件默认保存位置
GENESIS_TMP = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/tmp/genesis.json"))

# 节点创世文件共存位置
GENESIS_TMP_OTHER = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/tmp/genesis_other/genesis.json"))

# 节点创世文件模板
GENESIS_TEMPLATE = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/template/genesis.json"))

# 节点创世文件模板2
GENESIS_TEMPLATE2 = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/template/genesis2.json"))

# 部署目录
DEPLOY_PATH = r"./dark_test"

# 生成节点互连文件路径
STATIC_NODE_FILE = os.path.abspath(os.path.join(BASE_DIR, 'deploy/rely/tmp/static-nodes.json'))

# 节点私钥路径
NODEKEY = os.path.abspath(os.path.join(BASE_DIR, 'deploy/rely/tmp/nodekey'))

# 创世文件中写入有大量余额的账户
ADDRESS = "0x493301712671Ada506ba6Ca7891F436D29185821"


#钱包私钥集路径
PRIVATE_KEY_LIST = os.path.abspath(os.path.join(BASE_DIR, 'deploy/privatekeyfile4000.txt'))


# 钱包文件路径
KEYSTORE = os.path.abspath(os.path.join(BASE_DIR,
                                        'deploy/rely/keystore/UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821'))

# 该钱包的私钥
PRIVATE_KEY = '0xa11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7'

# 该钱包的公钥
PUBLIC_KEY = 'a28b52294324f17a8e5e15da2c1562494303d694a9ac6ca02c2ae78fd93af69bb454a711883c23d9a96e38b88e389fbb6225fc6578cb22b4905520c8fbd000c3'

# PRIVATE_KEY =   '0x40a2d01c7b10d19dbdd8b0c04be82d368b3d65a0a3f35e5c9c99eb81229298f7'

# 该钱包的公钥
PUBLIC_KEY = 'a28b52294324f17a8e5e15da2c1562494303d694a9ac6ca02c2ae78fd93af69bb454a711883c23d9a96e38b88e389fbb6225fc6578cb22b4905520c8fbd000c3'

# 钱包密码
PASSWORD = "88888888"

# 限制部署共识节点的数量，暂时不支持
NODE_NUMBER = 0

# 默认的部署cbft文件路径
CBFT = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/cbft.json"))

CBFT2 = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/cbft2.json"))
# 修改cbft后保存的文件路径
CBFT_TMP = os.path.abspath(os.path.join(BASE_DIR, 'deploy/rely/tmp/cbft.json'))

# cbft模板路径
CBFT_TEMPLATE = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/template/cbft.json"))

# platon bin文件保存路径
PLATON_BIN = os.path.abspath(os.path.join(BASE_DIR, 'deploy/rely/bin/platon'))

# platon 二进制文件保存路径
PLATON_DIR = os.path.abspath(os.path.join(BASE_DIR, 'deploy/rely/bin'))

# dpos合约abi文件路径
DPOS_CONTRACT_ABI = os.path.abspath(os.path.join(BASE_DIR, 'data/dpos/candidateConstract.json'))

# 种子节点
TEST_NET_NODE = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/test_net.yml"))

GOVERN_NODE_YML = os.path.abspath(os.path.join(BASE_DIR, "deploy/node/govern_node_7.yml"))

# mpclib
MPCLIB = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/mpclib/mpclib.tar.gz"))

# 用例根目录
CASE = os.path.abspath(os.path.join(BASE_DIR, "case"))

# 测试用例模块
CASE_DICT = {dirpath: os.path.abspath(os.path.join(BASE_DIR, CASE, dirpath)) for dirpath in os.listdir(CASE) if
             dirpath != ".pytest_cache" and dirpath != "__pycache__" and dirpath != "mpc" and not os.path.isfile(
                 dirpath)}
# 测试版本
VERSION_DICT = {
    "all": " ".join(CASE_DICT.values()),
    "pangu": " ".join([CASE_DICT["transaction"], CASE_DICT["contract"], CASE_DICT["blockchain"]]),
    "ppos": " ".join([CASE_DICT["transaction"], CASE_DICT["contract"], CASE_DICT["ppos"], CASE_DICT["blockchain"]]),
    "exclude_ppos": " ".join([v for k, v in CASE_DICT.items() if k != "ppos"]),
    "exclude_vc": " ".join([v for k, v in CASE_DICT.items() if k != "vc"]),
}

VERSION = "0.7"
SPLIT_LOG_SCRIPT = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/script/split_log.py"))

SUP_TEMPLATE = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/template/supervisor.conf"))
SUP_TMP = os.path.abspath(os.path.join(BASE_DIR, "deploy/rely/tmp/supervisor/"))
IS_TEST_NET = False


illegal_nodeID = "7ee3276fd6b9c7864eb896310b5393324b6db785a2528c00cc28ca8c3f86fc229a86f138b1f1c8e3a942204c03faeb40e3b22ab11b8983c35dc025de42865990"
#ppos初始化参数
#toekn总量
TOKENTOTAL= 1000000000000000000000000000

# platON基金会账户
FOUNDATIONADDRESS = "0x2B645d169998eb0447A21D0c48a1780d115251a9"

# 锁仓合约账户地址
FOUNDATIONLOCKUPADDRESS = "0x1000000000000000000000000000000000000001"

#质押合约地址
STAKINGADDRESS = "0x1000000000000000000000000000000000000002"

#platON激励池账户
INCENTIVEPOOLADDRESS="0x1000000000000000000000000000000000000003"

#platON开发者激励基金账户
DEVELOPERSADDRESS = "0x60ceca9c1290ee56b98d4e160ef0453f7c40d219"


account_list = ["0x1bA50320f13874Ff682CE64E148df4998481AB7a", "0xFc5F28B97184AE97d8b4496383FBC58328dc7996",
                "0xb203662cE471Ee733e309d783B819fF95d2cA491","0x993B3904519Bb4922949aEA76ADe7731FEe2f9b0",
                "0xbF7E5317229fC5Ee7fe0C854259e2c3774db167C","0xb83e38ba0E807FA5aD1f8Db0a7915C3F1A354e5E"]

privatekey_list = ["0xa3bc47d1d1b576f87cb2e2eede0395b7b78ea5490bf15784f1cfeb90e0b70766",
                   "0x345516b67a63d706785e1a02c0649ce0357d1476e0d0ef3ab2a4e7dbcf2ac800",
                   "0xa2b1984eccdeaf3355ddb585551bb1e70c5f133ec7dffd7a901e0023092d841e",
                   "e3162b25bc017bb785b603b6dcf858df81f8ddc97b8795d7a574f27141bef2a9",
                   "b7d9cb499f42b6af65b34cf8332d06c770825cc4dbc8aa7633b36d162a9e5855",
                   "df6b0517bf4ae3126022912de0ad09f34911621b05e566564eb5fd9fc81668d8"]

no_money = ["0xc0771e98F736887CC6C8bCAc407904B9d52CBCd7",
            "0x68f1971caad82fc946E53B4B021636723d104C0F",
            "0xC31c012414d9a9ccEae0bd8a6918C91Fba4eb700"]

no_money_key = ["0x1d4596a00b57e5030af88e6d95a8d303a9f6dc304189f4fc77396fc64c0eba8b",
                "0xb033323fa4868210235d6ca64ba642690c5866f03a8eb6906a54ba28734",
                "0xa62383dfee442c8cc8875ea8089087b5d330d5f6121079c01103e9ba4870d5e"]