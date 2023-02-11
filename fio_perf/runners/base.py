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
import time
import subprocess
from loguru import logger
from numpy import linspace

from config import DT_STR
from fio_report.runner import FIOReportRunner
from fio_report.output_json_parse import get_json_file_content


def progress_bar(iter_obj):
    """https://stackoverflow.com/questions/3160699/python-progress-bar/49234284#49234284"""

    def sec_to_str(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    len_iter_obj = len(iter_obj)
    steps = {
        int(x): y
        for x, y in zip(
            linspace(0, len_iter_obj, min(100, len_iter_obj), endpoint=False),
            linspace(0, 100, min(100, len_iter_obj), endpoint=False),
        )
    }
    # quarter and half block chars
    q_steps = ["", "\u258E", "\u258C", "\u258A"]
    start_t = time.time()
    time_str = "   [0:00:00, -:--:--]"
    activity = [" -", " \\", " |", " /"]
    for nn, item in enumerate(iter_obj):
        bar_str = ""
        if nn in steps:
            done = "\u2588" * int(steps[nn] / 4.0) + q_steps[int(steps[nn] % 4)]
            todo = " " * (25 - len(done))
            bar_str = "%4d%% |%s%s|" % (steps[nn], done, todo)
        if nn > 0:
            end_t = time.time()
            time_str = " [%s, %s]" % (
                sec_to_str(end_t - start_t),
                sec_to_str((end_t - start_t) * (len_iter_obj / float(nn) - 1)),
            )
        sys.stdout.write("\r" + bar_str + activity[nn % 4] + time_str)
        sys.stdout.flush()
        yield item
    bar_str = "%4d%% |%s|" % (100, "\u2588" * 25)
    time_str = "   [%s, 0:00:00]\n\n" % (sec_to_str(time.time() - start_t))
    sys.stdout.write("\r" + bar_str + time_str)
    sys.stdout.flush()


def parse_fio_parmfile(parmfile):
    """
    解析FIO配置文件
    :param parmfile:
    :return:
    """
    test_parameter = {"f_path": parmfile, "desc": parmfile}
    with open(parmfile, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if not line:
                continue
            if line.startswith('['):
                if "global" not in line:
                    test_parameter['desc'] = line.strip('[').strip(']')
            else:
                kv = line.split('=')
                if len(kv) == 1:
                    test_parameter[kv[0].strip()] = ''
                elif len(kv) == 2:
                    test_parameter[kv[0].strip()] = kv[1].strip()
                else:
                    raise Exception(f"参数错误! {line}")
    test_parameter["target"] = test_parameter["directory"] if "directory" in test_parameter else ""
    return test_parameter


class FIOBaseRunner(object):
    """FIO 执行引擎 - base"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.case_id = kwargs["case_id"] if "case_id" in kwargs else ""
        self.desc = kwargs["desc"] if "desc" in kwargs else ""
        self.output = os.path.abspath(kwargs["output"]) if "output" in kwargs else "./"
        self.report = kwargs["report"] if "report" in kwargs else True
        self.drop_caches = kwargs["drop_caches"] if "drop_caches" in kwargs else True
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

    def exec_drop_caches(self):
        logger.info("删除缓存...")
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

    def generate_test_list(self):
        """
        生成待测试项，基础类具体实现
        :return:
        """
        return []

    def generate_output_directory(self, test):
        directory = os.path.join(self.output, os.path.basename(test['target']), test['bs'])
        if "rwmixread" in test:
            directory = os.path.join(directory, f"{test['rw']}{test['rwmixread']}")
        else:
            directory = os.path.join(directory, f"{test['rw']}")

        self.make_directory(directory)
        return directory

    @staticmethod
    def generate_output_filename(test):
        if "name" in test:
            return test["name"]
        test_name = os.path.basename(test["f_path"]) if "f_path" in test else ""
        try:
            if "rwmixread" in test:
                test_name = f"{test['bs']}_{test['rw']}{test['rwmixread']}_{test['iodepth']}_{test['numjobs']}"
            else:
                test_name = f"{test['bs']}_{test['rw']}_{test['iodepth']}_{test['numjobs']}"
        except Exception as e:
            logger.warning(e)
        return test_name

    def generate_fio_command(self, test):
        """
        生成FIO执行命令，继承类具体实现
        :param test:
        :return:
        """
        return []

    def run_test(self, test, idx):
        """
        执行单项测试
        :param test: 待执行项参数
        :param idx: 待执行项 序号
        :return:
        """
        logger.log("STAGE", f"执行FIO测试{idx+1}：{test['desc']}")
        if self.drop_caches:
            self.exec_drop_caches()  # 清理缓存

        output_directory = self.generate_output_directory(test)
        test_name = self.generate_output_filename(test)
        output_file = os.path.join(output_directory, f"{test_name}.json")
        test["name"] = test_name
        test["output"] = output_file

        command = self.generate_fio_command(test)
        command_str = str(" ".join(command))
        if self.dry_run:
            logger.log("DESC", command_str)
            return

        rc, output = self._exec(command_str)
        logger.info(output)
        _, none_json_str = get_json_file_content(test["output"])
        logger.warning(none_json_str)
        return

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

    def run(self):
        """
        执行测试，入口
        :return:
        """
        # 检查环境
        self.is_fio_installed()
        tests = self.generate_test_list()

        if self.quiet:
            for idx, test in enumerate(tests):
                self.run_test(test, idx)
        else:
            for idx, test in enumerate(progress_bar(tests)):
                self.run_test(test, idx)

        if not self.dry_run and self.report:
            self.generate_report()


if __name__ == '__main__':
    pass
