#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:get_data
@time:2022/12/3
@email:tao.xu2008@outlook.com
@description: 获取FIO测试结果数据
"""
from loguru import logger

from fio_report import json_parse


def get_json_data(settings):
    list_of_json_files = json_parse.list_json_files(settings)
    # logger.debug(list_of_json_files)
    dataset = json_parse.import_json_dataset(settings, list_of_json_files)
    parsed_data = json_parse.get_flat_json_mapping(settings, dataset)
    # logger.debug(parsed_data)
    return parsed_data


if __name__ == '__main__':
    pass
