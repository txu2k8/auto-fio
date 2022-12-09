#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:models
@time:2022/09/15
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


class ExcelReportSettings(BaseModel):
    """报告 配置信息 - 数据模型"""
    # 结果统计 - 数据表
    data_sheet_title: Text = "结果统计"
    data_sheet_index: int = 0
    data_column_title: Tuple = (
        'jobname', 'rw', 'iodepth', 'numjobs', 'bs',
        'bw-write', 'iops-write', 'latency-write',
        'bw-read', 'iops-read', 'latency-read'
    )

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
