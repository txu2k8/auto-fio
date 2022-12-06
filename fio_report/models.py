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

    type: List = []
    dpi: int = 200
    title_fontsize: int = 16
    subtitle_fontsize: int = 10
    credit_fontsize: int = 10
    source_fontsize: int = 8
    table_fontsize: int = 10
    tablecolumn_spacing: int = 0.01
    colors: List = []

    input_directory: List[Text] = []


class ExcelReportSettings(BaseModel):
    """报告 配置信息 - 数据模型"""
    # 结果统计 - 数据表
    data_sheet_title: Text = "结果统计"
    data_sheet_index: int = 1
    data_column_title: Tuple = ('jobname', 'rw', 'iodepth', 'numjobs', 'bs', 'iops', 'bw', 'latency')

    # 对比分析 - 图表
    chart_sheet_title: Text = "对比分析"
    chart_sheet_index: int = 2
    chart_type: Text = "col"
    chart_style: int = 10
    chart_title: Text = "FIO结果对比"
    chart_x_axis_title: Text = "jobname"
    chart_y_axis_title: Text = ""
