#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:display
@time:2022/12/1
@email:tao.xu2008@outlook.com
@description: 
"""
import datetime

from fio_perf.models import FIOSettings


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
    number_of_tests = len(settings.tests) * settings.loops
    time_per_test = settings.runtime
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_header(settings: FIOSettings):
    dict_settings = dict(settings)
    header = "+++ Fio Benchmark Script +++"
    blockchar = "\u2588"
    data = parse_settings_for_display(dict_settings)
    fl = 30  # Width of left column of text
    length = data["length"]
    width = length + fl - len(header)
    duration = calculate_duration(settings)
    print(f"{blockchar}" * (fl + width))
    print((" " * int(width / 2)) + header)
    print()
    if settings.dry_run:
        print()
        print(" ====---> WARNING - DRY RUN <---==== ")
        print()
    estimated = "Estimated duration"
    print(f"{estimated:<{fl}}: {duration:<}")

    for item in dict_settings.keys():
        if item not in settings.filter_items:
            description = settings.descriptions[item]
            if item in data.keys():
                print(f"{description:<{fl}}: {data[item]:<}")
            else:
                if dict_settings[item]:
                    print(f"{description}:<{fl}: {dict_settings[item]:<}")
    print()
    print(f"{blockchar}" * (fl + width))


if __name__ == '__main__':
    pass
