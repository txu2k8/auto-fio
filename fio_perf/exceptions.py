#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:exceptions
@time:2022/09/16
@email:tao.xu2008@outlook.com
@description:
"""


class MyBaseError(Exception):
    pass


class FileFormatError(MyBaseError):
    pass


class BenchSettingsFormatError(FileFormatError):
    pass


class ClientFormatError(FileFormatError):
    pass


class FIOResultFormatError(FileFormatError):
    pass


if __name__ == '__main__':
    pass
