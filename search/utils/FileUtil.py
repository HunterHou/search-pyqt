#!/usr/bin/python3
import os

from search.utils.TimeUtil import thisFormatTime


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
