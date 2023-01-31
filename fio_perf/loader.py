#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:loader
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description: 数据加载
"""
from typing import Dict
from pydantic import ValidationError

from fio_perf import exceptions
from fio_perf.models import FIOParameters


def load_fio_parameters(data: Dict) -> FIOParameters:
    """将 FIOResult 数据（字典）转成 FIOResult 对象"""
    try:
        # validate with pydantic Node model
        fio_s_obj = FIOParameters.parse_obj(data)
    except ValidationError as ex:
        err_msg = f"FIOParameters ValidationError:\nerror: {ex}\ncontent: {data}"
        raise exceptions.FIOParametersFormatError(err_msg)

    return fio_s_obj


if __name__ == '__main__':
    pass
