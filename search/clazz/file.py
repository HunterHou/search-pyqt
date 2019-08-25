#!/usr/bin/python3

import datetime
import os

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

    def __init__(self, filename, path, type, dirpath):
        self.name = filename
        self.fileType = type
        self.dirPath = dirpath

        self.path = dirpath + "\\" + filename
        fileSize = os.path.getsize(path)
        # self.size = os.path.getsize(path)
        # self.createTime = getFormatTime(os.path.getctime(path))
        # self.modifyTime = getFormatTime(os.path.getmtime(path))

    def getSizeStr(self, fileSize):
        result = ""
        if fileSize <= 1024:
            result = str(int(fileSize))
        elif fileSize <= 1024 * 1024:
            result = str(int(fileSize / 1024)) + " k"
        elif fileSize <= 1024 * 1024 * 1024:
            result = str(int(fileSize / (1024 * 1024))) + " M"
        else:
            result = str(fileSize / (1024 * 1024)) + " M"
        return result

    def getFormatTime(self, longTime):
        return datetime.datetime.fromtimestamp(longTime)
