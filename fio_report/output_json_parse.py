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

    @staticmethod
    def _filter_json_files(filename):
        """
        验证并筛选 fio json文件有效性
        :param filename:
        :return:
        """
        with open(filename, 'r') as candidate_file:
            try:
                candidate_json = json.load(candidate_file)
                if candidate_json["fio version"]:
                    return filename
                else:
                    logger.debug(f"无效的fio结果文件：{filename}，忽略！")
            except Exception as e:
                logger.warning(e)

    @staticmethod
    def _import_json_data(filename):
        """
        加载JSON文件，返回字典/列表
        :param filename:
        :return:
        """
        with open(filename) as json_data:
            try:
                d = json.load(json_data)
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
                item["rawdata"].append(self._import_json_data(f))
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

    def validate_job_options(self, dataset):
        """
        验证job options
        :param dataset:
        :return:
        """
        job_options_raw = ["jobs", 0, "job options"]
        try:
            self.walk_dictionary(dataset[0]['rawdata'][0], job_options_raw)
            self.validate_job_option_key(dataset[0]['rawdata'][0])
            return job_options_raw
        except KeyError:
            return ['global options']

    @staticmethod
    def validate_number_of_jobs(dataset):
        """
        验证 JSON文件中job数量，目前只支持 1 job
        :param dataset:
        :return:
        """
        length = len(dataset[0]['rawdata'][0]['jobs'])
        if length > 1:
            logger.error(f"\n 暂时不支持处理JSON文件中存在多个job：({length}) jobs\n")
            logger.info("See also: https://github.com/louwrentius/fio-plot/issues/64")
            sys.exit(1)

    def get_json_mapping(self, mode, dataset):
        """
        获取JSON文件中对应值的mapping路径
        :param mode:
        :param dataset:
        :return:
        """
        self.validate_number_of_jobs(dataset)
        root = ["jobs", 0]
        job_options = self.validate_job_options(dataset)
        data = root + [mode]
        dictionary = {
            "fio_version": ["fio version"],
            "jobname": (root + ["jobname"]),
            "iodepth": (job_options + ["iodepth"]),
            "numjobs": (job_options + ["numjobs"]),
            "bs": (job_options + ["bs"]),
            "rw": (job_options + ["rw"]),
            "bw": (data + ["bw"]),
            "bw_bytes": (data + ["bw_bytes"]),
            "iops": (data + ["iops"]),
            "iops_stddev": (data + ["iops_stddev"]),
            "lat_ns": (data + ["lat_ns", "mean"]),
            "lat_stddev": (data + ["lat_ns", "stddev"]),
            "latency_ms": (root + ["latency_ms"]),
            "latency_us": (root + ["latency_us"]),
            "latency_ns": (root + ["latency_ns"]),
            "cpu_usr": (root + ["usr_cpu"]),
            "cpu_sys": (root + ["sys_cpu"]),
        }

        return dictionary

    def get_flat_json_mapping(self, dataset):
        """
        获取 dataset 数据结构中所有JSON文件的元素值，保存到 dataset[idx]["data"]
        :param dataset:
        :return:
        """
        for item in dataset:
            item["data"] = []
            for record in item["rawdata"]:
                options = self.validate_job_options(dataset)
                self.settings.rw = self.get_nested_value(record, options + ["rw"])
                if self.settings.rw in ["rw", "readwrite", "randrw"]:
                    modes = self.settings.filter
                elif self.settings.rw in ["read", "write"]:
                    modes = [self.settings.rw]
                else:
                    modes = [self.get_nested_value(record, options + ["rw"])[4:]]

                m = self.get_json_mapping(self.settings.rw, dataset)
                row_dict = {
                    "jobname": self.get_nested_value(record, m["jobname"]),
                    "iodepth": int(self.get_nested_value(record, m["iodepth"])),
                    "numjobs": int(self.get_nested_value(record, m["numjobs"])),
                    "bs": self.get_nested_value(record, m["bs"]),
                    "rw": self.get_nested_value(record, m["rw"]),
                    "latency_ms": self.get_nested_value(record, m["latency_ms"]),
                    "latency_us": self.get_nested_value(record, m["latency_us"]),
                    "latency_ns": self.get_nested_value(record, m["latency_ns"]),
                    "cpu_sys": self.get_nested_value(record, m["cpu_sys"]),
                    "cpu_usr": self.get_nested_value(record, m["cpu_usr"]),
                    "fio_version": self.get_nested_value(record, m["fio_version"]),
                    "result": []
                }
                for mode in modes:
                    m = self.get_json_mapping(mode, dataset)
                    row = {
                        "type": mode,
                        "iops": round(self.get_nested_value(record, m["iops"]), 0),
                        "iops_stddev": self.get_nested_value(record, m["iops_stddev"]),
                        "lat": self.get_nested_value(record, m["lat_ns"]),
                        "lat_ms": round(self.get_nested_value(record, m["lat_ns"])/1000/1000, 2),
                        "lat_stddev": self.get_nested_value(record, m["lat_stddev"]),
                        "bw": self.get_nested_value(record, m["bw"]),
                        "bw_mb": round(self.get_nested_value(record, m["bw_bytes"])/1024/1024, 2),
                    }
                    row_dict["result"].append(row)
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
