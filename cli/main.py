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

from config import __version__, __author__


app = typer.Typer(name="auto_fio", add_completion=False, help=f"FIO测试工具自动化 CLI.\n\n{__author__}")
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def dis_version(display: bool):
    if display:
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
def main(ctx: typer.Context,
         version: bool = typer.Option(
            False, "--version", "-v", help="Show version", callback=dis_version, is_eager=True
         ),  # 调用 dis_version 函数， 并且优先级最高(is_eager)
         ):
    """
    FIO测试工具自动化 CLI.
    """
    # typer.confirm("Are you sure?", default=True, abort=True)  # 给出选项，abort选项表示 No 则直接中断
    if ctx.invoked_subcommand is None:
        print('main process')


if __name__ == '__main__':
    app()
