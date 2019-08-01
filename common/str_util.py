# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-22 12:05
@LastEditors: huang
@LastEditTime: 2019-07-22 12:05
@Description:
"""

import random
import string


class StrUtil:
    def __init__(self,length):
        self.length=length

    def gen_random_string(self):
        '''
        指定生成位数的随机数包含字母和数字
        :param length:
        :return: string
        '''
        # 随机产生指定个数的字符
        num_of_numeric = random.randint(1,self.length-1)

        # 剩下的都是字母
        num_of_letter = self.length - num_of_numeric

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
