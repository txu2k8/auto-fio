#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:__init__.py
@time:2022/09/15
@email:tao.xu2008@outlook.com
@description: 全局配置，及配置文件读写方法。
"""
from config.globals import *
from config.cf_yaml import *


__version__ = "1.0.1"

__all__ = [
    "__version__",
    # 基本方法
    "ConfigIni", "read_yaml",
    # 全局内存变量-读写
    "set_global_value", "get_global_value", "get_global_dict",
    # 环境变量-读写
    "set_os_environ", "unset_os_environ", "get_os_environment",
    # 全局常量
    "BASE_DIR", "LOG_DIR", "STATIC_DIR",  # 全局路径 dir
    "global_cf",
    "DB_INFO",  # 数据库配置
    "TIME_STR",  # 时间戳
    "LOG_LEVEL", "LOG_ROTATION", "LOG_RETENTION",  # 日志配置
]


if __name__ == '__main__':
    pass
