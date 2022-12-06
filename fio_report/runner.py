#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner
@time:2022/12/3
@email:tao.xu2008@outlook.com
@description: 
"""
import json
from loguru import logger

from fio_report.output_json_parse import FIOJsonParse
from fio_report.report_xlsx import ReportXlsx


class FIOReportRunner(object):
    """FIO测试结果收集，报告生成"""
    def __init__(self, data_path, *args, **kwargs):
        self.data_path = data_path

    def run(self):
        json_data = FIOJsonParse(self.data_path).get_json_data()
        with open("./sss.json", "w+") as f:
            f.write(json.dumps(json_data, indent=2))
        # for bs_data in json_data:
        #     for data in bs_data['data']:
        #         logger.info(f"{data['jobname']}, {data['rw']}, bs={data['bs']}, iops={data['iops']}")
        ReportXlsx("./", json_data).create_xlsx_file()


if __name__ == '__main__':
    pass
