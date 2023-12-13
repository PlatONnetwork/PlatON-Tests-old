import time, pytest, rlp

from client_sdk_python.packages.platon_account.internal.transactions import bech32_address_bytes
from hexbytes import HexBytes

from common.key import mock_duplicate_sign
from tests.lib import assert_code, get_the_dynamic_parameter_gas_fee, get_pledge_list, get_governable_parameter_value


def estimated_delegate_withdrew_gas(client):
    node = client.node
    economic = client.economic
    address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    result = client.staking.create_staking(0, address, address)
    assert_code(result, 0)

    # 预估发起委托需要的gas
    data = rlp.encode([rlp.encode(int(1004)), rlp.encode(0), rlp.encode(bytes.fromhex(node.node_id)),
                       rlp.encode(economic.delegate_limit)])
    gas = (21000 + 6000 + 16000 + get_the_dynamic_parameter_gas_fee(data))
    gas_fees = gas * node.eth.gasPrice
    delegate_address, _ = economic.account.generate_account(node.web3, economic.delegate_limit + gas_fees)
    transaction_data = {"to": node.ppos.stakingAddress, "data": data, "from": delegate_address}
    estimated_gas = node.eth.estimateGas(transaction_data)
    assert gas == estimated_gas

    result = client.delegate.delegate(0, delegate_address)
    assert_code(result, 0)
    # 预估撤销委托需要的gas
    staking_blocknum = client.ppos.getCandidateInfo(node.node_id)["Ret"]["StakingBlockNum"]
    data = rlp.encode([rlp.encode(int(1005)), rlp.encode(staking_blocknum), rlp.encode(bytes.fromhex(node.node_id)),
                       rlp.encode(economic.delegate_limit)])
    gas_withdrew = 21000 + 6000 + 8000 + get_the_dynamic_parameter_gas_fee(data)
    transaction_data = {"to": client.node.ppos.stakingAddress, "data": data, "from": delegate_address}
    estimated_gas_withdrew = node.eth.estimateGas(transaction_data)
    assert gas_withdrew == estimated_gas_withdrew
    gas_fees_withdrew = estimated_gas_withdrew * node.eth.gasPrice

    return gas_fees, gas_fees_withdrew, address


@pytest.mark.P1
def test_estimated_gas_001(client_new_node):
    """
       @describe: 委托交易预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起委托成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起委托
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起委托成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    # step2：预估gas
    gas_fees, _, _ = estimated_delegate_withdrew_gas(client)
    print(gas_fees)
    # step1：创建账户，账户余额 = 交易金额 + gas * gasPrice
    delegate_address, _ = client.economic.account.generate_account(client.node.web3,
                                                                   client.economic.delegate_limit + gas_fees)
    print(client.node.eth.getBalance(delegate_address))
    # step3：发起委托
    result = client.delegate.delegate(0, delegate_address)
    assert_code(result, 0)
    balance = client.node.eth.getBalance(delegate_address)
    print(balance)
    assert balance == 0


@pytest.mark.P1
def test_estimated_gas_002(client_new_node):
    """
       @describe: 委托交易预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起委托成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + 委托手续费 + 取消委托手续费
       - 2. 预估gas
       - 3. 发起撤销委托
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起撤销委托
       - 3. 账户金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    economic = client.economic
    # step2 预估gas
    gas_fees, gas_fees_withdrew, _ = estimated_delegate_withdrew_gas(client)

    # step1 创建账户，账户余额 = 交易金额 + 委托手续费 + 取消委托手续费
    delegate_address, _ = client.economic.account.generate_account(client.node.web3,
                                                                   economic.delegate_limit + gas_fees + gas_fees_withdrew)
    result = client.delegate.delegate(0, delegate_address)
    assert_code(result, 0)
    balance = node.eth.getBalance(delegate_address)
    assert balance == gas_fees_withdrew
    # step3 发起撤销委托
    staking_blocknum = client.ppos.getCandidateInfo(node.node_id)["Ret"]["StakingBlockNum"]
    result = client.delegate.withdrew_delegate(staking_blocknum, delegate_address)
    assert_code(result, 0)
    balance = node.eth.getBalance(delegate_address)
    assert balance == economic.delegate_limit


def estimated_staking_gas(client):
    node = client.node
    economic = client.economic
    address, pri_key = client.economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    program_version_sign_ = node.program_version_sign[2:]
    address1 = bech32_address_bytes(address)
    data = HexBytes(rlp.encode([rlp.encode(int(1000)), rlp.encode(0), rlp.encode(address1),
                                rlp.encode(bytes.fromhex(node.node_id)), rlp.encode(client.staking.cfg.external_id),
                                rlp.encode(client.staking.cfg.node_name),
                                rlp.encode(client.staking.cfg.website), rlp.encode(client.staking.cfg.details),
                                rlp.encode(client.economic.create_staking_limit), rlp.encode(0),
                                rlp.encode(node.program_version),
                                rlp.encode(bytes.fromhex(program_version_sign_)),
                                rlp.encode(bytes.fromhex(node.blspubkey)),
                                rlp.encode(bytes.fromhex(node.schnorr_NIZK_prove))]))
    estimated_gas = node.eth.estimateGas({"from": address, "to": node.ppos.stakingAddress, "data": data})
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 32000
    assert estimated_gas == gas
    staking_gas_fees = gas * node.eth.gasPrice
    return staking_gas_fees


@pytest.mark.P1
def test_estimated_gas_003(client_new_node):
    """
       @describe: 质押交易预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起质押成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起质押
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起质押成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    staking_gas_fees = estimated_staking_gas(client)

    staking_address, _ = client.economic.account.generate_account(client.node.web3,
                                                                  client.economic.create_staking_limit + staking_gas_fees)
    result = client.staking.create_staking(0, staking_address, staking_address,
                                           amount=client.economic.create_staking_limit, reward_per=0)
    assert_code(result, 0)
    balance_after = client.node.eth.getBalance(staking_address)
    assert balance_after == 0


@pytest.mark.P1
def test_estimated_gas_004(client_new_node):
    """
       @describe: 修改质押信息预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起修改成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起修改
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起修改成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node_name = "node_name"
    reward_per = 0
    node = client.node
    econnmic = client.economic

    staking_gas_fees = estimated_staking_gas(client)

    address, pri_key = client.economic.account.generate_account(node.web3, econnmic.create_staking_limit * 2)
    result = client.staking.create_staking(0, address, address, amount=econnmic.create_staking_limit)
    assert_code(result, 0)
    balance = node.eth.getBalance(address)

    rlp_reward_per = rlp.encode(reward_per) if reward_per else b''
    data = HexBytes(rlp.encode(
        [rlp.encode(int(1001)), rlp.encode(bech32_address_bytes(address)), rlp.encode(bytes.fromhex(node.node_id)),
         rlp_reward_per,
         rlp.encode(client.staking.cfg.external_id), rlp.encode(node_name), rlp.encode(client.staking.cfg.website),
         rlp.encode(client.staking.cfg.details)]))
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 12000
    estimated_gas = node.eth.estimateGas({"from": address, "to": node.ppos.stakingAddress, "data": data})
    assert gas == estimated_gas
    estimated_edit_gas_fees = estimated_gas * node.eth.gasPrice
    result = client.ppos.editCandidate(address, node.node_id, client.staking.cfg.external_id, node_name,
                                       client.staking.cfg.website, client.staking.cfg.details,
                                       pri_key, reward_per=reward_per)
    assert_code(result, 0)
    time.sleep(3)
    balance1 = client.node.eth.getBalance(address)
    assert balance - estimated_edit_gas_fees == balance1
    result = client.staking.withdrew_staking(address)
    assert_code(result, 0)

    staking_address, pri_key = client.economic.account.generate_account(client.node.web3,
                                                                        client.economic.create_staking_limit + staking_gas_fees + estimated_edit_gas_fees)
    time.sleep(2)
    balance = node.eth.getBalance(staking_address)
    result = client.staking.create_staking(0, staking_address, staking_address,
                                           amount=client.economic.create_staking_limit)
    assert_code(result, 0)
    time.sleep(3)
    balance_befor = node.eth.getBalance(staking_address)
    assert balance - staking_gas_fees - econnmic.create_staking_limit == balance_befor

    rlp_reward_per = rlp.encode(reward_per) if reward_per else b''
    data = HexBytes(rlp.encode(
        [rlp.encode(int(1001)), rlp.encode(bech32_address_bytes(staking_address)),
         rlp.encode(bytes.fromhex(client.node.node_id)),
         rlp_reward_per,
         rlp.encode(client.staking.cfg.external_id), rlp.encode(node_name), rlp.encode(client.staking.cfg.website),
         rlp.encode(client.staking.cfg.details)]))
    estimated_edit_gas = client.node.eth.estimateGas(
        {"from": staking_address, "to": client.node.ppos.stakingAddress, "data": data})
    assert estimated_edit_gas == estimated_gas

    result = client.ppos.editCandidate(staking_address, client.node.node_id, client.staking.cfg.external_id, node_name,
                                       client.staking.cfg.website, client.staking.cfg.details,
                                       pri_key, reward_per=reward_per)
    assert_code(result, 0)
    balance_after = client.node.eth.getBalance(staking_address)
    assert balance_after == 0


@pytest.mark.P1
def test_estimated_gas_005(client_new_node):
    """
       @describe: 增持质押交易预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起增持成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起委托
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起委托成功
       - 3. 账户扣款金额正确
     """

    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    econnmic = client.economic

    gas_fees = estimated_staking_gas(client)
    address, pri_key = client.economic.account.generate_account(node.web3, econnmic.create_staking_limit * 2)
    result = client.staking.create_staking(0, address, address, amount=econnmic.create_staking_limit, reward_per=0)
    assert_code(result, 0)
    balance_befor = node.eth.getBalance(address)

    data = rlp.encode(
        [rlp.encode(int(1002)), rlp.encode(bytes.fromhex(node.node_id)), rlp.encode(0),
         rlp.encode(econnmic.add_staking_limit)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 20000
    estimated_increase_gas = node.eth.estimateGas({"from": address, "to": node.ppos.stakingAddress, "data": data})
    assert gas == estimated_increase_gas
    gas_increase_fees = gas * node.eth.gasPrice
    result = client.staking.increase_staking(0, address)
    assert_code(result, 0)
    balance = node.eth.getBalance(address)
    assert balance_befor - econnmic.add_staking_limit - gas_increase_fees == balance
    result = client.staking.withdrew_staking(address)
    assert_code(result, 0)

    amount = econnmic.create_staking_limit + econnmic.add_staking_limit + gas_fees + gas_increase_fees
    staking_address, _ = client.economic.account.generate_account(node.web3, amount)
    result = client.staking.create_staking(0, staking_address, staking_address, amount=econnmic.create_staking_limit,
                                           reward_per=0)
    assert_code(result, 0)
    time.sleep(2)
    balance1 = node.eth.getBalance(staking_address)
    assert amount - econnmic.create_staking_limit - gas_fees == balance1

    data = rlp.encode(
        [rlp.encode(int(1002)), rlp.encode(bytes.fromhex(node.node_id)), rlp.encode(0),
         rlp.encode(econnmic.add_staking_limit)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 20000
    estimated_increase_gas = node.eth.estimateGas(
        {"from": staking_address, "to": node.ppos.stakingAddress, "data": data})
    assert gas == estimated_increase_gas

    result = client.staking.increase_staking(0, staking_address)
    assert_code(result, 0)
    time.sleep(2)
    balance2 = node.eth.getBalance(staking_address)
    assert balance2 == 0


@pytest.mark.P1
def test_estimated_gas_006(client_new_node):
    """
       @describe: 撤销质押交易预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起撤销成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起委托
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起委托成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    econnmic = client.economic

    gas_fees = estimated_staking_gas(client)
    address, _ = client.economic.account.generate_account(node.web3, econnmic.create_staking_limit * 2)
    result = client.staking.create_staking(0, address, address, amount=econnmic.create_staking_limit, reward_per=0,
                                           transaction_cfg={})
    assert_code(result, 0)
    balance_after = node.eth.getBalance(address)
    assert econnmic.create_staking_limit - gas_fees == balance_after

    data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node.node_id))])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 6000 + 20000
    estimated_gas = node.eth.estimateGas({"from": address, "to": node.ppos.stakingAddress, "data": data})
    assert gas == estimated_gas
    gas_withdrew_fees = gas * node.eth.gasPrice

    result = client.staking.withdrew_staking(address)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(address)
    assert balance_after - gas_withdrew_fees + econnmic.create_staking_limit == balance1

    amount = econnmic.create_staking_limit + gas_fees + gas_withdrew_fees
    staking_address, _ = client.economic.account.generate_account(node.web3, amount)
    result = client.staking.create_staking(0, staking_address, staking_address, amount=econnmic.create_staking_limit,
                                           reward_per=0)
    assert_code(result, 0)
    balance1 = node.eth.getBalance(staking_address)
    assert amount - econnmic.create_staking_limit - gas_fees == balance1

    data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node.node_id))])
    estimated_withdrew_gas = node.eth.estimateGas(
        {"from": staking_address, "to": node.ppos.stakingAddress, "data": data})
    assert estimated_gas == estimated_withdrew_gas

    result = client.staking.withdrew_staking(staking_address)
    assert_code(result, 0)
    balance2 = node.eth.getBalance(staking_address)
    assert balance2 == econnmic.create_staking_limit


@pytest.mark.P1
def test_estimated_gas_007(client_new_node):
    """
       @describe: 举报惩罚预估gas,账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起举报成功
       @step:
       - 1. 创建账户，账户余额 = 交易金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起举报
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起举报成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    economic = client.economic
    address, _ = client.economic.account.generate_account(node.web3, economic.create_staking_limit)
    staking_address, _ = client.economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    result = client.staking.create_staking(0, staking_address, staking_address, amount=economic.create_staking_limit,
                                           reward_per=0)
    assert_code(result, 0)
    economic.wait_settlement(node)
    economic.wait_consensus(node)
    validatorlist = get_pledge_list(client.ppos.getValidatorList)
    assert node.node_id in validatorlist

    blocknumber = node.eth.blockNumber
    report_information = mock_duplicate_sign(1, node.nodekey, node.blsprikey, blocknumber)
    data = rlp.encode([rlp.encode(int(3000)), rlp.encode(1), rlp.encode(report_information)])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 21000 + 21000 + 21000
    estimated_gas = node.eth.estimateGas({"to": client.ppos.penaltyAddress, "data": data, "from": address})
    gas_fees = gas * node.eth.gasPrice
    assert gas == estimated_gas

    pledge_amount1 = client.ppos.getCandidateInfo(client.node.node_id)['Ret']['Released']
    penalty_ratio = int(get_governable_parameter_value(client, 'slashFractionDuplicateSign'))
    proportion_ratio = int(get_governable_parameter_value(client, 'duplicateSignReportReward'))
    proportion_reward, _ = economic.get_report_reward(pledge_amount1, penalty_ratio, proportion_ratio)

    report_address, _ = client.economic.account.generate_account(node.web3, gas_fees)
    estimated_slash_gas = node.eth.estimateGas({"to": client.ppos.penaltyAddress, "data": data, "from": address})
    assert estimated_gas == estimated_slash_gas

    result = client.duplicatesign.reportDuplicateSign(1, report_information, report_address)
    assert_code(result, 0)
    balance_after = node.eth.getBalance(report_address)
    assert balance_after == proportion_reward
    released = client.ppos.getCandidateInfo(node.node_id)['Ret']['Released']
    assert released == economic.create_staking_limit - proportion_reward * 2


@pytest.mark.P1
def test_estimated_gas_008(client_new_node):
    """
       @describe: 锁仓预估gas，账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起举报成功
       @step:
       - 1. 创建账户，账户余额 = 锁仓金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起锁仓
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起锁仓成功
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    economic = client.economic

    address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit)
    lock_amount = node.web3.toWei(1000, 'ether')
    plan = [{'Epoch': 1, 'Amount': lock_amount}, {'Epoch': 2, 'Amount': lock_amount}]
    plan_list = []
    for dict_ in plan:
        v = [dict_[k] for k in dict_]
        plan_list.append(v)
    rlp_list = rlp.encode(plan_list)
    data = rlp.encode([rlp.encode(int(4000)), rlp.encode(bech32_address_bytes(address)), rlp_list])
    gas = get_the_dynamic_parameter_gas_fee(data) + 21000 + 18000 + 8000 + 21000 * 2
    estimated_gas = node.eth.estimateGas({"to": client.ppos.restrictingAddress, "data": data, "from": address})
    assert gas == estimated_gas
    gas_fees = gas * node.eth.gasPrice

    restricting_address, _ = economic.account.generate_account(node.web3, lock_amount * 2 + gas_fees)
    estimated_restricting_gas = node.eth.estimateGas(
        {"to": client.ppos.restrictingAddress, "data": data, "from": address})
    assert estimated_gas == estimated_restricting_gas
    result = client.restricting.createRestrictingPlan(restricting_address, plan, restricting_address)
    assert_code(result, 0)
    balance = node.eth.getBalance(restricting_address)
    assert balance == 0


@pytest.mark.P1
def test_estimated_gas_009(client_new_node):
    """
       @describe: 领取委托奖励预估gas，账户余额 = 交易金额 + gas * gasPrice, 可以预估成功，且发起领取委托奖励成功
       @step:
       - 1. 创建账户，账户余额 = 委托金额 + gas * gasPrice
       - 2. 预估gas
       - 3. 发起领取委托奖励
       @expect:
       - 1. 预估gas成功，且gas正确
       - 2. 发起领取委托奖励
       - 3. 账户扣款金额正确
     """
    client = client_new_node
    client.ppos.need_quota_gas = False
    node = client.node
    economic = client.economic
    delegate_gas, gas_fees_withdrew, address = estimated_delegate_withdrew_gas(client)
    result = client.staking.withdrew_staking(address)
    assert_code(result, 0)

    address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit)
    staking_address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit * 2)
    result = client.staking.create_staking(0, staking_address, staking_address, reward_per=1000)
    assert_code(result, 0)
    address, _ = economic.account.generate_account(node.web3, economic.create_staking_limit)
    result = client.delegate.delegate(0, address)
    assert_code(result, 0)

    data = rlp.encode([rlp.encode(int(5000))])
    gas = get_the_dynamic_parameter_gas_fee(data) + 8000 + 3000 + 21000 + 1 * 1000 + 0 * 100
    estimated_gas = node.eth.estimateGas({"to": address, "data": data, "from": node.ppos.delegateRewardAddress})
    gas_fees = gas * node.eth.gasPrice
    stakingnum = client.staking.get_stakingblocknum()
    result = client.delegate.withdrew_delegate(stakingnum, address)
    assert_code(result, 0)

    delegate_address, _ = economic.account.generate_account(node.web3,
                                                            economic.delegate_limit + delegate_gas + gas_fees)
    result = client.delegate.delegate(0, delegate_address)
    assert_code(result, 0)
    balance = node.eth.getBalance(delegate_address)
    assert balance == gas_fees
    data = rlp.encode([rlp.encode(int(5000))])
    estimated_withdrew_gas = node.eth.estimateGas(
        {"to": delegate_address, "data": data, "from": node.ppos.delegateRewardAddress})
    assert estimated_withdrew_gas == estimated_gas
    result = client.delegate.withdraw_delegate_reward(delegate_address)
    assert_code(result, 0)
    balance_after = node.eth.getBalance(delegate_address)
    assert balance_after == 0
