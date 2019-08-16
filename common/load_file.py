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

from conf import setting as conf


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

def get_node_list(node_yml):
    """
    根据节点配置文件，生成共识节点列表，非共识节点列表
    :param node:
    :return: collusion_list,nocollusion_list
    """
    data = LoadFile(node_yml).get_data()
    collusion_list = data.get("collusion", [])
    num = conf.NODE_NUMBER
    if num == 0:
        num = len(collusion_list)
    if num > len(collusion_list):
        raise Exception("测试节点数大于配置文件中的节点数")
    nocollusion_list = data.get("nocollusion", [])
    if not collusion_list and not nocollusion_list:
        raise Exception("配置文件格式错误")
    return collusion_list, nocollusion_list


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


def get_node_info(node_yml: str)->dict:
    """
    获取节点信息
    :param yaml:
    :return: data{}
        collusion:[rpc_list,enode_list,nodeid_list,ip_list,port_list],
        nocollusion:[rpc_list,enode_list,nodeid_list,ip_list,port_list]
    """
    data = {}
    collusion_list, nocollusion_list = get_node_list(node_yml)
    rpc_list, enode_list, nodeid_list, ip_list, port_list = [], [], [], [], []
    for nodedict in collusion_list:
        rpc_list.append(nodedict["url"])
        enode_list.append("enode://" + nodedict["id"] + "@" + nodedict[
            "host"] + ":" + str(nodedict.get("port", 16789)))
        nodeid_list.append(nodedict["id"])
        ip_list.append(nodedict["host"])
        port_list.append(str(nodedict.get("port", 16789)))
    data["collusion"] = [rpc_list, enode_list, nodeid_list, ip_list, port_list]
    rpc_list, enode_list, nodeid_list, ip_list, port_list = [], [], [], [], []
    for nodedict in nocollusion_list:
        rpc_list.append(nodedict["url"])
        enode_list.append("enode://" + nodedict["id"] + "@" + nodedict[
            "host"] + ":" + str(nodedict.get("port", 16789)))
        nodeid_list.append(nodedict["id"])
        ip_list.append(nodedict["host"])
        port_list.append(str(nodedict.get("port", 16789)))
    data["nocollusion"] = [rpc_list, enode_list, nodeid_list, ip_list, port_list]
    return data


if  __name__=='__main__':
    node_yml_path = conf.GOVERN_NODE_YML
    node_info = get_node_info(node_yml_path)

    # 共识节点信息
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get('collusion')

    # 非共识节点信息
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get('nocollusion')

    print(nodeid_list)