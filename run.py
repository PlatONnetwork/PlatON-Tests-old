import os
import sys
import time

import pytest

from common.abspath import abspath
from common.cmd import parse_options
from common.download_packge import download_platon
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton


def find_process():
    """
    检查linux机器是否有运行用例的进程
    :return:
        :bool
    """
    if sys.platform == "linux":
        pid = os.popen(
            "ps -ef|grep python|grep run_local.py|grep -v grep|awk {'print $2'}")
        if len(pid.readlines())>0:
            return True
    return False


def run(version=None, module=None, case=None):
    """
    运行用例集
    :param case: 任意用例集或单条用例
    :param version: 测试的版本，只能是all,pangu,ppos,pangu_all
    :param module: 测试的模块，只能是transaction，contract，ppos，blockchain，collusion,vc,如果有多个，用','分割
    :return:
    """
    case_dict = conf.CASE_DICT
    version_dict = conf.VERSION_DICT
    if version:
        case = version_dict[version]
    elif module:
        case = " ".join([case_dict[m] for m in module.split(",")])
    elif case:
        case = case
    else:
        raise Exception("请传入需要测试的用例、版本或模块")
    report = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
    excute_cases = r"-s -v --disable-warnings {} --alluredir={} --junitxml={}".format(
        case, abspath("./report/allure/{}".format(report)),abspath("./report/junitxml/{}.xml".format(report)))
    pytest.main(excute_cases)


def setup(node_yml=None, collusion_number=0):
    if node_yml:
        conf.NODE_YML = abspath(node_yml)
    auto = AutoDeployPlaton()
    auto.check_node_yml(conf.NODE_YML)
    conf.NODE_NUMBER = collusion_number
    auto.start_all_node(conf.NODE_YML)


def teardown():
    auto = AutoDeployPlaton()
    auto.kill_of_yaml(conf.NODE_YML)


if __name__ == "__main__":
    if find_process():
        raise Exception("当前机器正在执行测试，请稍后再试")
    opt = parse_options()
    node_yml = opt.node
    url = opt.url
    if url:
        download_platon(download_url=url)
    setup(node_yml, 0)
    version = opt.type
    module = opt.module
    case = opt.case
    run(version=version, module=module, case=case)
    teardown()
