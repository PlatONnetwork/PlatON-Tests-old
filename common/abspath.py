import os

from conf.setting_merge import BASE_DIR


def abspath(path):
    """
    基于项目目录base_code/拼接路径，请传入基于base_code/的相对路径,
    path格式是相对路径./path or path/path2时才会拼接,path格式为绝对路径/path时，直接返回原路径
    :param base_path:
    :param path:
    :return:
    """
    if os.path.isabs(path):
        return path
    path = path.lstrip("./")
    return os.path.abspath(BASE_DIR + "/" + path)
