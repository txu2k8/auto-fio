#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:log_init
@time:2022/09/15
@email:tao.xu2008@outlook.com
@description:
# 日志级别
Level	    value	Logger method
TRACE	    5	    logger.trace
DEBUG	    10	    logger.debug
INFO	    20	    logger.info
SUCCESS	    25	    logger.success
WARNING	    30	    logger.warning
ERROR	    40	    logger.error
CRITICAL	50	    logger.critical

info_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>"
"""
import os
import sys
import atexit
from loguru import logger

from config import TIME_STR, LOG_DIR, LOG_LEVEL, LOG_ROTATION, LOG_RETENTION

DEFAULT_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
                 "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
                 "- <level>{message}</level>"
SIMPLE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <level>{message}</level>"
OBJECT_FORMAT = "{message}"
TRACE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
                 "<cyan>P{process}</cyan>:<cyan>T{thread}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
                 "- <level>{message}</level>"


def init_logger(prefix='test', case_id=0, trace=False):
    """
    初始化logger日志配置
    :param prefix:
    :param case_id:测试用例ID，作为文件名的一部分
    :param trace: 是否打印trace信息
    :return:
    """
    # 获取配置
    loglevel = 'TRACE' if trace else LOG_LEVEL
    spec_format = TRACE_FORMAT if loglevel == 'TRACE' else SIMPLE_FORMAT

    # 删除默认
    logger.remove()

    # 新增级别
    logger.level('STAGE', no=21, color='<blue><bold>')  # INFO < STAGE < ERROR
    logger.level('RUN', no=22, color='<blue><bold>')  # INFO < MC < ERROR
    logger.level('DESC', no=52)  # CRITICAL < DESC，打印描述信息到所有日志文件

    # 初始化控制台配置
    logger.add(sys.stderr, level=loglevel, format=spec_format)

    # 日志文件名处理
    if case_id > 1:
        prefix += '_tc{}'.format(case_id)

    logger.info(LOG_DIR)
    # 初始化日志配置 -- all日志文件
    logger.add(
        os.path.join(LOG_DIR, '{}.log'.format(prefix)),
        rotation=LOG_ROTATION,  # '100 MB',
        retention=LOG_RETENTION,  # '30 days',
        enqueue=True,
        encoding="utf-8",
        level=loglevel,
        format=spec_format,
        backtrace=True,
        diagnose=True
    )

    atexit.register(logger.remove)


if __name__ == '__main__':
    pass
