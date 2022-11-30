#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:command_generator
@time:2022/11/29
@email:tao.xu2008@outlook.com
@description: 根据参数组合，生成FIO命令行列表
"""
from typing import List
import subprocess
from loguru import logger

from fio.models import FIOKwargs, RWTypeEnum


class FIOOption(object):
    """根据参数组合，生成FIO命令行，执行"""
    def __init__(self, rw_list: List[RWTypeEnum], bs_list, numjobs_list, *args, **kwargs):
        self.rw_list = rw_list
        self.bs_list = bs_list
        self.numjobs_list = numjobs_list
        self.args = args
        self.kwargs = kwargs

        self.fio_bin = ""

    def fio_args_parse(self):
        """
        生成 FIOKwargs 列表
        :return:
        """
        fio_kwargs_list = []

    @staticmethod
    def _args2cmd(fio: FIOKwargs):
        """
        根据参数，生成测试命令
        :param fio:
        :return:
        """
        name = "{}_{}jobs_{}".format(fio.bs, fio.numjobs, fio.rw)
        _cmd = f"{fio.fio_bin} --name={name} --directory={fio.directory} " \
               f"--bs={fio.bs} --rw={fio.rw} --iodepth={fio.iodepth} --numjobs={fio.numjobs} " \
               f"--ioengine={fio.ioengine} --direct={fio.direct} " \
               f"--size={fio.size}  "
        if fio.time_based:
            _cmd += f"--time_based --runtime={fio.runtime} "
        if fio.group_reporting:
            _cmd += "--group_reporting "
        return _cmd

    @staticmethod
    def _exec(cmd):
        rc, output = subprocess.getstatusoutput(cmd)
        logger.debug(output.strip('\n'))
        return rc, output

    def is_fio_installed(self):
        rc, output = self._exec("{} --version".format(self.fio_bin))
        logger.info(output)
        if rc == 0 and "fio-" in output:
            return True
        return False

    def get_result(self, output):
        """
        根据fio执行输出，分析获取测试结果
        :param output:
        :return:
        """
        pass

    def report_csv(self, result):
        """
        根据解析到的测试结果，输出csv结果文件
        :param result:
        :return:
        """
        pass

    def run(self, fio_kwargs):
        """

        :param fio_kwargs:
        :return:
        """
        self.is_fio_installed()

        cmd = self._args2cmd(fio_kwargs)
        rc, output = self._exec(cmd)
        logger.info(output)
        return rc, output


if __name__ == '__main__':
    pass
