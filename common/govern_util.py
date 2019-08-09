# -*- coding:utf-8 -*-

"""
@Author: 
@Date: block_interval19/8/1 14:46
@LastEditors: 
@LastEditTime: block_interval19/8/1 14:46
@Description:
"""
import random
import string
import time
import json
import os

from client_sdk_python import Web3
from common import log

# 查询块高的时间间隔-单位秒
time_interval=10

# 一个共识周期数包含的区块数
# block_count

# 截止块高在某个共识周期的第(block_count-block_interval)个块高
# block_interval

# 提案截止块高中，设置截止块高在第几个共识周期中
# conse_index

# 提案截止块高中，设置截止块高在最大的共识周期中
# conse_border


def get_privatekey(address, file=None):
    '''
    根据钱包地址从4000个账号文件中获取钱包私钥
    :param address:
    :param file:
    :return:
    '''
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = os.path.abspath(os.path.join(BASE_DIR, "deploy/privatekeyfile4000.txt"))
    with open(file,'r') as f:
        address_list = {}
        for i in f.readlines():
            i = i.strip('\n')
            i = i.split(',')
            address_list[i[0]] = i[1]
    if address_list.get(address):
        return address_list.get(address)
    else:
        return


def is_cur_block_number_big_than_end_block_number(rpc_link,end_number):
    '''
    判断当前块高是否大于截止块高
    :param rpc_link,end_number:
    :return:
    '''
    while 1:
        block_number = rpc_link.eth.blockNumber

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒，查询出当前块高数'.format(time_interval))
        time.sleep(time_interval)

        log.info('当前块高={}'.format(block_number))
        if block_number >= end_number:
            log.info('当前块高={}'.format(block_number))
            break


def get_single_valid_end_and_effect_block_number(rpc_link,block_count,block_interval,conse_index):
    '''
    获取构造单个合理的截止块高和生效块高
    :param rpc_link,block_count,block_interval,conse_index:
    :return: tuple
    '''
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))

    if block_number % block_count == 0:
        # 截止块高
        end_number = block_number + (conse_index * block_count) - block_interval

        # 生效块高
        effect_number = end_number + (conse_index + 5) * block_count + block_interval
    else:
        mod = block_number % block_count
        interval = block_count - mod
        # 截止块高
        end_number = block_number + interval + (conse_index * block_count) - block_interval

        # 生效块高
        effect_number = end_number + (conse_index + 5) * block_count + block_interval
    return end_number, effect_number


def get_all_invalid_end_block_number(rpc_link,block_count,block_interval,conse_index,conse_border):
    '''
    获取构造各类不合理的截止区块块高
    :param rpc_link,block_count,block_interval,conse_index,conse_border:
    :return: list
    '''
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))

    if block_number % block_count == 0:

        # 截止块高
        end_number = block_number + (conse_index * block_count) - block_interval

        # 生效块高
        effect_number = end_number + (conse_index + 5) * block_count + block_interval

        end_number_list = [
            #  (None, effect_number),
            # ('number', effect_number),
            # ('0.a.0', effect_number),
            (block_number, effect_number),
            (block_number + block_count * conse_index - (block_interval-1), effect_number),
            (block_number + block_count * conse_border - (block_interval+1), effect_number + block_count * conse_border),
            (block_number + block_count * (conse_border + 1) - block_interval, effect_number + block_count * (conse_border + 1))]
    else:
        mod = block_number % block_count
        interval = block_count - mod

        # 截止块高
        end_number = block_number + interval + (conse_index * block_count) - block_interval

        # 生效块高
        effect_number = end_number + (conse_index + 5) * block_count + block_interval

        end_number_list = [
            #  (None, effect_number),
            # ('number', effect_number),
            # ('0.a.0', effect_number),
            (block_number, effect_number),
            (block_number + interval + block_count * conse_index - (block_interval-1), effect_number),
            (block_number + interval + block_count * conse_border - (block_interval+1), effect_number + block_count * conse_border),
            (block_number + interval + block_count * (conse_border + 1) - block_interval, effect_number + block_count * (conse_border + 1))]
    return end_number_list


def get_all_invalid_effect_block_number(rpc_link,block_count,block_interval,conse_index):
    '''
    获取构造各类不合理的生效区块块高
    :param rpc_link,block_count,block_interval,conse_index:
    :return: list
    '''
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber

    log.info('当前块高={}'.format(block_number))
    
    if block_number % block_count == 0:
        # 截止块高
        end_number = block_number + (conse_index * block_count) - block_interval
        effect_number_list = [
                              #   (end_number, None),
                              # (end_number, 'number'),
                              # (end_number, '0.a.0'),
                              (end_number, block_number),
                              (end_number, end_number),
                              (end_number, end_number + (conse_index + 4) * block_count+block_interval),
                              (end_number, end_number + (conse_index + 5) * block_count - 1+block_interval),
                              (end_number, end_number + (conse_index + 5) * block_count + 1+block_interval),
                              (end_number, end_number + (conse_index + 10) * block_count+block_interval)]
    else:
        mod = block_number % block_count
        interval = block_count - mod
        log.info(interval)

        # 截止块高
        end_number = block_number + interval + (conse_index * block_count) - block_interval
        effect_number_list = [
                              #   (end_number, None),
                              # (end_number, 'number'),
                              # (end_number, '0.a.0'),
                              (end_number, block_number),
                              (end_number, end_number),
                              (end_number, end_number + (conse_index + 4) * block_count+block_interval),
                              (end_number, end_number + (conse_index + 5) * block_count - 1+block_interval),
                              (end_number, end_number + (conse_index + 5) * block_count + 1+block_interval),
                              (end_number, end_number + (conse_index + 10) * block_count+block_interval)]

    return effect_number_list


def get_all_legal_end_and_effect_block_number(rpc_link,block_count,block_interval,conse_index,conse_border):
    '''
    获取构造各类合理的截止区块、生效区块块高
    :param rpc_link,block_count,block_interval,conse_index,conse_border:
    :return: list
    '''
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))

    if block_number % block_count == 0:
        end_number_list = [(block_number + block_count * conse_index - block_interval,
                            block_number + block_count * conse_index + (conse_index + 5) * block_count),
                           (block_number + block_count * conse_index - block_interval,
                            block_number + block_count * conse_index + (conse_index + 8) * block_count),
                           (block_number + block_count * conse_border - block_interval,
                            block_number + block_count * conse_border + (conse_border + 10) * block_count)]
    else:
        mod = block_number % block_count
        interval = block_count - mod
        end_number_list = [(block_number + interval + block_count * conse_index - block_interval,
                            block_number + interval + block_count * conse_index + (conse_index + 5) * block_count),
                           (block_number + interval + block_count * conse_index - block_interval,
                            block_number + interval + block_count * conse_index + (conse_index + 8) * block_count),
                           (block_number + interval + block_count * conse_border - block_interval,
                            block_number + interval + block_count * conse_border + (conse_border + 10) * block_count)]
    return end_number_list


def get_all_legal_end_and_effect_block_number_for_vote(rpc_link,block_count,block_interval,conse_index,conse_border):
    '''
    获取构造各类合理的截止区块、生效区块块高
    :param rpc_link,block_count,block_interval,conse_index,conse_border:
    :return: list
    '''
    # 当前块高
    block_number = rpc_link.web3.eth.blockNumber
    log.info('当前块高={}'.format(block_number))

    if block_number % block_count == 0:
        end_number_list = [
            (block_number + block_count * conse_index - block_interval, block_number + block_count * conse_index + (conse_index + 5) * block_count),
            (block_number + block_count * (conse_border - 1) - block_interval,
             block_number + block_count * (conse_border - 1) + (conse_border - 1 + 5) * block_count),
            (block_number + block_count * conse_border - block_interval, block_number + block_count * conse_border + (conse_border + 5) * block_count)]
    else:
        mod = block_number % block_count
        interval = block_count - mod
        end_number_list = [(block_number + interval + block_count * conse_index - block_interval,
                            block_number + interval + block_count * conse_index + (conse_index + 5) * block_count),
                           (block_number + interval + block_count * (conse_border - 1) - block_interval,
                            block_number + interval + block_count * (conse_border - 1) + (conse_border - 1 + 5) * block_count),
                           (block_number + interval + block_count * conse_border - block_interval,
                            block_number + interval + block_count * conse_border + (conse_border + 5) * block_count)]
    return end_number_list


def get_current_settle_account_candidate_list(rpc_link):
    '''
    获取当前结算周期非验证人的候选人列表
    :return:
    '''
    revice1 = rpc_link.getCandidateList()
    revice2 = rpc_link.getVerifierList()

    node_info1 = revice1.get('Data')
    node_info2 = revice2.get('Data')

    candidate_list = []
    verifier_list = []

    for nodeid in node_info1:
        candidate_list.append(nodeid.get('NodeId'))

    for nodeid in node_info2:
        verifier_list.append(nodeid.get('NodeId'))

    candidate_no_verify_list = []
    for list1 in candidate_list:
        if list1 not in verifier_list:
            candidate_no_verify_list.append(list1)
    return candidate_no_verify_list


def get_stakingaddree(rpc_link,nodeid):
    '''
    根据节点id获取质押钱包地址
    :param rpc_link:
    :param nodeid:
    :return:
    '''
    result = rpc_link.getCandidateInfo(nodeid)
    candidateInfo = result.get('Data')

    address = candidateInfo.get('StakingAddress')
    return Web3.toChecksumAddress(address)


def waite_to_settle_account_cycle_block_number(rpc_link, block_count,end_block=None):
    '''
    等待指定快高，未指定则等待至本结算周期结束
    :param rpc_link:
    :param end_block:
    :return:
    '''

    # 共识周期块高数
    block_count = block_count

    # 当前块高
    current_block = rpc_link.eth.blockNumber

    if not end_block:
        wait_block = block_count - (current_block % block_count)
        end_block = current_block + wait_block

    while 1:
        current_block = rpc_link.eth.blockNumber
        if end_block < current_block:
            break
        log.info('等待一段时间={}秒，查询出当前块高数'.format(time_interval))
        time.sleep(time_interval)


def is_exist_ineffective_proposal_info(rpc_link):
    '''
    判断链上是否存在有效的升级提案-用于判断是否可以发起升级提案
    :param rpc_link:
    :return:
    '''
    log.info('is_exist_ineffective_proposal_info-开始')
    result = rpc_link.listProposal()

    proposal_info = result.get('Data')

    if not proposal_info:
        log.info('查询提案失败')
    else:
        log.info('查询提案成功')
        proposal_info = json.loads(proposal_info)
        if proposal_info is None:
            log.info('提案信息为空')
            return False
        else:
            log.info('有提案信息')

            proposal_list = []
            endvotingblock_list = []

            for p_list in proposal_info:
                proposal_list.append(p_list.get('ProposalID'))
                endvotingblock_list.append(p_list.get('EndVotingBlock'))

            log.info('提案信息为：{}'.format(proposal_info))
            flag=False

            #当前块高
            block_number = rpc_link.eth.blockNumber
            for i in range(0, len(proposal_list)):
                if endvotingblock_list[i] > block_number:
                    log.info('有可投票的升级提案')
                    flag = True
                    break
                else:
                    result = rpc_link.getTallyResult(proposal_list[i].strip())
                    data=result.get('Data')

                    if not data:
                        log.info('根据升级提案号，查询升级提案失败')
                        flag = False
                    else:
                        status_info = json.loads(data)
                        status = status_info.get('status')
                        log.info('判断提案信息的状态={}'.format(status))
                        if status == 4:
                            log.info('有预生效的升级提案')
                            flag = True
                            break
                        else:
                            flag=False
                            log.info('没有预生效的升级提案')
            return flag
    log.info('is_exist_ineffective_proposal_info-结束')


def is_exist_ineffective_proposal_info_for_vote(rpc_link):
    '''
    判断链上是否存在有效的升级提案-用于判断是否可以发起投票
    :param rpc_link:
    :return:
    '''
    log.info('is_exist_ineffective_proposal_info_for_vote-开始')

    result = rpc_link.listProposal()
    proposal_info = result.get('Data')

    if not proposal_info:
        log.info('查询提案失败')
    else:
        log.info('查询提案成功')
        proposal_info = json.loads(proposal_info)

        if proposal_info is None:
            log.info('提案信息为空')
            return False
        else:
            log.info('有提案信息')
            proposal_list = []
            endvotingblock_list = []

            for p_list in proposal_info:
                proposal_list.append(p_list.get('ProposalID'))
                endvotingblock_list.append(p_list.get('EndVotingBlock'))

            log.info('提案信息为：{}'.format(proposal_info))

            flag = False

            #当前块高
            block_number = rpc_link.eth.blockNumber
            for i in range(0, len(proposal_list)):
                if endvotingblock_list[i] > block_number:
                    log.info('有可投票的升级提案')
                    flag = True
                    break
                else:
                    flag=False
                    log.info('没有可投票的升级提案')
            return flag
    log.info('is_exist_ineffective_proposal_info_for_vote-结束')


def get_effect_proposal_id(rpc_link):
    '''
    获取链上有效的升级提案版本号（暂时只支持升级提案）
    :param rpc_link:
    :return:
    '''
    if not is_exist_ineffective_proposal_info(rpc_link):
        log.info('链上不存在有效的升级提案')
        return None
    else:
        result = rpc_link.listProposal()
        proposal_info = result.get('Data')
        proposal_info = json.loads(proposal_info)

        proposalid_list = []
        newversion_list = []
        endvotingblock_list = []

        for pid_list in proposal_info:
            proposalid_list.append(pid_list.get('ProposalID'))
            endvotingblock_list.append(pid_list.get('EndVotingBlock'))
            newversion_list.append(pid_list.get('NewVersion'))

        # 当前块高
        block_number = rpc_link.eth.blockNumber
        for i in range(0, len(proposalid_list)):
            if endvotingblock_list[i] > block_number:
                return proposalid_list[i]
            else:
                result = rpc_link.getTallyResult(proposalid_list[i].strip())
                if not result.get('Data'):
                    log.info('根据升级提案号，查询升级提案失败')
                else:
                    status_info = result.get('Data')
                    status_info = json.loads(status_info)
                    status = status_info.get('status')
                    if status == 4:
                        return proposalid_list[i]


def get_effect_proposal_info_for_vote(rpc_link):
    '''
    获取链上有效的升级提案版本号（暂时只支持升级提案）
    :param rpc_link:
    :return:
    '''
    if not is_exist_ineffective_proposal_info_for_vote(rpc_link):
        log.info('链上不存在可投票的升级提案')
        return None
    else:
        result = rpc_link.listProposal()
        proposal_info = result.get('Data')
        proposal_info = json.loads(proposal_info)

        proposalid_list = []
        newversion_list = []
        endvotingblock_list = []

        for pid_list in proposal_info:
            proposalid_list.append(pid_list.get('ProposalID'))
            newversion_list.append(pid_list.get('NewVersion'))
            endvotingblock_list.append(pid_list.get('EndVotingBlock'))

        # 当前块高
        block_number = rpc_link.eth.blockNumber
        for i in range(0, len(proposalid_list)):
            if endvotingblock_list[i] > block_number:
                return proposalid_list[i],newversion_list[i],endvotingblock_list[i]


def get_proposal_vote_end_block_number(rpc_link):
    '''
    获取提案的投票截止块高
    :param rpc_link:
    :return:
    '''
    result = rpc_link.listProposal()
    proposal_info = result.get('Data')

    if not is_exist_ineffective_proposal_info(rpc_link):
        log.info('链上不存在有效的升级提案')
    else:
        proposal_info = json.loads(proposal_info)
        end_block_list = []

        for e_list in proposal_info:
            end_block_list.append(e_list.get('EndVotingBlock'))
        end_block_list.sort()
        return end_block_list[-1]


def get_proposal_vote_effect_block_number(rpc_link):
    '''
    获取提案生效块高
    :param rpc_link:
    :return:
    '''
    result = rpc_link.listProposal()
    proposal_info = result.get('Data')

    if not is_exist_ineffective_proposal_info(rpc_link):
        log.info('链上不存在有效的升级提案')
    else:
        proposal_info = json.loads(proposal_info)
        effect_block_list = []

        for e_list in proposal_info:
            effect_block_list.append(e_list.get('ActiveBlock'))
        effect_block_list.sort()

        return effect_block_list[-1]


def get_effect_proposal_id_and_version(rpc_link):
    '''
    获取有效的升级提案的 ProposalID NewVersion（暂时只支持升级提案，所有获取到的是当前生效的升级提案 ProposalID NewVersion）
    :param rpc_link:
    :return:
    '''
    if not is_exist_ineffective_proposal_info(rpc_link):
        log.info('链上不存在有效的升级提案')
        return None
    else:
        result = rpc_link.listProposal()
        proposal_info = result.get('Data')
        proposal_info = json.loads(proposal_info)

        proposalid_list = []
        newversion_list = []
        endvotingblock_list =[]

        for pid_list in proposal_info:
            proposalid_list.append(pid_list.get('ProposalID'))
            endvotingblock_list.append(pid_list.get('EndVotingBlock'))
            newversion_list.append(pid_list.get('NewVersion'))

        #当前块高
        block_number = rpc_link.eth.blockNumber
        for i in range(0, len(proposalid_list)):
            if endvotingblock_list[i] > block_number:
                return proposalid_list[i], newversion_list[i]


def get_version(rpc_link,flag=None):
    '''
    获取版本号，不传入flag，为获取链上版本号，例：链上版本号为0.7.0
    flag = 1（获取小于链上主版号） 0.6.0
    flag = 2 (获取等于链上主版本号，小版本号不等于) 0.7.1
    flag = 3 (获取大于链上主版本号) 0.8.0
    :param flag:
    :return:
    '''

    msg = rpc_link.getActiveVersion()
    version = int(msg.get('Data'))

    # 返回链上版本号
    if flag is None:
        new_version = version
    elif flag == 1:
        ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
        ver0 = ver_byte[0]
        ver1 = ver_byte[1]
        ver2 = ver_byte[2]
        ver3 = ver_byte[3]
        new_ver3 = (ver2 - 1).to_bytes(length=1, byteorder='big', signed=False)
        new_version_byte = ver_byte[0:1] + new_ver3 + ver_byte[3:]
        new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
    elif flag == 2:
        ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
        ver0 = ver_byte[0]
        ver1 = ver_byte[1]
        ver2 = ver_byte[2]
        ver3 = ver_byte[3]
        new_ver3 = (ver3 + 1).to_bytes(length=1, byteorder='big', signed=False)
        new_version_byte = ver_byte[0:3] + new_ver3
        new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
    elif flag == 3:
        ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
        ver0 = ver_byte[0]
        ver1 = ver_byte[1]
        ver2 = ver_byte[2]
        ver3 = ver_byte[3]
        new_ver2 = (ver2 + 1).to_bytes(length=1, byteorder='big', signed=False)
        new_version_byte = ver_byte[0:1] + new_ver2 + ver_byte[3:]
        new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
    else:
        pass
    return new_version


def get_rate_of_voting(rpc_link, proposalid):
    '''
    计算升级提案投票率
    :param rpc_link:
    :param proposalid:
    :return:
    '''
    result = rpc_link.getTallyResult(proposalid)
    resultinfo = result.get('Data')
    resultinfo = json.loads(resultinfo)

    if not resultinfo:
        log.info('根据给定的提案id查询提案结果失败')
    else:
        yeas = resultinfo.get('yeas')
        accuVerifiers = resultinfo.get('accuVerifiers')
        return yeas/accuVerifiers


def get_accuVerifiers_of_proposal(rpc_link, proposalid):
    '''
    获取在整个投票期内有投票资格的验证人总数
    :param rpc_link:
    :param proposalid:
    :return:
    '''
    result = rpc_link.getTallyResult(proposalid)
    resultinfo = result.get('Data')
    resultinfo = json.loads(resultinfo)

    if not resultinfo:
        log.info('根据给定的提案id查询提案结果失败')
    else:
        accuVerifiers = resultinfo.get('accuVerifiers')
        return accuVerifiers


def get_yeas_of_proposal(rpc_link, proposalid):
    '''
    获取在整个投票期内有投票资格的验证人总数
    :param rpc_link:
    :param proposalid:
    :return:
    '''
    result = rpc_link.getTallyResult(proposalid)
    resultinfo = result.get('Data')
    resultinfo = json.loads(resultinfo)

    if not resultinfo:
        log.info('根据给定的提案id查询提案结果失败')
    else:
        yeas = resultinfo.get('yeas')
        return yeas


def get_current_verifier(rpc_link):
    '''
    获取当前结算周期验证人列表
    :param rpc_link:
    :return:
    '''
    result = rpc_link.getVerifierList()
    verifier_info = result.get('Data')

    verifier_list = []
    for list1 in verifier_info:
        verifier_list.append(list1.get('NodeId'))
    return verifier_list


def get_current_validator(rpc_link):
    '''
    获取当前共识轮验证人列表
    :param rpc_link:
    :return:
    '''
    result = rpc_link.getValidatorList()
    validator_info = result.get('Data')

    validator_list = []
    for list1 in validator_info:
        validator_list.append(list1.get('NodeId'))
    return validator_list


def gen_random_string(length):
    '''
    获取指定生成位数的随机数包含字母和数字
    :param length:
    :return: string
    '''
    len=length
    # 随机产生指定个数的字符
    num_of_numeric = random.randint(1, len - 1)

    # 剩下的都是字母
    num_of_letter = len - num_of_numeric

    # 随机生成数字
    numerics = [random.choice(string.digits) for i in range(num_of_numeric)]

    # 随机生成字母
    letters = [random.choice(string.ascii_letters) for i in range(num_of_letter)]

    # 结合两者
    all_chars = numerics + letters

    # 对序列随机排序
    random.shuffle(all_chars)

    # 生成最终字符串
    result = ''.join([i for i in all_chars]).lower()

    return result
