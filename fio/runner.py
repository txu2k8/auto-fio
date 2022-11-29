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
from loguru import logger

from config import LOG_DIR, read_yaml
from fio.models import RWTypeEnum
from fio.loader import load_client, load_fio_result
from fio.command_generator import FIOCmdGen


class FIORunner(object):
    """FIO 执行引擎"""
    def __init__(self, testbed_yaml, bucket_prefix, bucket_num, obj_prefix, obj_num, obj_size, workers, clean):
        self.testbed_yaml = testbed_yaml
        self.bucket_prefix = bucket_prefix
        self.bucket_num = bucket_num
        self.obj_prefix = obj_prefix
        self.obj_num = obj_num
        self.obj_size = obj_size
        self.workers = workers
        self.clean = clean
        self.access_key = ""
        self.secret_key = ""
        self.endpoint_list = []
        self.driver_list = []
        self.clients = []
        self.nodes = []
        self.workload_xml_local_path = os.path.join(LOG_DIR, "workloads.xml")  # 本地workload xml文件

        self.parse_args()

    def parse_args(self):
        """解析参数，并做参数校验"""
        testbed_data = read_yaml(self.testbed_yaml)
        client_data = testbed_data["client"]
        client_data.sort(key=lambda x: x["ip"])
        self.clients = [load_client(d) for d in client_data]
        self.nodes = [load_node(n) for n in testbed_data["target"]["node"]]
        self.access_key = testbed_data["target"]["access_key"]
        self.secret_key = testbed_data["target"]["secret_key"]
        self.endpoint_list = testbed_data["target"]["endpoint"]
        self.driver_list = [f"driver{x}" for x in range(1, len(testbed_data["client"]) + 1)]

        # 校验workers参数是否正确
        min_workers = len(self.clients) * len(self.driver_list)
        if self.workers % min_workers != 0:
            raise Exception("workers需要是{}的倍数！".format(min_workers))

    def create_workload_xml(self, workload_type: WorkloadTypeEnum, r_ratio=None):
        """
        创建测试 workloads的xml配置文件
        :param workload_type:
        :param r_ratio: 读写混合时，读占比
        :return:
        """
        w_xml = WorkloadsXML(
            self.access_key, self.secret_key,
            self.endpoint_list, self.driver_list,
            self.bucket_prefix, self.bucket_num,
            self.obj_prefix, self.obj_num, self.obj_size
        )
        ws_list = [
            w_xml.workstage_init(self.workers),
            # w_xml.workstage_prepare(workers),
        ]
        workload_name = "{}节点_EC{}_{}水位_{}并发_{}_{}".format(
            len(self.nodes), "8+4", 0, self.workers, workload_type.value, self.obj_size
        )  # TODO
        if workload_type == WorkloadTypeEnum.read:
            ws_list.append(w_xml.workstage_read(self.workers, name=workload_name))
        elif workload_type == WorkloadTypeEnum.write:
            # ws_list.append(w_xml.workstage_write(self.workers, name=workload_name))
            ws_list.append(w_xml.workstage_prepare_write(self.workers, name=workload_name))
        elif workload_type == WorkloadTypeEnum.readwrite:
            ws_list.append(w_xml.workstage_read_write(self.workers, r_ratio=r_ratio, name=workload_name))
        else:
            raise Exception("不支持的workloads类型：{}，请传入：".format(workload_type.value))

        if self.clean:
            ws_list.append(w_xml.workstage_cleanup(self.workers))
            ws_list.append(w_xml.workstage_dispose(self.workers))
        w_xml.create_workload_xml(workload_name, ws_list, self.workload_xml_local_path)
        return workload_name

    def run(self, workload_type: WorkloadTypeEnum):
        # 创建workload xml
        w_name = self.create_workload_xml(workload_type)
        # return

        # 启动并配置 cosbench 服务
        start_cosbench(self.clients)

        # 启动 测试过程数据收集
        start_collect(self.nodes)

        # 提交测试、等等测试完成
        wid = submit_test(self.clients[0], self.workload_xml_local_path)

        # 停止 测试过程数据收集
        stop_collect(self.nodes)

        # 备份 测试过程数据
        backup_collect(self.nodes)

        # 备份 测试结果数据
        backup_cosbench_data(self.clients[0], wid, w_name)

    def generate_report(self):
        logger.info("分析结果数据、生成测试报告...")


if __name__ == '__main__':
    pass
