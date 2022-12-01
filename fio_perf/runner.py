#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner
@time:2022/11/16
@email:tao.xu2008@outlook.com
@description: 
"""
import os
import sys
import time
import shutil
import itertools
from pathlib import Path
import subprocess
from loguru import logger
from numpy import linspace

from config import LOG_DIR
from fio_perf import default_settings
from fio_perf import display
from fio_perf.models import FIOSettings, FIOKwargs, RWTypeEnum


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
    time_str = "   [%s, 0:00:00]\n" % (sec_to_str(time.time() - start_t))
    sys.stdout.write("\r" + bar_str + time_str)
    sys.stdout.flush()


class FIORunner(object):
    """FIO 执行引擎"""

    def __init__(self, target, template, rw, iodepth, numjobs, bs, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.settings = FIOSettings(
            target=target,
            template=template,
            rw=rw,
            iodepth=iodepth,
            numjobs=numjobs,
            bs=bs,
            output=LOG_DIR,
        )
        # print(self.settings)

    @staticmethod
    def _exec(cmd):
        rc, output = subprocess.getstatusoutput(cmd)
        logger.debug(output.strip('\n'))
        return rc, output

    def is_fio_installed(self):
        command = "fio_perf"
        if shutil.which(command) is None:
            logger.error("Fio executable not found in path. Is Fio installed?")
            sys.exit(1)
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
        command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
        self._exec(command)

    @staticmethod
    def make_directory(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            logger.error(f"Failed to create {directory}")
            sys.exit(1)

    def generate_output_directory(self, test):
        if test["rw"] in self.settings.mixed:
            directory = (
                f"{self.settings.output}/{os.path.basename(test['target'])}/"
                f"{test['rw']}{test['rwmixread']}/{test['bs']}"
            )
        else:
            directory = f"{self.settings.output}/{os.path.basename(test['target'])}/{test['bs']}"

        if "run" in test.keys():
            directory = directory + f"/run-{test['run']}"

        return directory

    @staticmethod
    def check_encoding():
        try:
            print("\u3000")  # blank space
        except UnicodeEncodeError:
            logger.error("""
            It seems your default encoding is not UTF-8. This script requires UTF-8.
            You can change the default encoding with 'export PYTHONIOENCODING=UTF-8',
            """)
            exit(90)

    def check_settings(self):
        """
        检查配置 有效性
        :return:
        """
        if self.settings.type not in ["device", "rbd"] and not self.settings.size:
            logger.error("When the target is a file or directory, --size must be specified.")
            sys.exit(4)
        if self.settings.type == "directory":
            for item in self.settings.target:
                if not os.path.exists(item):
                    logger.error(f"The target directory ({item}) doesn't seem to exist.")
                    sys.exit(5)

        for mode in self.settings.rw:
            writemodes = ['write', 'randwrite', 'rw', 'readwrite', 'trimwrite']
            if mode in writemodes and not self.settings.destructive:
                logger.error(f"Mode {mode} will overwrite data on {self.settings.target} but destructive flag not set.")
                sys.exit(1)

            if mode in self.settings.mixed:
                if self.settings.rwmixread:
                    self.settings.loop_items.append("rwmixread")
                else:
                    logger.error("If a mixed (read/write) mode is specified, please specify --rwmixread")
                    sys.exit(8)
            else:
                self.settings.filter_items.append("rwmixread")

    def gather_settings(self):
        """
        聚合默认配置和用户自定义配置
        :return:
        """
        custom_settings = {}
        self.settings = {**self.settings, **custom_settings}
        self.check_settings()
        return

    def generate_test_list(self):
        """
        根据输入的参数列表，遍历生成待测试的条件组合
        :return:
        """
        loop_items = self.settings.loop_items
        dict_settings = dict(self.settings)
        dataset = []
        for item in loop_items:
            result = dict_settings[item]
            dataset.append(result)
        benchmark_list = list(itertools.product(*dataset))

        result = [dict(zip(loop_items, item)) for item in benchmark_list]
        self.settings.tests = result

    def check_target_type(self, target, filetype):
        """Validate path and file / directory type.
        It also returns the appropritate fio command line parameter based on the
        file type.
        """

        keys = ["file", "device", "directory", "rbd"]

        test = {keys[0]: Path.is_file, keys[1]: Path.is_block_device, keys[2]: Path.is_dir}

        parameter = {keys[0]: "--filename", keys[1]: "--filename", keys[2]: "--directory"}

        if not filetype == "rbd":

            if not os.path.exists(target):
                print(f"Benchmark target {filetype} {target} does not exist.")
                sys.exit(10)

            if filetype not in keys:
                print(f"Error, filetype {filetype} is an unknown option.")
                exit(123)

            check = test[filetype]

            path_target = Path(target)  # path library needs to operate on path object

            if check(path_target):
                return parameter[filetype]
            else:
                print(f"Target {filetype} {target} is not {filetype}.")
                sys.exit(10)
        else:
            return None

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

    def expand_command_line(self, command, test):
        if self.settings.size:
            command.append(f"--size={self.settings.size}")

        if self.settings.runtime and not self.settings.entire_device:
            command.append(f"--runtime={self.settings.runtime}")

        if self.settings.time_based:
            command.append("--time_based")

        if self.settings.rwmixread and test["rw"] in self.settings.mixed:
            command.append(f"--rwmixread={test['rwmixread']}")

        if self.settings.extra_opts:
            for option in self.settings.extra_opts:
                option = str(option)
                command.append("--" + option)

        if self.settings.ss:
            command.append(f"--steadystate={self.settings.ss}")
            if self.settings.ss_dur:
                command.append(f"--ss_dur={self.settings.ss_dur}")
            if self.settings.ss_ramp:
                command.append(f"--ss_ramp={self.settings.ss_ramp}")

        return command

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

    def run_test(self, test):
        """
        执行单项测试
        :param test: 待执行项参数
        :return:
        """

        output_directory = self.generate_output_directory(test)
        output_file = f"{output_directory}/{test['rw']}-{test['iodepth']}-{test['numjobs']}.json"

        command = [
            "fio",
            "--output-format=json",
            f"--output={output_file}",
        ]
        if self.settings.template:
            command.append(self.settings.template)
        logger.error(test)
        logger.warning(output_directory)
        command = self.expand_command_line(command, test)

        target_parameter = self.check_target_type(test["target"], self.settings.type)
        if target_parameter:
            command.append(f"{target_parameter}={test['target']}")

        if self.settings.dry_run:
            logger.warning(command)
            return

        self.make_directory(output_directory)
        return self._exec(command)

    def run(self):
        """
        执行测试，入口
        :return:
        """
        # 检查环境
        # self.is_fio_installed()
        # self.check_encoding()

        self.generate_test_list()
        display.display_header(self.settings)
        tests = self.settings.tests

        if self.settings.quiet:
            for test in tests:
                self.drop_caches()
                self.run_test(test)
        else:
            for test in progress_bar(tests):
                self.drop_caches()
                self.run_test(test)

    def generate_report(self):
        logger.info("分析结果数据、生成测试报告...")


if __name__ == '__main__':
    pass