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
from fio_perf.runner import FIORunner


def init_print(case_id, desc, **kwargs):
    logger.log('DESC', '{0}输入信息{0}'.format('*' * 20))
    logger.log('DESC', "测试用例: {}".format(case_id))
    logger.log('DESC', '测试描述：{}'.format(desc))
    command = 'python3 ' + ' '.join(sys.argv)
    logger.log('DESC', '执行命令：{}'.format(command))
    logger.log('DESC', '执行时间：{}'.format(datetime.now()))
    for k, v in kwargs.items():
        if k == "rw":
            v = [x.value for x in v]
        logger.log('DESC', '{}：{}'.format(k, v))
    # logger.log('DESC', '*' * 48)


def int_split_callback(value: str):
    ret_value = []
    if isinstance(value, list):
        for v in value:
            ret_value.extend([int(x) for x in v.strip().split(",")])
    else:
        ret_value = [int(x) for x in value.strip().split(",")]
    return ret_value


def str_split_callback(value: str):
    ret_value = []
    if isinstance(value, list):
        for v in value:
            ret_value.extend(v.strip().split(","))
    else:
        ret_value = value.strip().split(",")
    return ret_value


@app.command(help='FIO性能测试')
def perf(
        template: Text = typer.Option('', exists=True, resolve_path=True, help="FIO测试配置文件路径（如果需要更多参数，可以使用配置文件）TODO"),
        target: List[Text] = typer.Option(..., callback=str_split_callback, help="【列表，逗号分隔】FIO测试目标路径"),
        rw: List[RWTypeEnum] = typer.Option([RWTypeEnum.randrw], help="【列表】测试类型"),
        iodepth: List[Text] = typer.Option([1, 2], callback=int_split_callback, help="【列表，逗号分隔】队列深度"),
        numjobs: List[Text] = typer.Option([1, 16], callback=int_split_callback, help="【列表，逗号分隔】并发数"),
        blocksize: List[Text] = typer.Option(['4K'], callback=str_split_callback, help="【列表，逗号分隔】块大小，例：4K，单位(B/K/M)"),
        rwmixread: List[Text] = typer.Option([], callback=int_split_callback, help="【列表，逗号分隔】混合读写->读占比（百分比）"),

        size: Text = typer.Option('100M', help="单个文件大小，例：1G，单位(B/K/M/G)"),
        output: str = typer.Option(LOG_DIR, help="FIO测试结果保存路径"),
        clean: bool = typer.Option(False, help="执行完成后清理数据"),
        dry_run: bool = typer.Option(False, help="不执行fio参数，仅打印执行流程"),
        quiet: bool = typer.Option(False, help="打印执行进度"),
        trace: bool = typer.Option(False, help="print TRACE level log"),
        case_id: int = typer.Option(0, min=0, help="测试用例ID，关联到日志文件名"),
        desc: str = typer.Option('', help="测试描述"),
):
    init_logger(prefix='fio', case_id=case_id, trace=trace)
    init_print(case_id, desc, **{
        "target": target,
        "template": template,
        "rw": rw,
        "iodepth": iodepth,
        "numjobs": numjobs,
        "bs": blocksize,
        "clean": clean,
    })
    runner = FIORunner(
        target, template, rw, iodepth, numjobs, blocksize, rwmixread,
        size=size, output=output, clean=clean, dry_run=dry_run, quiet=quiet
    )
    runner.run()


@app.command(help='FIO perf - 1：写性能测试')
def perf_write(
        target: str = typer.Option('', help="FIO测试目标路径"),
        template: str = typer.Option('', help="FIO测试配置文件路径"),
        rw: List[RWTypeEnum] = typer.Option([RWTypeEnum.randwrite], help="测试类型【列表】"),
        iodepth: List[int] = typer.Option([1], help="队列深度【列表】"),
        numjobs: List[int] = typer.Option([1], help="并发数【列表】"),
        bs: str = typer.Option('4K', help="对象SIZE，格式：1MB，支持单位(B/KB/MB/GB)"),
        output: str = typer.Option(LOG_DIR, help="FIO测试结果保存路径"),

        clean: bool = typer.Option(False, help="执行完成后清理数据"),
        trace: bool = typer.Option(False, help="print TRACE level log"),
        case_id: int = typer.Option(0, min=0, help="测试用例ID，关联到日志文件名"),
        desc: str = typer.Option('', help="测试描述"),
):
    init_logger(prefix='cosbench', case_id=case_id, trace=trace)
    init_print(case_id, desc, **{
        "target": target,
        "template": template,
        "rw": rw,
        "iodepth": iodepth,
        "numjobs": numjobs,
        "bs": bs,
        "clean": clean,
    })
    runner = FIORunner(target, template, rw, iodepth, numjobs, bs, output, clean=clean)
    runner.run()


if __name__ == "__main__":
    app()
