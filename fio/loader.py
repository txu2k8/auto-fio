#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:loader
@time:2022/11/16
@email:tao.xu2008@outlook.com
@description: 数据加载
"""
from typing import Dict
from pydantic import ValidationError

from fio import exceptions
from fio.models import Client, FIOResult


def load_client(data: Dict) -> Client:
    """将client数据（字典）转成 Client 对象"""
    try:
        # validate with pydantic Client model
        client_obj = Client.parse_obj(data)
    except ValidationError as ex:
        err_msg = f"Client ValidationError:\nerror: {ex}\ncontent: {data}"
        raise exceptions.ClientFormatError(err_msg)

    return client_obj


def load_fio_result(data: Dict) -> FIOResult:
    """将 FIOResult 数据（字典）转成 FIOResult 对象"""
    try:
        # validate with pydantic Node model
        fio_r_obj = FIOResult.parse_obj(data)
    except ValidationError as ex:
        err_msg = f"FIOResult ValidationError:\nerror: {ex}\ncontent: {data}"
        raise exceptions.FIOResultFormatError(err_msg)

    return fio_r_obj


if __name__ == '__main__':
    pass
