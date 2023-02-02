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

from config import ConfigIni
from fio_perf.models import FIOParmFiles
from fio_perf.display import display_parmfile
from fio_perf.runners.base import FIOBaseRunner, progress_bar, parse_fio_parmfile


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

    def get_fio_parmfiles(self):
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

    def parse_fio_parmfile1(self, parmfile):
        """
        解析fio parmfile配置文件
        :param parmfile:配置文件全路径
        :return:
        """
        cf = ConfigIni(parmfile)
        sections = cf.sections
        if len(sections) < 2:
            raise Exception(f"FIO配置文件参数错误：{parmfile}")
        test_parameter = {"path": parmfile}
        for section in sections:
            test_parameter.update(cf.get_kvs(section))
            if section not in ["global", "GLOBAL"]:
                test_parameter["desc"] = section
        test_parameter["target"] = test_parameter["directory"] if "directory" in test_parameter else ""
        return test_parameter

    def generate_test_list(self):
        """
        根据输入的parmfile，遍历所有fio配置文件，生成测试项
        :return:
        """
        logger.log("STAGE", "遍历fio配置文件生成待测试项...")
        parmfiles = self.get_fio_parmfiles()
        for parmfile in parmfiles:
            test = parse_fio_parmfile(parmfile)
            self.parameters.tests.append(test)
            self.parameters.estimated_duration += int(test["runtime"]) if "runtime" in test else 0

    def generate_output_directory(self, test):
        if test["rw"] in self.parameters.mixed:
            directory = os.path.join(
                self.parameters.output, os.path.basename(test['target']), f"{test['rw']}{test['rwmixread']}", test['bs']
            )
        else:
            directory = os.path.join(self.parameters.output, os.path.basename(test['target']), test['bs'])

        return directory

    def generate_output_filename(self, test):
        if "name" in test:
            return test["name"]
        test_name = os.path.basename(test["path"])
        try:
            if test["rw"] in self.parameters.mixed:
                test_name = f"{test['rw']}{test['rwmixread']}_{test['bs']}_{test['iodepth']}_{test['numjobs']}"
            else:
                test_name = f"{test['rw']}_{test['bs']}_{test['iodepth']}_{test['numjobs']}"
        except Exception as e:
            logger.warning(e)
        return test_name

    def run_test(self, test, idx):
        """
        执行单项测试
        :param test: 待执行项参数
        :param idx: 待执行项 序号
        :return:
        """
        logger.log("STAGE", f"执行FIO测试{idx+1}：{test['desc']}")
        if self.parameters.drop_caches:
            self.drop_caches()  # 清理缓存
        output_directory = self.generate_output_directory(test)
        test_name = self.generate_output_filename(test)
        output_file = os.path.join(output_directory, f"{test_name}.json")

        command = ["fio"]
        if self.parameters.client:
            command.append(f"--client={self.parameters.client}")
        command.extend(
            [
                test["path"],
                "--output-format=json",
                f"--output={output_file}"
            ]
        )
        command_str = str(" ".join(command))

        if self.parameters.dry_run:
            logger.log("DESC", command_str)
            return

        self.make_directory(output_directory)
        rc, output = self._exec(command_str)
        logger.info(output)
        return

    def run(self):
        """
        配置文件执行测试，入口
        :return:
        """
        # 检查环境
        # self.is_fio_installed()
        self.generate_test_list()
        display_parmfile(self.parameters)
        tests = self.parameters.tests

        if self.parameters.quiet:
            for idx, test in enumerate(tests):
                self.run_test(test, idx)
        else:
            for idx, test in enumerate(progress_bar(tests)):
                self.run_test(test, idx)

        if not self.dry_run and self.report:
            self.generate_report()


if __name__ == '__main__':
    pass
