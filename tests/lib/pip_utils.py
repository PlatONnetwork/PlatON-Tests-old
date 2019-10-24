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

from client_sdk_python import Web3
from common import log, connect
from common.load_file import LoadFile
from common.log import log
from hexbytes import HexBytes
from environment.node import Node


def upload_platon(node: Node, platon_bin):
    node.run_ssh("rm -rf {}".format(node.remote_bin_file))
    node.upload_file(platon_bin, node.remote_bin_file)
    node.run_ssh("chmod +x {}".format(node.remote_bin_file))



def is_exist_effective_proposal(node, proposaltype=2):
    '''
    判断链上是否存在有效的升级提案-用于判断是否可以发起升级提案
    :param node:
    :param proposaltype 1为升级提案 2、文本提案 4、取消提案
    :return:
    '''
    log.info('is_exist_effective_proposal_info-开始')
    result = node.pip.listProposal()
    proposal_info = result.get('Data')
    flag = False
    if not proposal_info:
        log.info('查询提案失败')
        log.info('is_exist_effective_proposal-结束')
    else:
        log.info('查询提案成功')
        proposal_info = json.loads(proposal_info)
        if proposal_info is None:
            log.info('提案信息为空')
            log.info('is_exist_effective_proposal-结束')
            flag = True
        else:
            proposal_list1 = []
            endvotingblock_list1 = []
            proposal_list2 = []
            endvotingblock_list2 = []
            proposal_list4 = []
            endvotingblock_list4 = []

            for p_list in proposal_info:
                if p_list.get('ProposalType') == 1:

                    proposal_list1.append(p_list.get('ProposalID'))
                    endvotingblock_list1.append(p_list.get('EndVotingBlock'))

                elif p_list.get('ProposalType') == 2:
                    proposal_list2.append(p_list.get('ProposalID'))
                    endvotingblock_list2.append(p_list.get('EndVotingBlock'))

                elif p_list.get('ProposalType') == 4:
                    proposal_list4.append(p_list.get('ProposalID'))
                    endvotingblock_list4.append(p_list.get('EndVotingBlock'))

            log.info('提案信息为：{}'.format(proposal_info))
            flag = False
            # 当前块高
            block_number = node.eth.blockNumber

            if proposaltype == 2:
                for i in range(0, len(proposal_list2)):
                    if endvotingblock_list2[i] > block_number:
                        log.info('存在投票期的升级提案')
                        flag = True
                        break
                    else:
                        result = node.pip.getTallyResult(proposal_list2[i].strip())
                        data = result.get('Data')
                        if not data:
                            log.info('根据升级提案号，查询升级提案失败')
                            flag = False
                        else:
                            status_info = json.loads(data)
                            status = status_info.get('status')
                            if status == 4:
                                log.info('有预生效的升级提案')
                                flag = True
                                break

            elif proposaltype == 1:
                for i in range(0, len(proposal_list1)):
                    if endvotingblock_list1[i] > block_number:
                        log.info('存在投票期的文本提案')
                        flag = True
                        break

            elif proposaltype == 4:
                for i in range(0, len(proposal_list4)):
                    if endvotingblock_list4[i] > block_number:
                        log.info('存在投票期的取消提案')
                        flag = True
                        break
            else:
                log.info('传入proposalType有误')
                return

    return flag


def is_exist_effective_proposal_for_vote(node, proposaltype=2):
    '''
    判断链上是否存在有效的升级提案-用于判断是否可以发起投票
    :param proposaltype:
    :param node:
    :return:
    '''
    log.info('is_exist_effective_proposal_for_vote-开始')
    result = node.pip.listProposal()
    proposal_info = result.get('Data')
    if not proposal_info:
        log.info('查询提案信息失败')
        log.info('is_exist_effective_proposal_for_vote-结束')
    else:
        log.info('查询提案信息成功')
        proposal_info = json.loads(proposal_info)

        if proposal_info is None:
            log.info('提案信息为空')
            log.info('is_exist_effective_proposal_for_vote-结束')
            return False
        else:
            proposal_list1 = []
            endvotingblock_list1 = []
            proposal_list2 = []
            endvotingblock_list2 = []
            proposal_list4 = []
            endvotingblock_list4 = []

            for p_list in proposal_info:
                if p_list.get('ProposalType') == 1:
                    proposal_list1.append(p_list.get('ProposalID'))
                    endvotingblock_list1.append(p_list.get('EndVotingBlock'))

                elif p_list.get('ProposalType') == 2:
                    proposal_list2.append(p_list.get('ProposalID'))
                    endvotingblock_list2.append(p_list.get('EndVotingBlock'))

                elif p_list.get('ProposalType') == 4:
                    proposal_list4.append(p_list.get('ProposalID'))
                    endvotingblock_list4.append(p_list.get('EndVotingBlock'))

            log.info('提案信息为：{}'.format(proposal_info))

            flag = False

            # 当前块高
            block_number = node.eth.blockNumber
            if proposaltype == 1:
                for i in range(0, len(proposal_list1)):
                    if endvotingblock_list1[i] > block_number:
                        log.info('存在处于投票期的文本提案')
                        flag = True
                        break
            elif proposaltype == 2:
                for i in range(0, len(proposal_list2)):
                    if endvotingblock_list2[i] > block_number:
                        log.info('存在处于投票期的升级提案')
                        flag = True
                        break

            elif proposaltype == 4:
                for i in range(0, len(proposal_list4)):
                    if endvotingblock_list4[i] > block_number:
                        log.info('存在处于投票期的取消提案')
                        flag = True
                        break
            else:
                log.info('传入proposaltype{}有误'.format(proposaltype))
            return flag


def get_effect_proposal_info_for_vote(node, proposaltype=2):
    '''
    获取链上处于投票期的提案信息
    :param proposaltype:
    :param node:
    :return:
    '''

    if not is_exist_effective_proposal_for_vote(node, 1) and proposaltype == 1:
        log.info('链上不存在处于投票期的文本提案')
        return None

    if not is_exist_effective_proposal_for_vote(node, 2) and proposaltype == 2:
        log.info('链上不存在处于投票期的升级提案')
        return None

    if not is_exist_effective_proposal_for_vote(node, 4) and proposaltype == 4:
        log.info('链上不存在处于投票期的取消提案')
        return None

    result = node.pip.listProposal()
    proposal_info = result.get('Data')
    proposal_info = json.loads(proposal_info)

    proposalid_list1 = []
    endvotingblock_list1 = []
    submitblock_list1 = []

    proposalid_list2 = []
    newversion_list2 = []
    endvotingblock_list2 = []
    activeblock_list2 = []
    submitblock_list2 = []

    proposalid_list4 = []
    endvotingblock_list4 = []
    submitblock_list4 = []

    for pid_list in proposal_info:
        if pid_list.get('ProposalType') == 1:
            proposalid_list1.append(pid_list.get('ProposalID'))
            endvotingblock_list1.append(pid_list.get('EndVotingBlock'))
            submitblock_list1.append(pid_list.get('SubmitBlock'))

        elif pid_list.get('ProposalType') == 2:
            proposalid_list2.append(pid_list.get('ProposalID'))
            newversion_list2.append(pid_list.get('NewVersion'))
            endvotingblock_list2.append(pid_list.get('EndVotingBlock'))
            activeblock_list2.append(pid_list.get('ActiveBlock'))
            submitblock_list2.append(pid_list.get('SubmitBlock'))

        elif pid_list.get('ProposalType') == 4:
            proposalid_list4.append(pid_list.get('ProposalID'))
            endvotingblock_list4.append(pid_list.get('EndVotingBlock'))
            submitblock_list4.append(pid_list.get('SubmitBlock'))

        else:
            log.info('传入proposaltype有误')

        # 当前块高
        block_number = node.eth.blockNumber
        if proposaltype == 1:
            for i in range(0, len(proposalid_list1)):
                if endvotingblock_list1[i] > block_number:
                    log.info('链上存在可投票的文本提案')
                    return proposalid_list1[i], endvotingblock_list1[i], submitblock_list1[i]

        elif proposaltype == 2:
            for i in range(0, len(proposalid_list2)):
                if endvotingblock_list2[i] > block_number:
                    log.info('链上存在可投票的升级提案')
                    return proposalid_list2[i], newversion_list2[i], endvotingblock_list2[i], activeblock_list2[i], submitblock_list2[i]

        elif proposaltype == 4:
            for i in range(0, len(proposalid_list4)):
                if endvotingblock_list4[i] > block_number:
                    log.info('链上存在可投票的取消提案')
                    return proposalid_list4[i], endvotingblock_list4[i], submitblock_list4[i]


def get_effect_proposal_info_of_preactive(node):
    '''
    获取链上处于预生效的提案信息
    :param node:
    :return:
    '''

    result = node.pip.listProposal()
    proposal_info = result.get('Data')
    proposal_info = json.loads(proposal_info)
    print(proposal_info)
    for pid_list in proposal_info:
        if pid_list.get('ProposalType') == 2:
            if get_status_of_proposal(node, pid_list.get('ProposalID')) == 4:
                return pid_list.get('ProposalID'), pid_list.get('NewVersion'), pid_list.get('ActiveBlock')
    raise Exception('不存在预生效升级提案')


def get_version(node, version=None):
    '''
    获取版本号，不传入flag，为获取链上版本号，例：链上版本号为X.Y.Z
    flag = 1   X.Y-1.Z
    flag = 2   X.Y.Z-1(Z需要大于0)
    flag = 3   X.Y.Z+1
    flag = 4   X.Y+1.Z-1 (Z需要大于0)
    flag = 5   X.Y+1.Z
    flag = 6   X.Y+1.9
    flag = 7   X.9.9
    flag = 8   9.Y.Z
    flag = 0   8.Y.Z
    :param flag:
    :return:
    '''

    if not version:
        msg = node.pip.getActiveVersion()
        version = int(msg.get('Data'))
    version = 1793
    ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
    ver0 = ver_byte[0]
    ver1 = ver_byte[1]
    ver2 = ver_byte[2]
    ver3 = ver_byte[3]

    # 返回链上版本号

    new_version0 = version

    new_ver3 = (ver2 - 1).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = ver_byte[0:1] + new_ver3 + ver_byte[3:]
    new_version1 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    if ver3:
        new_ver3 = (ver3 - 1).to_bytes(length=1, byteorder='big', signed=False)
        new_version_byte = ver_byte[0:3] + new_ver3
        new_version2 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver3 = (9).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = ver_byte[0:3] + new_ver3
    new_version3 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    if ver3:
        new_ver2 = (ver2 + 1).to_bytes(length=1, byteorder='big', signed=False)
        new_ver3 = (ver3 - 1).to_bytes(length=1, byteorder='big', signed=False)
        new_version_byte = ver_byte[0:1] + new_ver2 + new_ver3
        new_version4 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver2 = (ver2 + 1).to_bytes(length=1, byteorder='big', signed=False)
    new_ver3 = (1).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = ver_byte[0:1] + new_ver2 + new_ver3
    new_version5 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver2 = (ver2 + 1).to_bytes(length=1, byteorder='big', signed=False)
    new_ver3 = (9).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = ver_byte[0:1] + new_ver2 + new_ver3
    new_version6 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver2 = (9).to_bytes(length=1, byteorder='big', signed=False)
    new_ver3 = (0).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = ver_byte[0:1] + new_ver2 + new_ver3
    new_version7 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver1 = (9).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = new_ver1 + ver_byte[2:3] + ver_byte[3:]
    new_version8 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    new_ver1 = (8).to_bytes(length=1, byteorder='big', signed=False)
    new_version_byte = new_ver1 + ver_byte[2:3] + ver_byte[3:]
    new_version9 = int.from_bytes(new_version_byte, byteorder='big', signed=False)

    if ver3 == 0:
        version_list = [new_version0, new_version1, 0, new_version3, 0, new_version5, new_version6, new_version7,
                        new_version8, new_version9]

    else:
        version_list = [new_version0, new_version1, new_version2, new_version3, new_version4, new_version5,
                        new_version6, new_version7, new_version8, new_version9]

    return version_list





