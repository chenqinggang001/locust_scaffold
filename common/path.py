#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
common_path = os.path.abspath(__file__)
# print(common_path)

# common 目录
common_dir = os.path.dirname(common_path)
# print(common_dir)

# 项目根路径
root_dir = os.path.dirname(common_dir)
# print(root_dir)

# log路径
log_path = os.path.join(root_dir, 'log')
if not os.path.exists(log_path):
    os.mkdir(log_path)

# 测试数据路径
testdata_path = os.path.join(root_dir, 'testdata')
if not os.path.exists(testdata_path):
    os.mkdir(testdata_path)

# 报告路径
reports_path = os.path.join(root_dir, 'reports')
if not os.path.exists(reports_path):
    os.mkdir(reports_path)

testapidata_path = os.path.join(testdata_path, 'testapidata')
testapidata_filter_path = os.path.join(testapidata_path, 'filter')
testapidata_recoder_path = os.path.join(testapidata_path, 'recoder')

# index_page_api = os.path.join(testapidata_path, "index.json")
