#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:globals
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description:
"""
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

from utils.exceptions import EnvNotFound, VariableNotFound
from config.cf_ini import ConfigIni, DefaultOption


# 时间字符串
dt = datetime.now()
DT_STR = dt.strftime("%Y-%m-%d %H:%M:%S")
TIME_STR = dt.strftime("%Y%m%d_%H%M%S")  # 时间字符串 -%f

# 项目BASE目录
BASE_DIR = Path(__file__).resolve().parent.parent if __file__.endswith('py') else os.getcwd()
global_cf_path = os.path.join(BASE_DIR, "config", "global_cf.ini")

# 日志、报告目录路径
LOG_DIR = os.path.join(BASE_DIR, "log", TIME_STR)

# STATIC目录路径
STATIC_DIR = os.path.join(BASE_DIR, "static")

# global_cf.ini 配置项
# 创建配置对象为全局变量
global_cf = ConfigIni(global_cf_path)
LOG_LEVEL = global_cf.get_str("DEFAULT", "log_level", vars=DefaultOption(global_cf.cf, "DEFAULT", log_level='INFO'))
LOG_ROTATION = global_cf.get_str("DEFAULT", "log_rotation", vars=DefaultOption(global_cf.cf, "DEFAULT", log_rotation='100 MB'))
LOG_RETENTION = global_cf.get_str("DEFAULT", "log_retention", vars=DefaultOption(global_cf.cf, "DEFAULT", log_retention='30 days'))

DB_INFO = {
    "engine": global_cf.get_str("DEFAULT", "db_engine", vars=DefaultOption(global_cf.cf, "DEFAULT", db_engine='django.db.backends.sqlite3')),
    "name": global_cf.get_str("DEFAULT", "db_name", vars=DefaultOption(global_cf.cf, "DEFAULT", db_name='db.sqlite3')),
}

# 设置全局 key/value
_global_dict = {}


def set_global_value(key, value):
    """
    设置全局变量
    :param key:
    :param value:
    :return:
    """
    global _global_dict
    # print(key, value)
    _global_dict[key] = value


def get_global_value(key):
    """
    获取全局变量中key对应的值
    :param key:
    :return:
    :exception: 如果没找到，raise VariableNotFound
    """
    try:
        global _global_dict
        return _global_dict[key]
    except KeyError:
        raise VariableNotFound(key)


def get_global_dict():
    """获取整个全局变量字典"""
    return _global_dict


# 设置环境变量
def set_os_environ(variables_mapping):
    """
    设置系统环境变量的key/value：os.environ
    :param variables_mapping:
    :return:
    """
    for variable in variables_mapping:
        os.environ[variable] = variables_mapping[variable]
        logger.debug(f"Set OS environment variable: {variable}")


def unset_os_environ(variables_mapping):
    """
    删除系统环境变量中的key/value：os.environ
    :param variables_mapping:
    :return:
    """
    for variable in variables_mapping:
        os.environ.pop(variable)
        logger.debug(f"Unset OS environment variable: {variable}")


def get_os_environment(variable_name):
    """
    获取系统环境变量值
    :param variable_name:
    :return:
    :exception: 如果没找到，raise EnvNotFound
    """
    try:
        return os.environ[variable_name]
    except KeyError:
        raise EnvNotFound(variable_name)


if __name__ == '__main__':
    pass
