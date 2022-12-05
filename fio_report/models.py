#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:models
@time:2022/09/15
@email:tao.xu2008@outlook.com
@description:
"""
from typing import Text, List
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
