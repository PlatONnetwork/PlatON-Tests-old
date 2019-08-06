# -*- coding:utf-8 -*-

"""
@Author: @Author
@Date: @Date @Eime
@LastEditors: @Author
@LastEditTime: @Date @Eime
@Description:
"""

from common import log


class OperateBlockNumber:
    def __init__(self,rpc_link,conse_size,index,border):
        self.rpc_link=rpc_link
        self.conse_size = conse_size
        self.index=index
        self.border=border

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
                               (block_number + self.conse_size * M - 20, block_number + self.conse_size * M+ (N + 10) * self.conse_size)]
        else:
            mod = block_number % self.conse_size
            interval = self.conse_size - mod
            end_number_list = [(block_number + interval + self.conse_size * N - 20, block_number + interval + self.conse_size * N+ (N + 5) * self.conse_size),
                               (block_number + interval + self.conse_size * N - 20, block_number + interval + self.conse_size * N+ (N + 8) * self.conse_size),
                               (block_number + interval + self.conse_size * M - 20, block_number + interval + self.conse_size * M+ (N + 10) * self.conse_size)]
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
