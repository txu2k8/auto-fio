#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runners
@time:2022/11/27
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import sys

import itertools
from pathlib import Path
from loguru import logger

from fio_perf import display, loader
from fio_perf.models import FIOParameters
from fio_perf.runners.base import FIOBaseRunner, progress_bar


class FIOParametersRunner(FIOBaseRunner):
    """FIO 执行引擎 - 参数排列组合执行、收集结果"""

    def __init__(self, target, template, rw, iodepth, numjobs, bs, rwmixread, *args, **kwargs):
        super(FIOParametersRunner, self).__init__(*args, **kwargs)
        self.parameters = FIOParameters(
            target=target,
            template=str(template),
            rw=rw,
            iodepth=iodepth,
            numjobs=numjobs,
            bs=bs,
            rwmixread=rwmixread,
            size=kwargs["size"],
            runtime=kwargs["runtime"],
            extra_opts=kwargs["extra_opts"],
            output=self.output,
            dry_run=self.dry_run,
            quiet=self.quiet,
        )

    def check_parameters(self):
        """
        检查配置 有效性
        :return:
        """
        logger.log("STAGE", "检查FIO参数配置有效性...")
        if self.parameters.type not in ["device", "rbd"] and not self.parameters.size:
            logger.error("When the target is a file or directory, --size must be specified.")
            sys.exit(4)
        if self.parameters.type == "directory":
            for item in self.parameters.target:
                if not os.path.exists(item):
                    logger.error(f"The target directory ({item}) doesn't seem to exist.")
                    sys.exit(5)

        for mode in self.parameters.rw:
            writemodes = ['write', 'randwrite', 'rw', 'readwrite', 'trimwrite']
            if mode in writemodes and not self.parameters.destructive:
                logger.error(f"Mode {mode} will overwrite data on {self.parameters.target} but destructive flag not set.")
                sys.exit(1)

            if mode in self.parameters.mixed:
                if self.parameters.rwmixread:
                    self.parameters.loop_items.append("rwmixread")
                else:
                    logger.error("If a mixed (read/write) mode is specified, please specify --rwmixread")
                    sys.exit(8)
            else:
                self.parameters.filter_items.append("rwmixread")

    @staticmethod
    def check_target_type(target, filetype):
        """
        Validate path and file / directory type.
        It also returns the appropritate fio command line parameter based on the
        file type.
        :param target:
        :param filetype:
        :return:
        """

        keys = ["file", "device", "directory", "rbd"]
        test = {keys[0]: Path.is_file, keys[1]: Path.is_block_device, keys[2]: Path.is_dir}
        parameter = {keys[0]: "--filename", keys[1]: "--filename", keys[2]: "--directory"}

        if not filetype == "rbd":

            if not os.path.exists(target):
                logger.error(f"Target {filetype} {target} does not exist.")
                sys.exit(10)

            if filetype not in keys:
                logger.error(f"Error, filetype {filetype} is an unknown option.")
                sys.exit(123)

            check = test[filetype]

            path_target = Path(target)  # path library needs to operate on path object

            if check(path_target):
                return parameter[filetype]
            else:
                logger.error(f"Target {filetype} {target} is not {filetype}.")
                sys.exit(10)
        else:
            return None

    def gather_parameters(self):
        """
        聚合默认配置和用户自定义配置
        :return:
        """
        logger.log("STAGE", "聚合FIO参数和配置文件内容参数（TODO）...")
        custom_parameters = {}
        self.parameters = loader.load_fio_parameters({**dict(self.parameters), **custom_parameters})
        self.check_parameters()

    def generate_test_list(self):
        """
        根据输入的参数列表，遍历生成待测试的条件组合
        :return:
        """
        logger.log("STAGE", "条件组合生成待测试项...")
        self.gather_parameters()
        loop_items = self.parameters.loop_items
        dict_parameters = dict(self.parameters)
        dataset = []
        for item in loop_items:
            result = dict_parameters[item]
            dataset.append(result)
        benchmark_list = list(itertools.product(*dataset))

        result = [dict(zip(loop_items, item)) for item in benchmark_list]
        self.parameters.tests = result

        display.display_header(self.parameters)
        return result

    def expand_command_line(self, command, test):
        """
        生成测试命令
        :param command:
        :param test:
        :return:
        """
        # 通用参数
        if self.parameters.size:
            command.append(f"--size={self.parameters.size}")
        if self.parameters.runtime and not self.parameters.entire_device:
            command.append(f"--runtime={self.parameters.runtime}")
        if self.parameters.time_based:
            command.append("--time_based")
        command.append(f"--ioengine={self.parameters.ioengine}")
        command.append(f"--direct={self.parameters.direct}")
        if self.parameters.group_reporting:
            command.append("--group_reporting")

        # 测试轮巡 指定参数
        for k, v in test.items():
            if k == "target":
                continue
            command.append(f"--{k}={v}")

        if self.parameters.rwmixread and test["rw"] in self.parameters.mixed:
            command.append(f"--rwmixread={test['rwmixread']}")

        if self.parameters.extra_opts:
            command.append(self.parameters.extra_opts)

        return command

    def generate_fio_command(self, test):
        """
        生成FIO执行命令
        :param test:
        :return:
        """
        command = [
            "fio",
            "--output-format=json",
            f"--output={test['output']}",
            f"--name={test['name']}",
        ]
        if self.parameters.template:
            command.append(self.parameters.template)

        target_parameter = self.check_target_type(test["target"], self.parameters.type)
        if target_parameter:
            command.append(f"{target_parameter}={test['target']}")

        command = self.expand_command_line(command, test)

        return command


if __name__ == '__main__':
    pass
