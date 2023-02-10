#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import queue

from common.path import testdata_path


def read_text_on_quqe(parent_path, file_name):
    users_file = os.path.join(testdata_path, parent_path)
    users_file = os.path.join(users_file, file_name)
    with open(file=users_file, mode='r+', encoding='utf-8') as f:
        # 创建一个队列
        s = queue.Queue()
        while True:
            if line := f.readline().strip("\n"):
                s.put_nowait(line)
            else:
                break
        return s


def read_text_line(parent_path: str, file_path: str):
    users_file = os.path.join(testdata_path, parent_path)
    users_file = os.path.join(users_file, file_path)
    s = []
    with open(file=users_file, mode='r+', encoding='utf-8') as f:
        while True:
            if line := f.readline().strip("\n"):
                s.append(line)
            else:
                break
    return s
