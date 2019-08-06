# -*- coding:utf-8 -*-

"""
@Author: 
@Date: 2019/8/1 14:46
@LastEditors: 
@LastEditTime: 2019/8/1 14:46
@Description:
"""
import random
import string
import math
import datetime
import time

from common import log
from utils.platon_lib.ppos import Ppos


def gen_random_string(length):
    '''
    指定生成位数的随机数包含字母和数字
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


class GovernUtil:

    # 时间间隔-秒
    time_interval=10

    def __init__(self,rpc_link,conse_size=None,index=None,border=None,flag=None,end_number=None,nodeid=None):
        self.rpc_link=rpc_link
        self.conse_size = conse_size
        self.index=index
        self.border=border
        self.flag = flag
        self.end_number = end_number
        self.nodeid = nodeid

    def get_version(self):
        '''
        获取版本号，不传入flag，为获取链上版本号，例：链上版本号为0.7.0
        flag = 1（获取小于链上主版号） 0.6.0
        flag = 2 (获取等于链上主版本号，小版本号不等于) 0.7.1
        flag = 3 (获取大于链上主版本号) 0.8.0
        :param flag:
        :return:
        '''

        msg = self.rpc_link.getActiveVersion()
        version = int(msg.get('Data'))

        # 返回链上版本号
        if self.flag is None:
            new_version = version
        elif self.flag == 1:
            ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
            ver0 = ver_byte[0]
            ver1 = ver_byte[1]
            ver2 = ver_byte[2]
            ver3 = ver_byte[3]
            new_ver3 = (ver2 - 1).to_bytes(length=1, byteorder='big', signed=False)
            new_version_byte = ver_byte[0:1] + new_ver3 + ver_byte[3:]
            new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
        elif self.flag == 2:
            ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
            ver0 = ver_byte[0]
            ver1 = ver_byte[1]
            ver2 = ver_byte[2]
            ver3 = ver_byte[3]
            new_ver3 = (ver3 + 1).to_bytes(length=1, byteorder='big', signed=False)
            new_version_byte = ver_byte[0:3] + new_ver3
            new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
        elif self.flag == 3:
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

    def get_candidate_no_verify(self):
        '''
        获取当前结算周期非验证人的候选人列表
        :return:
        '''
        revice1 = self.rpc_link.getCandidateList()
        revice2 = self.rpc_link.getVerifierList()

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

    def submitversion(self):
        pass

    # 判断当前块高是否大于截止块高
    def get_block_number(self):
        while 1:
            block_number = self.rpc_link.eth.blockNumber
            time.sleep(self.time_interval)
            log.info('当前块高={}'.format(block_number))
            if block_number >= self.end_number:
                log.info('当前块高={}'.format(block_number))
                break

    # 构造各类合理的截止区块-块高数
    def get_all_legal_end_and_effect_block_number(self):
        # 当前块高
        block_number = self.rpc_link.web3.eth.blockNumber
        log.info('当前块高={}'.format(block_number))
        # block_number=number

        # 设置截止块高 在第几个共识周期 N=index
        N = self.index

        # 共识周期个数的最大边界值
        M= self.border

        if block_number % self.conse_size == 0:
            end_number_list = [(block_number + self.conse_size * N - 20, block_number + self.conse_size * N+ (N + 5) * self.conse_size),
                               (block_number + self.conse_size * N - 20, block_number + self.conse_size * N+ (N + 8) * self.conse_size),
                               (block_number + self.conse_size * M - 20, block_number + self.conse_size * M+ (M + 10) * self.conse_size)]
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod
            end_number_list = [(block_number + interval + self.conse_size * N - 20, block_number + interval + self.conse_size * N+ (N + 5) * self.conse_size),
                               (block_number + interval + self.conse_size * N - 20, block_number + interval + self.conse_size * N+ (N + 8) * self.conse_size),
                               (block_number + interval + self.conse_size * M - 20, block_number + interval + self.conse_size * M+ (M + 10) * self.conse_size)]
        return end_number_list

    # 构造单个合理的截止块高和生效块高-块高数
    def get_invalid_end_and_effect_block_number(self):
        # 当前块高
        block_number = self.rpc_link.web3.eth.blockNumber
        log.info('当前块高={}'.format(block_number))

        # 设置截止块高 在第几个共识周期 N=index
        N = self.index

        if block_number % self.conse_size == 0:
            # 截止块高
            end_number = block_number + (N * self.conse_size) - 20

            # 生效块高
            effect_number = end_number + (N + 5) * self.conse_size
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod
            # 截止块高
            end_number = block_number + interval + (N * self.conse_size) - 20

            # 生效块高
            effect_number = end_number + (N + 5) * self.conse_size
        return end_number, effect_number

    # 构造各类不合理的截止区块-块高数
    def get_all_invalid_end_block_number(self):
        # 当前块高
        block_number = self.rpc_link.web3.eth.blockNumber
        log.info('当前块高={}'.format(block_number))
        # block_number=number

        # 设置截止块高 在第几个共识周期 N=index
        N = self.index

        # 共识周期个数的最大边界值
        M= self.border

        if block_number % self.conse_size == 0:

            # 截止块高
            end_number = block_number + (N * self.conse_size) - 20

            # 生效块高
            effect_number = end_number + (N + 5) * self.conse_size

            end_number_list = [(None, effect_number),
                               ('number', effect_number),
                               ('0.a.0', effect_number),
                               (block_number, effect_number),
                               (block_number + self.conse_size * N - 19, effect_number),
                               (block_number + self.conse_size * M - 21, effect_number + self.conse_size * M),
                               (block_number + self.conse_size * (M + 1) - 20, effect_number + self.conse_size * (M + 1))]
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod

            # 截止块高
            end_number = block_number + interval + (N * self.conse_size) - 20

            # 生效块高
            effect_number = end_number + (N + 5) * self.conse_size

            end_number_list = [(None, effect_number),
                               ('number', effect_number),
                               ('0.a.0', effect_number),
                               (block_number, effect_number),
                               (block_number + interval + self.conse_size * N - 19, effect_number),
                               (block_number + interval + self.conse_size * M - 21, effect_number + self.conse_size * M),
                               (block_number + interval + self.conse_size * (M + 1) - 20, effect_number + self.conse_size * (M + 1))]
        return end_number_list

    # 构造各类不合理的生效区块-块高数
    def get_all_invalid_effect_block_number(self):
        # 当前块高
        block_number = self.rpc_link.web3.eth.blockNumber
        log.info('当前块高={}'.format(block_number))
        # block_number=number

        # 设置截止块高 在第几个共识周期 N=index
        N = self.index

        if block_number % self.conse_size == 0:
            # 截止块高
            end_number = block_number + (N * self.conse_size) - 20
            effect_number_list = [(end_number, None),
                                  (end_number, 'number'),
                                  (end_number, '0.a.0'),
                                  (end_number, block_number),
                                  (end_number, end_number),
                                  (end_number, end_number + (N + 4) * self.conse_size),
                                  (end_number, end_number + (N + 5) * self.conse_size - 1),
                                  (end_number, end_number + (N + 5) * self.conse_size + 1),
                                  (end_number, end_number + (N + 11) * self.conse_size)]
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod

            # 截止块高
            end_number = block_number + interval + (N * self.conse_size) - 20
            effect_number_list = [(end_number, None),
                                  (end_number, 'number'),
                                  (end_number, '0.a.0'),
                                  (end_number, block_number),
                                  (end_number, end_number),
                                  (end_number, end_number + (N + 4) * self.conse_size),
                                  (end_number, end_number + (N + 5) * self.conse_size - 1),
                                  (end_number, end_number + (N + 5) * self.conse_size + 1),
                                  (end_number, end_number + (N + 11) * self.conse_size)]

        return effect_number_list

    # 构造各类合理的截止区块-块高数
    def get_all_legal_end_and_effect_block_number_for_vote(self):
        # 当前块高
        block_number = self.rpc_link.web3.eth.blockNumber
        log.info('当前块高={}'.format(block_number))

        # 设置截止块高 在第几个共识周期 N=index
        N = self.index

        # 共识周期个数的最大边界值
        M= self.border

        if block_number % self.conse_size == 0:
            end_number_list = [(block_number + self.conse_size * N - 20, block_number + self.conse_size * N+ (N + 5) * self.conse_size),
                               (block_number + self.conse_size * (M-1) - 20, block_number + self.conse_size * (M-1)+ (M-1 + 5) * self.conse_size),
                               (block_number + self.conse_size * M - 20, block_number + self.conse_size * M+ (M + 5) * self.conse_size)]
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod
            end_number_list = [(block_number + interval +self.conse_size * N - 20,block_number + interval +self.conse_size * N + (N + 5) * self.conse_size),
                               (block_number + interval +self.conse_size * (M - 1) - 20,block_number + interval +self.conse_size * (M - 1) + (M - 1 + 5) * self.conse_size),
                               (block_number + interval +self.conse_size * M - 20,block_number + interval +self.conse_size * M + (M + 5) * self.conse_size)]
        return end_number_list

# if  __name__=='__main__':
#     rpc_url='http://192.168.120.121:6789'
#
#     # address='0xdB245C0ebbCa84395c98c3b2607863cA36ABBD79'
#     # private_key='b735b2d48e5f6e1dc897081f8655fdbb376ece5b2b648c55eee72c38102a0357'
#
#     link_1 = Ppos(rpc_url, Web3.toChecksumAddress('0x493301712671Ada506ba6Ca7891F436D29185821'))
#         # ,
#         #           chainid=101,privatekey='0xa11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7')
#
#     # 当前版本号
#     version = OperateVersion(link_1,flag=None)
#
#     cur_version = version.get_version()
#
#     print('cur_version={}'.format(cur_version))