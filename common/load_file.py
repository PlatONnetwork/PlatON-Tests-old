'''
@Author: xiaoming
@Date: 2018-12-01 11:42:43
@LastEditors: xiaoming
@LastEditTime: 2018-12-05 14:16:00
@Description: 用于读取yml或json文件中的内容
'''

import json
import os

import yaml


class LoadFile(object):
    '''
    把json或者yaml文件转为python字典或者列表字典
    @file:文件的绝对路径
    '''

    def __init__(self, file):
        if file.split('.')[-1] != 'yaml' and file.split('.')[-1] != 'json' and file.split('.')[-1] != 'yml':
            raise Exception("文件格式必须是yaml或者json")
        self.file = file

    def get_data(self):
        '''
        传入任意yaml或json格式的文件，调用该方法获取结果
        '''
        if self.file.split('.')[-1] == "json":
            return self.load_json()
        return self.load_yaml()

    def load_json(self):
        '''
        Convert json file to dictionary
        '''
        try:
            with open(self.file, encoding="utf-8") as f:
                result = json.load(f)
                if isinstance(result, list):
                    result = [i for i in result if i != '']
                return result
        except FileNotFoundError as e:
            raise e

    def load_yaml(self):
        '''
        Convert yaml file to dictionary
        '''
        try:
            with open(self.file, encoding="utf-8")as f:
                result = yaml.load(f)
                if isinstance(result, list):
                    result = [i for i in result if i != '']
                return result
        except FileNotFoundError as e:
            raise e



def get_all_file(path):
    '''
    Get all yaml or json files
        @path: folder path
    '''
    try:
        result = [os.path.abspath(os.path.join(path, filename)) for filename in os.listdir(
            path) if filename.endswith(".json") or filename.endswith(".yml") or filename.endswith(".yaml")]
        return result
    except FileNotFoundError as e:
        raise e


def get_file(path):
    '''
    Get all yaml or json files
        @path: folder path
    '''
    try:
        result = []
        for x, _, _ in os.walk(path):
            if os.listdir(x):
                result += get_all_file(x)
            else:
                result += x
        return result
    except FileNotFoundError as e:
        raise e



def get_f(collsion_list):
    """
    获取最大作弊节点数量
    :param collsion_list:
    :return:
    """
    num = len(collsion_list)
    if num < 3:
        raise Exception("共识节点数少于3")
    if num == 3:
        return 0
    f = (num-1)/3
    return int(f)


def get_f_for_n(n):
    """
    根据共识节点总数，获取最大作弊节点数量
    :param collsion_list:
    :return:
    """
    num =  n
    if num < 3:
        raise Exception("共识节点数少于3")
    if num == 3:
        return 0
    f = (num-1)/3
    return int(f)
