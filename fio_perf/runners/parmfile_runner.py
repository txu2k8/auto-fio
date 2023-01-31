#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner_parmfile
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
from fio_perf.models import FIOParmFiles
from fio_perf.runners.base import FIOBaseRunner


class FIOParmFileRunner(FIOBaseRunner):
    """FIO 执行引擎 - 传入配置文件/目录，遍历执行"""

    def __init__(self, client, parmfile, *args, **kwargs):
        super(FIOParmFileRunner, self).__init__(args, kwargs)
        self.parameters = FIOParmFiles(
            client=client,
            parmfile=parmfile,
            output=self.output,
            dry_run=self.dry_run,
            quiet=self.quiet,
        )

    def run(self):
        # TODO
        return


if __name__ == '__main__':
    pass
