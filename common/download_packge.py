# -*- coding: UTF-8 -*-
"""
@author: DouYueWei
@time: 2018/12/26 10:21
@usage:
"""
import os
import shutil
import tarfile

import requests

from conf import setting as conf


def download_platon(download_url: 'str', path=conf.PLATON_DIR):
    """

    :param download_url: 新包下载地址
    :param path: platon相对路径
    :return:

    """
    packge_name = download_url.split('/')[-1][:-7]
    platon_path = os.path.abspath(path)
    platon_tar_path = os.path.join(platon_path, 'platon.tar.gz')
    extractall_path = os.path.join(platon_path,packge_name)
    # 下载tar.gz压缩包
    resp = requests.get(url=download_url, headers={
                        'Authorization': 'Basic cGxhdG9uOlBsYXRvbjEyMyE='})
    data = resp.content
    with open(platon_tar_path, 'wb') as f:
        f.write(data)
    f.close()

    # 解压
    tar = tarfile.open(platon_tar_path)
    tar.extractall(path=platon_path)
    tar.close()
    for filename in os.listdir(extractall_path):
        print(filename)
        if filename == "linux":
            shutil.copyfile(os.path.join(extractall_path, 'linux', 'platon'),conf.PLATON_BIN)
    else:
        shutil.copyfile(os.path.join(extractall_path, 'platon'),conf.PLATON_BIN)
    # 复制platon二进制文件
    # for filename in os.listdir(os.path.join(platon_path, packge_name)):
    #     print(filename)
    #     if filename == 'linux':
    #         with open(os.path.join(platon_path, packge_name, 'linux', 'platon'), 'rb') as read_file:
    #             platon_data = read_file.read()
    #         break
    # else:
    #     with open(os.path.join(platon_path, packge_name, 'platon'), 'rb') as read_file:
    #         platon_data = read_file.read()
    # with open(os.path.join(platon_path, 'platon'), 'wb') as write_file:
    #     write_file.write(platon_data)
    # read_file.close()
    # write_file.close()

    # 删除下载、解压文件
    os.remove(platon_tar_path)
    print(extractall_path)
    try:
        shutil.rmtree(extractall_path)
    except:
        rmtree(extractall_path)


def rmtree(top):
    import stat
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)
