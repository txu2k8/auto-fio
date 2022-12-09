#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:models
@time:2022/09/15
@email:tao.xu2008@outlook.com
@description:
"""
from enum import Enum
from typing import Text, List
from pydantic import BaseModel


class RWTypeEnum(str, Enum):
    """
    参数IO读写类型
    """
    randread = "randread"  # 测试随机读的 I/O
    randwrite = "randwrite"  # 测试随机写的 I/O
    randrw = "randrw"  # 测试随机混合写和读的 I/O
    read = "read"  # 测试顺序读的 I/O
    write = "write"  # 测试顺序写的 I/O
    rw = "rw"  # 测试顺序混合写和读的 I/O
    readwrite = "readwrite"  # 测试顺序混合写和读的 I/O, 等同rw


RWTypeEnum.randread.description = "测试随机读的 I/O"
RWTypeEnum.randwrite.description = "测试随机写的 I/O"
RWTypeEnum.randrw.description = "测试随机混合写和读的 I/O"
RWTypeEnum.read.description = "测试顺序读的 I/O"
RWTypeEnum.write.description = "测试顺序写的 I/O"
RWTypeEnum.rw.description = "测试顺序混合写和读的 I/O"


class FIOKwargs(BaseModel):
    """FIO参数 - 模型"""
    fio_bin: Text = "fio"
    directory: Text
    rw: RWTypeEnum
    bs: Text = '4K'
    size: Text = '100M'
    numjobs: int = 1
    iodepth: int = 4
    time_based: bool = True
    runtime: int = 120
    ioengine: Text = "libaio"
    direct: int = 1
    group_reporting: bool = True


class FIOSettings(BaseModel):
    """FIO 配置信息 - 数据模型"""
    # 测试目标、参数模板
    template: Text = ""  # FIO命令行参数配置文件
    target: List[Text]
    # FIO 遍历参数列表，参数传递
    rw: List[Text] = [RWTypeEnum.randread.value, RWTypeEnum.randwrite.value]
    iodepth: List[int] = [1, 2, 4, 8, 16, 32, 64]
    numjobs: List[int] = [1, 2, 4, 8, 16, 32, 64]
    bs: List[Text] = ['4K']
    rwmixread: List[int] = []  # 混合读写时，读占比

    # 所有测试统一参数
    size: Text = '100M'
    runtime: int = 60
    time_based: bool = True
    ioengine: Text = "libaio"
    direct: int = 1
    group_reporting: bool = True

    entire_device: bool = False
    destructive: bool = True
    ss: bool = False  # Detect steady state
    ss_dur: Text = None  # Steady state rolling window
    ss_ramp: Text = None  # Steady state rampup

    extra_opts: List = []  # 其他参数

    # 框架相关参数
    drop_caches: bool = True
    type: Text = "directory"
    dry_run: bool = False
    quiet: bool = False
    output: Text = "./"
    loops: int = 1
    # 定义常量
    mixed: List = ["readwrite", "rw", "randrw"]  # mixed测试类型列表
    loop_items: List = [
        "target",
        "rw",
        "iodepth",
        "numjobs",
        "bs",
    ]
    filter_items: List = [
        "filter_items",
        "drop_caches",
        "tests",
        "loop_items",
        "dry_run",
        "mixed",
        "quiet",
    ]

    # 计算保存数据
    tests: List = []


# FIO参数描述
DESCRIPTIONS = {
        "target": "Test target",
        "template": "Job template",
        "ioengine": "I/O Engine",
        "rw": "Test mode (read/write)",
        "iodepth": "IOdepth to be tested",
        "numjobs": "NumJobs to be tested",
        "bs": "Block size",
        "direct": "Direct I/O",
        "size": "Specified simple1 data size",
        "rwmixread": "Read/write mix in %% read",
        "runtime": "Time duration per simple1 (s)",
        "extra_opts": "Extra custom options",
        "loginterval": "Log interval of perf data (ms)",
        "invalidate": "Invalidate buffer cache",
        "loops": "run loops",
        "type": "Target type",
        "output": "Output folder",
        "time_based": "Time based",
        "tests": "run tests",
        "benchmarks": "Number of benchmarks",
        "precondition": "Run precondition workload",
        "precondition_template": "Precondition template",
        "precondition_repeat": "Precondition after each simple1",
        "ss": "Detect steady state",
        "ss_dur": "Steady state rolling window",
        "ss_ramp": "Steady state rampup",
        "entire_device": "Benchmark entire device",
        "ceph_pool": "Ceph RBD pool",
        "destructive": "Allow destructive writes",

        "group_reporting": "group reporting"
    }


class Client(BaseModel):
    """客户端 - 参数模型"""
    ip: Text = ''
    user: Text = 'root'
    password: Text = ''


# 结果
class ResultType(str, Enum):
    """
    FIO 测试结果 类型
    """
    read = "read"  # 读结果
    write = "write"  # 写结果


class FIOResult(BaseModel):
    """
    FIO 测试结果
    """
    type: ResultType  # 测试结果类型
    IOPS: Text = ''  # iops
    BW: Text = ''  # 带宽
    latency: Text = ''  # 使用

