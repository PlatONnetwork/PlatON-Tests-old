import pytest

from common import log
from common.abspath import abspath
from common.cmd import parse_options
from common.download_packge import download_platon
from conf import setting as conf
from deploy.deploy import AutoDeployPlaton


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
    excute_cases = r"-s -v --disable-warnings {}".format(case)
    pytest.main(excute_cases)
    while True:
        try:
            pytest.main(excute_cases)
        except Exception as e:
            log.error(e)
            continue


def setup(node_yml=None):
    if node_yml:
        conf.NODE_YML = abspath(node_yml)
    auto = AutoDeployPlaton(is_metrics=True)
    # auto.check_node_yml(conf.NODE_YML)
    # auto.booms(conf.NODE_YML)
    # auto.deploy_default_yml(conf.NODE_YML)
    auto.kill_of_yaml(conf.NODE_YML)
    # auto.start_all_node(conf.NODE_YML)


def teardown():
    auto = AutoDeployPlaton()
    auto.kill_of_yaml(conf.NODE_YML)


if __name__ == "__main__":
    opt = parse_options()
    node_yml = opt.node
    node_yml = "./deploy/node/25_cbft.yml"
    # node_yml = "./deploy/node/travis_node.yml"
    url = opt.url
    # url = "http://192.168.18.31:8085/ci/packages/PlatON_Go/318/PlatON_Go_linux_[ppos_optimize]_b318.04172003.tar.gz"
    if url:
        download_platon(download_url=url)
    setup(node_yml)
    version = opt.type
    module = opt.module
    module = "transaction"
    case = opt.case
    run(version=version, module=module, case=case)
    # teardown()
