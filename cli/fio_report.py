#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:stress
@time:2022/09/01
@email:tao.xu2008@outlook.com
@description: CosBench性能测试 ...
"""
import sys
from typing import List, Optional, Text, Union
from datetime import datetime
from loguru import logger
import typer

from cli.log import init_logger
from cli.main import app
from config import LOG_DIR
from fio_perf.models import RWTypeEnum
from fio_report.runner import FIOReportRunner


def init_print(**kwargs):
    logger.log('DESC', '{0}输入信息{0}'.format('*' * 20))
    command = 'python3 ' + ' '.join(sys.argv)
    logger.log('DESC', '执行命令：{}'.format(command))
    logger.log('DESC', '执行时间：{}'.format(datetime.now()))
    for k, v in kwargs.items():
        if k == "rw":
            v = [x.value for x in v]
        logger.log('DESC', '{}：{}'.format(k, v))
    # logger.log('DESC', '*' * 48)


@app.command(help='FIO测试结果生成csv报告')
def report_csv(
        data_path: List[Text] = typer.Option(["D:\\minio\\20221203_085114\\test"], help="FIO测试结果数据路径"),
        output: Text = typer.Option(LOG_DIR, help="报告文件输出路径"),
):
    init_logger(prefix='report-csv')
    init_print(**{
        "input": data_path,
        "output": output,
    })
    runner = FIOReportRunner(
        data_path=data_path, output=output
    )
    runner.run()


if __name__ == "__main__":
    app()
