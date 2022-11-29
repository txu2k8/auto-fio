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
    randwread = "randwread"  # 测试随机读的 I/O
    randwrite = "randwrite"  # 测试随机写的 I/O
    randrw = "randrw"  # 测试随机混合写和读的 I/O
    read = "read"  # 测试顺序读的 I/O
    write = "write"  # 测试顺序写的 I/O
    rw = "rw"  # 测试顺序混合写和读的 I/O


RWTypeEnum.randwread.description = "测试随机读的 I/O"
RWTypeEnum.randwrite.description = "测试随机写的 I/O"
RWTypeEnum.randrw.description = "测试随机混合写和读的 I/O"
RWTypeEnum.read.description = "测试顺序读的 I/O"
RWTypeEnum.write.description = "测试顺序写的 I/O"
RWTypeEnum.rw.description = "测试顺序混合写和读的 I/O"


class Client(BaseModel):
    """客户端 - 参数模型"""
    ip: Text = ''
    user: Text = 'root'
    password: Text = ''


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

