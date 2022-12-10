#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:display
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description: 
"""
import datetime
from loguru import logger

from fio_perf.models import FIOSettings, DESCRIPTIONS


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


def calculate_duration(settings: FIOSettings):
    number_of_tests = len(settings.tests)
    time_per_test = settings.runtime
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_header(settings: FIOSettings):
    logger.log('DESC', '{0}参数信息{0}'.format('*' * 20))
    dict_settings = dict(settings)
    data = parse_settings_for_display(dict_settings)
    fl = 30  # Width of left column of text
    duration = calculate_duration(settings)
    if settings.dry_run:
        logger.warning(" ====---> WARNING - DRY RUN <---==== ")
    len_test = "TestCase Count"
    estimated = "Estimated duration"
    logger.log('DESC', f"{len_test:<{fl}}: {len(settings.tests):<}")
    logger.log('DESC', f"{estimated:<{fl}}: {duration:<}")

    for item in dict_settings.keys():
        if item not in settings.filter_items:
            description = DESCRIPTIONS[item]
            if item in data.keys():
                logger.log('DESC', f"{description:<{fl}}: {data[item]:<}")
            else:
                if dict_settings[item]:
                    logger.log('DESC', f"{description}:<{fl}: {dict_settings[item]:<}")
    logger.log('DESC', '{0}开始执行{0}'.format('*' * 20))


if __name__ == '__main__':
    pass
