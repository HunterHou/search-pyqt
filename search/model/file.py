#!/usr/bin/python3

from search.utils.fileUtil import *


def getCode(fileName):
    code = ""
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
    name = ""
    # 文件路径
    path = ""
    # 番号
    code = ""
    # 演员
    actress = ""
    # 类型
    fileType = ""
    # 文件夹路径
    dirPath = ""
    size = ""
    createTime = ""
    modifyTime = ""

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
