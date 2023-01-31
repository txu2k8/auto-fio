#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:exceptions
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description:
"""


class MyBaseError(Exception):
    pass


class FileFormatError(MyBaseError):
    pass


class FIOParametersFormatError(FileFormatError):
    pass


if __name__ == '__main__':
    pass
