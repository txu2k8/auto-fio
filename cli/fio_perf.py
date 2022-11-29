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
from datetime import datetime
from loguru import logger
import typer

from cli.log import init_logger
from cli.main import app
from cosbench.models import WorkloadTypeEnum
from cosbench.runner import CosBenchRunner


def init_print(case_id, desc, bucket_num, obj_num, workers, testbed):
    logger.log('DESC', '{0}基本信息{0}'.format('*' * 20))
    logger.log('DESC', "测试用例: {}".format(case_id))
    logger.log('DESC', '测试描述：{}'.format(desc))
    logger.log('DESC', '桶数：{}'.format(bucket_num))
    logger.log('DESC', '对象数：{}'.format(obj_num))
    logger.log('DESC', '并发数：{}'.format(workers))
    command = 'python3 ' + ' '.join(sys.argv)
    logger.log('DESC', '执行命令：{}'.format(command))
    logger.log('DESC', '执行时间：{}'.format(datetime.now()))
    logger.log('DESC', '测试床：{}'.format(testbed))
    logger.log('DESC', '*' * 48)


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


@app.command(help='cosbench perf - 1：读性能测试')
def perf_read(
        testbed: str = typer.Option('', help="测试环境配置文件路径"),
        bucket_prefix: str = typer.Option('cosbench', help="桶名称前缀"),
        bucket_num: int = typer.Option(32, min=1, help="桶数量，对象会被均衡写入到各个桶中"),
        obj_prefix: str = typer.Option('data', help="对象名前缀"),
        obj_num: int = typer.Option(60, min=1, help="对象数"),
        obj_size: str = typer.Option('128MB', help="对象SIZE，格式：1MB，支持单位(B/KB/MB/GB)"),
        workers: int = typer.Option(1, min=1, help="总并发数"),
        clean: bool = typer.Option(False, help="执行完成后清理数据"),
        trace: bool = typer.Option(False, help="print TRACE level log"),
        case_id: int = typer.Option(0, min=0, help="测试用例ID，关联到日志文件名"),
        desc: str = typer.Option('', help="测试描述"),
):
    init_logger(prefix='cosbench', case_id=case_id, trace=trace)
    init_print(case_id, desc, bucket_num, obj_num, workers, testbed)
    cr = CosBenchRunner(testbed, bucket_prefix, bucket_num, obj_prefix, obj_num, obj_size, workers, clean)
    cr.run(WorkloadTypeEnum.read)


@app.command(help='cosbench perf - 1：写性能测试')
def perf_write(
        testbed: str = typer.Option('', help="测试环境配置文件路径"),
        bucket_prefix: str = typer.Option('cosbench', help="桶名称前缀"),
        bucket_num: int = typer.Option(32, min=1, help="桶数量，对象会被均衡写入到各个桶中"),
        obj_prefix: str = typer.Option('data', help="对象名前缀"),
        obj_num: int = typer.Option(60, min=1, help="对象数"),
        obj_size: str = typer.Option('128MB', help="对象SIZE，格式：1MB，支持单位(B/KB/MB/GB)"),
        workers: int = typer.Option(1, min=1, help="总并发数"),
        clean: bool = typer.Option(False, help="执行完成后清理数据"),
        trace: bool = typer.Option(False, help="print TRACE level log"),
        case_id: int = typer.Option(0, min=0, help="测试用例ID，关联到日志文件名"),
        desc: str = typer.Option('', help="测试描述"),
):
    init_logger(prefix='cosbench_perf_write', case_id=case_id, trace=trace)
    init_print(case_id, desc, bucket_num, obj_num, workers, testbed)
    cr = CosBenchRunner(testbed, bucket_prefix, bucket_num, obj_prefix, obj_num, obj_size, workers, clean)
    cr.run(WorkloadTypeEnum.write)


if __name__ == "__main__":
    app()
