#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 日志处理的封装
from datetime import datetime
import os
# o_path = os.getcwd()
# sys.path.append(o_path)
import logging
from common.path import log_path



def get_logger(name='root',
               logger_level='DEBUG',
               stream_handler_level='DEBUG',
               file=False,
               file_handler_level='INFO',
               off=True,
               fmt_str="[%(asctime)s]-[%(filename)s %(lineno)s]-[%(levelname)s]:[%(name)s]:%(message)s"
               ):
    """logger封装"""

    # 获取日志收集器 logger
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)
    # "time:%(asctime)s--%(levelname)s:%(name)s:%(message)s--%(filename)s---%(lineno)s"
    fmt = logging.Formatter(fmt_str)
    # 日志处理器
    handler = logging.StreamHandler()
    handler.setLevel(stream_handler_level)
    logger.addHandler(handler)
    handler.setFormatter(fmt)
    logger.removeHandler(handler)
    # 日志文件处理
    if file:
        current_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        file_name = f'{current_time}.log'
        file_path = os.path.join(log_path, file_name)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(file_handler_level)
        logger.addHandler(file_handler)
        file_handler.setFormatter(fmt)
    return logger


# current_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
# file_name = f'{current_time}.log'
# file_path = os.path.join(log_path, file_name)
# #
# logger = get_logger('chenqg',file=file_path)
#
# if __name__ == '__main__':
#     log = get_logger('chenqg')
#     logger.info("这里有一个bug")
#     logger.warning('这里有一个警告信息')
#     logger.error('这里有一个错误')



