'''
@Author: xiaoming
@Date: 2018-12-29 11:28:34
@LastEditors: xiaoming
@LastEditTime: 2019-01-02 10:24:10
@Description: 测试过程日志
'''
import logging
import os
import time
from logging import handlers

from conftest import BASE_DIR


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', fmt="[%(asctime)s]-%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"):
        self.logger = logging.getLogger(filename)
        log_format = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(log_format)
        file = handlers.WatchedFileHandler(filename, encoding='UTF-8')
        file.setFormatter(log_format)
        self.logger.addHandler(sh)
        self.logger.addHandler(file)


def setup_logger(logfile, loglevel):
    log = Logger(logfile, level=loglevel)
    return log


if not os.path.exists('{}/log'.format(BASE_DIR)):
    os.makedirs('{}/log'.format(BASE_DIR))
log = setup_logger('{}/log/{}.log'.format(BASE_DIR, str(
    time.strftime("%Y-%m-%d", time.localtime()))), 'info').logger




