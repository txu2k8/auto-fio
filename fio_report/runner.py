#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner
@time:2022/12/04
@email:tao.xu2008@outlook.com
@description: 
"""
from loguru import logger

from fio_report.output_json_parse import FIOJsonParse
from fio_report.report_xlsx import ReportXlsx


class FIOReportRunner(object):
    """FIO测试结果收集，报告生成"""
    def __init__(self, data_path, output, comments=None, *args, **kwargs):
        self.data_path = data_path
        self.output = output
        self.comments = comments

    def run(self):
        json_data = FIOJsonParse(self.data_path).get_json_data()
        # with open("./sss.json", "w+") as f:
        #     f.write(json.dumps(json_data, indent=2))
        ReportXlsx(self.output, json_data, comments=self.comments).create_xlsx_file()
        logger.log("DESC", "输出结果：{}".format(self.output))


if __name__ == '__main__':
    pass
