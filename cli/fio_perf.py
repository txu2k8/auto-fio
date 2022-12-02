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
import re
from typing import List, Text
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


def duration_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    second = 0
    if ctx.resilient_parsing:
        return
    if not value:
        return second
    else:
        try:
            dhms = re.findall(r'-?[0-9]\d*', value)
            d, h, m, s = dhms
            second = int(d) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        except Exception as e:
            raise typer.BadParameter("duration参数格式错误，必需以h、m、s组合，如1h3m10s")

    return second


@app.command(help='FIO性能测试')
def perf(
        template: str = typer.Option('', help="FIO测试配置文件路径（如果需要更多参数，可以使用配置文件）"),
        target: List[str] = typer.Option(['D:\\minio\\'], help="FIO测试目标路径【列表】"),
        rw: List[RWTypeEnum] = typer.Option([RWTypeEnum.randrw], help="测试类型【列表】"),
        iodepth: List[int] = typer.Option([1, 2], help="队列深度【列表】"),
        numjobs: List[int] = typer.Option([1, 16], help="并发数【列表】"),
        bs: List[Text] = typer.Option(['4K'], help="Block Size，格式：1M，支持单位(B/K/M)"),
        rwmixread: List[int] = typer.Option([0], help="混合读写->读占比（百分比）"),

        size: Text = typer.Option('100M', help="单个文件大小，格式：1M，支持单位(B/K/M/G)"),
        output: str = typer.Option(LOG_DIR, help="FIO测试结果保存路径"),

        clean: bool = typer.Option(False, help="执行完成后清理数据"),
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
        "bs": bs,
        "clean": clean,
    })
    runner = FIORunner(
        target, template, rw, iodepth, numjobs, bs, rwmixread,
        size=size, output=output, clean=clean
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
