#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:display
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import datetime
from loguru import logger

from fio_perf.models import FIOParameters, DESCRIPTIONS, FIOParmFiles


def parse_settings_for_display(settings):
    data = {}
    max_length = 0
    action = {list: lambda a: " ".join(map(str, a)), str: str, int: str, bool: str}
    for k, v in settings.items():
        if k == 'descriptions':
            continue
        if v:
            data[str(k)] = action[type(v)](v)
            length = len(data[k])
            if length > max_length:
                max_length = length
    data["length"] = max_length
    return data


def calculate_duration(parameters: FIOParameters):
    number_of_tests = len(parameters.tests)
    time_per_test = parameters.runtime
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_header(parameters: FIOParameters):
    logger.log('DESC', '{0}参数信息{0}'.format('*' * 20))
    dict_settings = dict(parameters)
    data = parse_settings_for_display(dict_settings)
    fl = 30  # Width of left column of text
    duration = calculate_duration(parameters)
    if parameters.dry_run:
        logger.warning(" ====---> WARNING - DRY RUN <---==== ")
    len_test = "TestCase Count"
    estimated = "Estimated duration"
    logger.log('DESC', f"{len_test:<{fl}}: {len(parameters.tests):<}")
    logger.log('DESC', f"{estimated:<{fl}}: {duration:<}")

    for item in dict_settings.keys():
        if item not in parameters.filter_items:
            description = DESCRIPTIONS[item]
            if item in data.keys():
                logger.log('DESC', f"{description:<{fl}}: {data[item]:<}")
            else:
                if dict_settings[item]:
                    logger.log('DESC', f"{description}:<{fl}: {dict_settings[item]:<}")
    logger.log('DESC', '{0}开始执行{0}'.format('*' * 20))


def display_parmfile(parameters: FIOParmFiles):
    logger.log('DESC', '{0}参数信息{0}'.format('*' * 20))
    fl = 30  # Width of left column of text
    duration = 'NA'
    if parameters.estimated_duration:
        duration = str(datetime.timedelta(seconds=parameters.estimated_duration))
    if parameters.dry_run:
        logger.warning(" ====---> WARNING - DRY RUN <---==== ")
    client_desc = "Test Client"
    count_desc = "TestCase Count"
    client = parameters.client or "localhost"
    estimated_desc = "Estimated duration"
    logger.log('DESC', f"{client_desc:<{fl}}: {client:<}")
    logger.log('DESC', f"{count_desc:<{fl}}: {len(parameters.tests):<}")
    logger.log('DESC', f"{estimated_desc:<{fl}}: {duration:<}")

    for test in parameters.tests:
        desc = 'TestCase ParmFile'
        logger.log('DESC', f"{desc:<{fl}}: {test['path']:<}")
    logger.log('DESC', '{0}开始执行{0}'.format('*' * 20))


if __name__ == '__main__':
    pass
