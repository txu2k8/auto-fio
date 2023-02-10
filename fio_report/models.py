#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:models
@time:2022/12/04
@email:tao.xu2008@outlook.com
@description:
"""
from typing import Text, List, Tuple
from pydantic import BaseModel


class ReportSettings(BaseModel):
    """报告 配置信息 - 数据模型"""
    rw: Text = ''
    filter: List = ["read", "write"]
    input_directory: List[Text] = []


class PerformanceResult(BaseModel):
    """性能测试结果 - 数据模型"""
    bw: int = 0
    iops: int = 0
    latency: int = 0


class FIOResult(BaseModel):
    """FIO测试结果 - 数据模型"""
    jobname: Text = ''
    client_num: int = 1
    ioengine: Text = ''
    runtime: int = 0
    direct: int = 1
    iodepth: Text = ''
    numjobs: Text = ''
    filesize: Text = ''
    bs: Text = ''
    rw: Text = ''
    write: PerformanceResult = PerformanceResult()
    read: PerformanceResult = PerformanceResult()


def generate_column_title_1():
    title_row_1 = []
    title_row_2 = []
    for k, v in FIOResult().dict().items():
        if isinstance(v, dict):
            for p_k, p_v in v.items():
                title_row_1.append(k)
                title_row_2.append(p_k)
        else:
            title_row_1.append(k)
            title_row_2.append(v)
    return title_row_1, title_row_2


def generate_column_title_2():
    title_row = []
    for k, v in FIOResult().dict().items():
        if isinstance(v, dict):
            for p_k, p_v in v.items():
                title_row.append(f"{p_k}-{k}")
        else:
            title_row.append(k)
    return title_row


class ExcelReportSettings(BaseModel):
    """报告 配置信息 - 数据模型"""
    # 结果统计 - 数据表
    data_sheet_title: Text = "结果统计"
    data_sheet_index: int = 0
    data_column_title: Tuple[Tuple] = (generate_column_title_2(),)
    data_column_write_idx = len(FIOResult().dict().keys()) - 2  # 测试结果开始列 -- bw-write列

    # 对比分析 - 图表
    chart_sheet_title: Text = "对比分析"
    chart_sheet_index: int = 1
    chart_type: Text = "col"
    chart_style: int = 10
    chart_title: Text = "FIO结果对比"
    chart_x_axis_title: Text = "jobname"
    chart_y_axis_title: Text = ""

    # 描述信息 - 数据表
    desc_sheet_title: Text = "描述信息"
    desc_sheet_index: int = 2
    desc_column_title: Tuple = ("键", "值")

    # 环境配置 - 数据表
    env_sheet_title: Text = "环境配置"
    env_sheet_index: int = 3


if __name__ == "__main__":
    print(generate_column_title_2())
