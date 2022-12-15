#!/usr/bin/python
# -*- coding:utf-8 _*-
"""
@author:TXU
@file:main
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description:
"""
import typer
from typing import Optional

from config import __version__, __author__


def version_callback(value: bool):
    if value:
        print(__version__)
        print(__author__)
        raise typer.Exit()


def public(
        version: Optional[bool] = typer.Option(
            None, "--version", callback=version_callback, help='Show the tool version'
        ),
):
    """公共参数"""
    pass


app = typer.Typer(name="Perf", callback=public, add_completion=False, help=f"FIO测试工具自动化 CLI.\n\n{__author__}")


if __name__ == '__main__':
    app()
