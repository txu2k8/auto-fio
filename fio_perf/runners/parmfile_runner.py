#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner_parmfile
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import os
from loguru import logger

from fio_perf.models import FIOParmFiles
from fio_perf.display import display_parmfile
from fio_perf.runners.base import FIOBaseRunner, parse_fio_parmfile


class FIOParmFileRunner(FIOBaseRunner):
    """FIO 执行引擎 - 传入配置文件/目录，遍历执行"""

    def __init__(self, client, parmfile, *args, **kwargs):
        super(FIOParmFileRunner, self).__init__(*args, **kwargs)
        self.parameters = FIOParmFiles(
            client=client,
            parmfile=parmfile,
            output=self.output,
            dry_run=self.dry_run,
            quiet=self.quiet,
        )
        print(self.parameters)

    def list_fio_parmfiles(self):
        """
        根据fio配置参数路径，查找所有配置文件
        :return:
        """
        parmfiles = []
        parmfile_path = os.path.abspath(self.parameters.parmfile)
        if os.path.isdir(parmfile_path):
            # 配置文件目录，递归遍历所有文件
            for dir_path, dir_names, file_names in os.walk(parmfile_path):
                for file_name in file_names:
                    parmfiles.append(os.path.join(dir_path, file_name))
        elif os.path.exists(parmfile_path):
            parmfiles.append(parmfile_path)
        else:
            raise Exception(f"FIO配置文件路径无效：{parmfile_path}")
        return parmfiles

    def generate_test_list(self):
        """
        根据输入的parmfile，遍历所有fio配置文件，生成测试项
        :return:
        """
        logger.log("STAGE", "遍历fio配置文件生成待测试项...")
        parmfiles = self.list_fio_parmfiles()
        for parmfile in parmfiles:
            test = parse_fio_parmfile(parmfile)
            self.parameters.tests.append(test)
            self.parameters.estimated_duration += int(test["runtime"]) if "runtime" in test else 0

        display_parmfile(self.parameters)

        return self.parameters.tests

    def generate_fio_command(self, test):
        """
        生成FIO执行命令
        :param test:
        :return:
        """
        command = ["fio"]
        if self.parameters.client:
            command.append(f"--client={self.parameters.client}")
        command.extend(
            [
                test["f_path"],
                "--output-format=json",
                f"--output={test['output']}"
            ]
        )
        return command


if __name__ == '__main__':
    pass
