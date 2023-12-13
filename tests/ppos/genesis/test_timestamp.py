
import pytest
from dacite import from_dict

from common.log import log
from tests.lib import Genesis
from tests.lib.utils import assert_code


@pytest.fixture()
def modify_timestamp_client(new_genesis_env, client_consensus):
    genesis = from_dict(data_class=Genesis, data=new_genesis_env.genesis_config)
    genesis.timestamp = "0x1bad51d73b0"
    new_file = new_genesis_env.cfg.env_tmp + "/genesis_1.0.0.json"
    genesis.to_file(new_file)
    new_genesis_env.deploy_all(new_file)
    yield client_consensus



@pytest.mark.P1
def test_staking_001(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用createStaking()接口失败
          @step:
          - 1. 非共识节点发起质押
          @expect:
          - 1. 质押失败
          """

    client = modify_timestamp_client
    address = client.economic.account.account_with_money['address']
    # step1：非共识节点发起质押
    status = True
    try:
        result = client.staking.create_staking(0, address, address)
    except:
        status = False
    assert status == False


@pytest.mark.P1
def test_staking_002(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getVerifierList()接口成功
          @step:
          - 1. 查询当前结算周期的验证人队列
          @expect:
          - 1. 调用成功，返回码：301200，拉取结算周期验证人列表失败
          """

    client = modify_timestamp_client
    # step1：查询当前结算周期的验证人队列
    result= client.ppos.getVerifierList()
    assert_code(result, 301200)


@pytest.mark.P1
def test_staking_003(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getValidatorList()接口成功
          @step:
          - 1. 查询当前共识周期的验证人列表
          @expect:
          - 1. 查询成功
          """

    client = modify_timestamp_client
    # step1：查询当前共识周期的验证人列表
    result= client.ppos.getValidatorList()
    assert_code(result, 0)


@pytest.mark.P1
def test_staking_004(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getCandidateList()接口成功
          @step:
          - 1. 查询所有实时的候选人列表
          @expect:
          - 1. 查询成功
          """
    client = modify_timestamp_client
    # step1：查询所有实时的候选人列表
    result= client.ppos.getCandidateList()
    assert_code(result, 0)



@pytest.mark.P1
def test_staking_005(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getRelatedListByDelAddr()接口成功
          @step:
          - 1. 查询当前账户地址所委托的节点的NodeID和质押Id
          @expect:
          - 1. 调用成功，返回码：301203，拉取委托关联映射关系失败
          """

    client = modify_timestamp_client
    # step1：查询当前账户地址所委托的节点的NodeID和质押Id
    result= client.ppos.getRelatedListByDelAddr('lat1drz94my95tskswnrcnkdvnwq43n8jt6dmzf8h8')
    assert_code(result, 301203)


@pytest.mark.P1
def test_staking_006(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getDelegateInfo()接口成功
          @step:
          - 1. 查询当前单个节点的委托信息
          @expect:
          - 1. 调用成功，返回码：301205，查询委托详情失败
          """

    client = modify_timestamp_client
    # step1：查询当前单个节点的委托信息
    result= client.ppos.getDelegateInfo(0,'lat1drz94my95tskswnrcnkdvnwq43n8jt6dmzf8h8', client.node.node_id)
    assert_code(result, 301205)


@pytest.mark.P1
def test_staking_007(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getCandidateInfo()接口成功
          @step:
          - 1. 查询当前节点的质押信息
          @expect:
          - 1. 查询成功
          """

    client = modify_timestamp_client
    # step1：查询当前节点的质押信息
    result= client.ppos.getCandidateInfo(client.node.node_id)
    assert_code(result, 0)


@pytest.mark.P1
def test_staking_008(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getPackageReward()接口成功
          @step:
          - 1. 查询当前结算周期的区块奖励
          @expect:
          - 1. 查询成功
          """

    client = modify_timestamp_client
    # step1：查询当前结算周期的区块奖励
    result= client.ppos.getPackageReward()
    assert_code(result, 0)


@pytest.mark.P1
def test_staking_009(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getStakingReward()接口成功
          @step:
          - 1. 查询当前结算周期的质押奖励
          @expect:
          - 1. 查询成功
          """

    client = modify_timestamp_client
    # step1：查询当前结算周期的质押奖励
    result= client.ppos.getStakingReward()
    assert_code(result, 0)


@pytest.mark.P1
def test_staking_010(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getAvgPackTime()接口成功
          @step:
          - 1. 查询打包区块的平均时间
          @expect:
          - 1. 查询成功
          """

    client = modify_timestamp_client
    # step1：查询打包区块的平均时间
    result= client.ppos.getAvgPackTime()
    assert_code(result, 0)



@pytest.mark.P1
def test_restricting_001(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用CreateRestrictingPlan()接口成功
          @step:
          - 1. 查询当前结算周期的区块奖励
          @expect:
          - 1. 调用成功，返回码：301205，查询委托详情失败
          """

    client = modify_timestamp_client
    # step1：查询当前结算周期的区块奖励
    staking_address, _ = client.economic.account.generate_account(client.node.web3, 0)
    plan = [{'Epoch': 1, 'Amount': 10 ** 18 * 1000}]
    status = True
    try:
        result = client.restricting.createRestrictingPlan(staking_address, plan, client.economic.account.account_with_money['address'])
    except:
        status = False
    assert status == False



@pytest.mark.P1
def test_restricting_002(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getRestrictingInfo()接口成功
          @step:
          - 1. 获取锁仓信息
          @expect:
          - 1. 调用成功，返回码：304005，没有在锁仓合约中找到该账户
          """

    client = modify_timestamp_client
    # step1：获取锁仓信息
    result= client.ppos.getRestrictingInfo('lat1drz94my95tskswnrcnkdvnwq43n8jt6dmzf8h8')
    assert_code(result, 304005)


@pytest.mark.P1
def test_reward_001(modify_timestamp_client):
    """
          @describe: 修改创世文件出块时间为未来时间，调用getDelegateReward()接口成功
          @step:
          - 1. 查询账户在各节点未提取委托奖励。
          @expect:
          - 1. 调用成功，返回码：305001，没有查询到委托的信息
          """

    client = modify_timestamp_client
    # step1：获取锁仓信息
    address, _ = client.economic.account.generate_account(client.node.web3, 0)
    result= client.ppos.getDelegateReward(address)
    assert_code(result, 305001)
