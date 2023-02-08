#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:output_json_parse.py
@time:2022/12/04
@email:tao.xu2008@outlook.com
@description: 解析FIO json格式结果文件
"""
import os
import sys
import json
from loguru import logger

from fio_report.models import ReportSettings


class FIOJsonParse(object):
    """解析加载FIO JSON 文件"""

    def __init__(self, data_path):
        self.settings = ReportSettings(
            input_directory=data_path,
        )

    def _filter_json_files(self, filename):
        """
        验证并筛选 fio json文件有效性
        :param filename:
        :return:
        """
        d = self._loads_json_data(filename)
        if d["fio version"]:
            return filename
        else:
            logger.debug(f"无效的fio结果文件：{filename}，忽略！")

    @staticmethod
    def _loads_json_data(filename):
        """
        加载JSON文件，返回字典/列表
        :param filename:
        :return:
        """
        json_data = ""
        with open(filename) as f:
            json_start = False
            for line in f.readlines():
                if not json_start:
                    if "{" in line:
                        json_start = True
                        json_data += line
                    continue
                json_data += line

        try:
            d = json.loads(json_data)
        except json.decoder.JSONDecodeError:
            print(f"Failed to JSON parse {filename}")
            sys.exit(1)
        return d

    def list_json_files(self):
        """
        列表查询目录下符合条件的所有JSON文件
        :return:
        """
        # 获取目录下所有JSON文件
        input_directories = []
        for directory in self.settings.input_directory:
            absolute_dir = os.path.abspath(directory)
            print(absolute_dir)
            for dir_path, dir_names, file_names in os.walk(absolute_dir):
                input_dir_struct = {"directory": dir_path, "files": []}
                for file in file_names:
                    if file.endswith(".json"):
                        input_dir_struct["files"].append(os.path.join(dir_path, file))
                input_directories.append(input_dir_struct)

        # 筛选JSON文件，并排序
        dataset = []
        for directory in input_directories:
            file_list = []
            for file in directory["files"]:
                result = self._filter_json_files(file)
                if result:
                    file_list.append(result)

            directory["files"] = sorted(file_list)
            absolute_dir = os.path.abspath(str(directory))
            if not directory["files"]:
                logger.debug(f"\n没有找到匹配的JSON文件：{str(absolute_dir)}\n")
                continue
            dataset.append(directory)

        return dataset

    def import_json_dataset(self, dataset):
        """
        加载dataset中每个JSON文件，保存到rawdata中
        :param dataset:
        :return:
        """
        for item in dataset:
            item["rawdata"] = []
            for f in item["files"]:
                print(f)
                item["rawdata"].append(self._loads_json_data(f))
        return dataset

    @staticmethod
    def get_nested_value(dictionary, key):
        """
        获取JSON文件内容的嵌套内容
        :param dictionary:
        :param key:
        :return:
        """
        if not key:
            return None
        for item in key:
            dictionary = dictionary[item]
        return dictionary

    @staticmethod
    def walk_dictionary(dictionary, path):
        result = dictionary
        for item in path:
            result = result[item]
        return result

    @staticmethod
    def validate_job_option_key(dataset):
        mykeys = dataset['jobs'][0]['job options'].keys()
        if "iodepth" in mykeys:
            return True
        else:
            raise KeyError

    def get_job_options_mapping(self, record):
        """
        获取 job options映射
        :param record:
        :return:
        """
        return ["client_stats", 0, "job options"] if "client_stats" in record else ["jobs", 0, "job options"]

    def get_json_mapping(self, mode, record):
        """
        获取JSON文件中对应值的mapping路径
        :param mode: read|write
        :param record:
        :return:
        """

        root = ["jobs", 0]
        if "client_stats" in record:
            client_stats = record["client_stats"]
            len_client_stats = len(client_stats)
            if len_client_stats == 1:
                root = ['client_stats', 0]
            elif len_client_stats > 1:
                for idx, job in enumerate(client_stats):
                    if job["jobname"] == "All clients":
                        root = ['client_stats', idx]
                        break
                else:
                    raise Exception("未找到 All clients！")
            else:
                raise Exception("client_stats的job数为0！")

        job_options = self.get_job_options_mapping(record)
        data = root + [mode]
        dictionary = {
            "fio_version": ["fio version"],
            "jobname": (root + ["jobname"]),
            "iodepth": (job_options + ["iodepth"]),
            "numjobs": (job_options + ["numjobs"]),
            "bs": (job_options + ["bs"]),
            "rw": (job_options + ["rw"]),
            "size": (job_options + ["size"]),
            "runtime": (job_options + ["runtime"]),
            "ioengine": (job_options + ["ioengine"]),
            "direct": (job_options + ["direct"]),
            "bw": (data + ["bw"]),
            "bw_bytes": (data + ["bw_bytes"]),
            "iops": (data + ["iops"]),
            "iops_stddev": (data + ["iops_stddev"]),
            "slat_ns": (data + ["slat_ns", "mean"]),
            "clat_ns": (data + ["clat_ns", "mean"]),
            "lat_ns": (data + ["lat_ns", "mean"]),
            "lat_stddev": (data + ["lat_ns", "stddev"]),
            "latency_ms": (root + ["latency_ms"]),
            "latency_us": (root + ["latency_us"]),
            "latency_ns": (root + ["latency_ns"]),
            "cpu_usr": (root + ["usr_cpu"]),
            "cpu_sys": (root + ["sys_cpu"]),
        }

        return dictionary

    def get_json_options(self, record):
        """
        从"global options"、"job options"获取测试参数配置
        :param record: json数据记录
        :return:
        """
        options = {
            "jobname": "",
            "rw": "",
            "iodepth": "",
            "numjobs": "",
            "bs": "",
            "filesize": "",
            "runtime": "",
            "ioengine": "",
            "direct": "",
        }
        # 先查找"global options"中数据
        if "global options" in record:
            global_options = self.get_nested_value(record, ['global options'])
            options.update(global_options)
        # 再查找各个JOB中 job options
        job_options = self.get_nested_value(record, self.get_job_options_mapping(record))
        options.update(job_options)
        return options

    def get_json_result(self, record, rw):
        """
        从json的jobs中获取结果数据
        :param record:
        :param rw: 读写方式
        :return:
        """
        if rw in ["rw", "readwrite", "randrw"]:
            modes = ["read", "write"]
        elif rw in ["read", "write"]:
            modes = [rw]
        else:
            modes = [rw[4:]]

        # 获取结果（read、write除外）
        m = self.get_json_mapping(modes[0], record)
        row_dict = {
            "latency_ms": self.get_nested_value(record, m["latency_ms"]),
            "latency_us": self.get_nested_value(record, m["latency_us"]),
            "latency_ns": self.get_nested_value(record, m["latency_ns"]),
            "cpu_sys": self.get_nested_value(record, m["cpu_sys"]),
            "cpu_usr": self.get_nested_value(record, m["cpu_usr"]),
            "fio_version": self.get_nested_value(record, m["fio_version"]),
            "result": []
        }

        # 获取 read、write 结果
        result = []
        for mode in modes:
            m = self.get_json_mapping(mode, record)
            row = {
                "type": mode,
                "iops": round(self.get_nested_value(record, m["iops"]), 0),
                "iops_stddev": self.get_nested_value(record, m["iops_stddev"]),
                "slat": self.get_nested_value(record, m["slat_ns"]),
                "clat": self.get_nested_value(record, m["clat_ns"]),
                "lat": self.get_nested_value(record, m["lat_ns"]),
                "clat_ms": round(self.get_nested_value(record, m["clat_ns"]) / 1000 / 1000, 2),
                "lat_ms": round(self.get_nested_value(record, m["lat_ns"]) / 1000 / 1000, 2),
                "lat_stddev": self.get_nested_value(record, m["lat_stddev"]),
                "bw": self.get_nested_value(record, m["bw"]),
                "bw_mb": round(self.get_nested_value(record, m["bw_bytes"]) / 1024 / 1024, 2),
            }
            result.append(row)
        row_dict["result"] = result
        return row_dict

    def get_flat_json_mapping(self, dataset):
        """
        获取 dataset 数据结构中所有JSON文件的元素值，保存到 dataset[idx]["data"]
        :param dataset:
        :return:
        """
        for item in dataset:
            item["data"] = []
            for record in item["rawdata"]:
                all_options = self.get_json_options(record)
                row_dict = self.get_json_result(record, all_options["rw"])
                row_dict.update(all_options)
                item["data"].append(row_dict)
        return dataset

    def get_json_data(self):
        """
        获取FIO JSON数据
        :return:
        """
        list_of_json_files = self.list_json_files()
        # logger.debug(list_of_json_files)
        dataset = self.import_json_dataset(list_of_json_files)
        parsed_data = self.get_flat_json_mapping(dataset)
        # logger.debug(parsed_data)
        return parsed_data


if __name__ == '__main__':
    pass
