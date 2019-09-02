#!/usr/bin/python
# encoding=utf-8

import os

curPath = os.path.realpath(os.curdir)
rootpath = curPath.replace(curPath.split("\\")[-1], "")
configPath = rootpath + "path.txt"
configs = []

with open(configPath, encoding='utf-8') as file:
    while True:
        key_value_str = file.readline()
        if key_value_str == "":
            break
        key_value = key_value_str.split("=")
        configs.append({"key": key_value[0], "value": key_value[1]})


def getPath():
    for conf in configs:
        if 'path' == conf.get("key"):
            return conf.get("value")
