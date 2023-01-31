#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:base
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import sys
import shutil
import subprocess
from loguru import logger

from config import DT_STR
from fio_report.runner import FIOReportRunner


class FIOBaseRunner(object):
    """FIO 执行引擎 - base"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.case_id = kwargs["case_id"] if "case_id" in kwargs else ""
        self.desc = kwargs["desc"] if "desc" in kwargs else ""
        self.output = os.path.abspath(kwargs["output"]) if "output" in kwargs else "./"
        self.report = kwargs["report"] if "report" in kwargs else True
        self.dry_run = kwargs["dry_run"] if "dry_run" in kwargs else False
        self.quiet = kwargs["quiet"] if "quiet" in kwargs else False

    @staticmethod
    def _exec(cmd):
        logger.log("RUN",  cmd)
        rc, output = subprocess.getstatusoutput(cmd)
        logger.debug(output.strip('\n'))
        return rc, output

    def is_fio_installed(self):
        logger.log("STAGE", "检查FIO工具是否安装...")
        command = "fio_perf"
        if shutil.which(command) is None:
            logger.error("Fio executable not found in path. Is Fio installed?")
            sys.exit(1)

        logger.log("STAGE", "检查FIO工具版本...")
        command = ["fio", "--version"]
        rc, output = self._exec(command)
        result = output.strip()
        if "fio-3" in result:
            return True
        elif "fio-2" in result:
            logger.error(f"Your Fio version ({result}) is not compatible. Please use Fio-3.x")
            sys.exit(1)
        else:
            logger.error("Could not detect Fio version.")
            sys.exit(1)

    def drop_caches(self):
        # logger.info("清除环境cache...")
        command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
        self._exec(command)

    @staticmethod
    def make_directory(directory):
        try:
            if not os.path.exists(directory):
                logger.log("STAGE", f"创建FIO测试结果保存目录：{directory}")
                os.makedirs(directory)
        except OSError:
            logger.error(f"Failed to create {directory}")
            sys.exit(1)

    def generate_report(self):
        logger.log('DESC', '{0}数据收集{0}'.format('*' * 20))
        logger.log("STAGE", "分析结果数据、生成测试报告...")
        comments = {
            "测试时间": DT_STR,
            "测试命令": ' '.join(sys.argv),
            "测试描述": self.desc,
            "测试用例": self.case_id
        }
        FIOReportRunner(data_path=[self.output], output=self.output, comments=comments).run()


if __name__ == '__main__':
    pass
