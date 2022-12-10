#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:models
@time:2022/11/27
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


class FIOSettings(BaseModel):
    """FIO 配置信息 - 数据模型"""
    # 测试目标、参数模板
    template: Text = ""  # FIO命令行参数配置文件
    target: List[Text]
    # FIO 遍历参数列表，参数传递
    rw: List[Text] = [RWTypeEnum.randread.value, RWTypeEnum.randwrite.value]
    iodepth: List[int] = [1, 2, 4]
    numjobs: List[int] = [1, 16, 32]
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
    extra_opts: Text = ""  # 其他参数，拼接为字符串，如： “--key value --bool_key”

    # 框架相关参数
    drop_caches: bool = True
    type: Text = "directory"
    dry_run: bool = False
    quiet: bool = False
    output: Text = "./"

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
        "type": "Target type",
        "output": "Output folder",
        "time_based": "Time based",
        "tests": "run tests",
        "entire_device": "Benchmark entire device",
        "destructive": "Allow destructive writes",
        "group_reporting": "group reporting"
    }
