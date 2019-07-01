# -*- coding: UTF-8 -*-
"""
@author: DouYuewei
@time: 2018/11/1 10:39
@usage:platon encode工具
"""
import re
from hexbytes import HexBytes


def encode_type(i: int):
    return encode_int('int64', i)


def encode_int(typ, i: int):
    """
    int类型encode
    :param typ: int类型：int64\int32\int16\int8 uint64\32\16\8
    :param i: int数字
    :return:bytearray
    """
    num = int(re.sub('\D', "", typ)) // 8
    return i.to_bytes(length=num, byteorder='big', signed=True)


def encode_string(abi_str: str):
    if isinstance(abi_str, str):
        return bytearray(abi_str, 'utf-8')
    else:
        raise Exception('please input a str')


def encode_boolean(boolean: bool):
    if isinstance(boolean, bool):
        return bytearray(boolean)
    else:
        raise Exception('please input a bool')


def dec2Bin(dec):
    result = ''

    if dec:
        result = dec2Bin(dec // 2)
        return result + str(dec % 2)
    else:
        return result


if __name__ == '__main__':
    x = encode_int('int64', 20)
    print(type(x), x)
