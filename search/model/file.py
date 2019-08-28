#!/usr/bin/python3

import os

from search.utils.timeUtil import *


def getPng(filename, end):
    filename = filename.replace(".mp4", end)
    filename = filename.replace(".wmv", end)
    filename = filename.replace(".mkv", end)
    filename = filename.replace(".avi", end)
    return filename


def getSuffix(filename):
    if filename is None:
        return ""
    arr = filename.split(".")
    if len(arr) <= 1:
        return arr[0]
    return arr[len(arr) - 1]


def getTitle(filename):
    if filename is None:
        return ""
    arr = filename.split(".")
    return arr[0]


def getSizeStr(path):
    result = ""
    fileSize = getSize(path)
    if fileSize <= 1024:
        result = str(int(fileSize))
    elif fileSize <= 1024 * 1024:
        result = str(int(fileSize / 1024)) + " k"
    elif fileSize <= 1024 * 1024 * 1024:
        result = str(int(fileSize / (1024 * 1024))) + " M"
    else:
        result = str(int(fileSize / (1024 * 1024))) + " M"
    return result


def getSize(path):
    size = 0
    try:
        size = os.path.getsize(path)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return size


def getCreateTime(path):
    creatTime = ""
    try:
        creatTime = os.path.getctime(path)
        creatTime = thisFormatTime(creatTime)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return creatTime


def getModifyTime(path):
    modifyTime = "0"
    try:
        modifyTime = os.path.getmtime(path)
        modifyTime = thisFormatTime(modifyTime)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return modifyTime


def getCode(fileName):
    code = None
    rights = fileName.split("[")
    if len(rights) <= 1:
        return code
    for index in range(len(rights)):
        if index == 0:
            continue
        right = rights[index]
        lefts = right.split("]")
        for left in lefts:
            if left.find("-") > 0:
                return left
    return code


def getActress(fileName):
    actress = ""
    rights = fileName.split("[")
    if len(rights) <= 1:
        return actress
    for index in range(len(rights)):
        if index == 0:
            continue
        right = rights[index]
        lefts = right.split("]")
        for left in lefts:
            if left.find("-") == 0:
                return left
    return actress


class File:
    # 名称
    name = None
    # 文件路径
    path = None
    # 番号
    code = None
    # 演员
    actress = None
    # 类型
    fileType = None
    # 文件夹路径
    dirPath = None
    size = None
    createTime = None
    modifyTime = None

    def __init__(self, filename, type, dirpath):
        self.name = filename
        self.code = getCode(filename)
        self.actress = getActress(filename)
        self.fileType = type
        self.dirPath = dirpath
        path = dirpath + "\\" + filename
        self.path = path
        self.size = getSizeStr(path)
        self.createTime = getCreateTime(path)
        self.modifyTime = getModifyTime(path)
