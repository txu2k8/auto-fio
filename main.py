#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:main
@time:2022/09/16
@email:tao.xu2008@outlook.com
@description:
"""
import sys
from cli.main import app


if __name__ == '__main__':
    try:
        app()
    except KeyboardInterrupt:
        print("\nControl-C pressed - quitting...")
        sys.exit(1)
