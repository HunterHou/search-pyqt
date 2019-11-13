#!/usr/bin/python3

import operator
import os

from PyQt5.QtGui import QPixmap

from search.const.const import *
from search.net.httpUitls import getResponse
from search.utils.timeUtil import *


def writeNfo(path, filename, context):
    suffex = 'nfo'
    filepath = path + filename + "." + suffex
    ex = os.path.exists(filepath)
    if ex:
        filename = filename + "(1)"
        writeNfo(path, filename, context)
    else:
        writeFile(path, filename, suffex, context)


def writeFile(path, filename, suffex, context):
    filepath = path + "\\" + filename + "." + suffex
    with open(filepath, 'w', encoding="utf-8") as file:
        file.write(context)


def getPixMapFromNet(path, width, height):
    response = getResponse(path)
    photo = None
    if response.status == 200:
        photo = QPixmap()
        photo.loadFromData(response.read())
        photo = photo.scaled(width, height)
    return photo


def getPixMap(path, width, height):
    path = replaceSuffix(path, PNG)
    image = QPixmap(path)
    if image.isNull():
        path = path.replace(PNG, JPG)
        image = QPixmap(path)
    if image.isNull():
        imageArray = path.split(".")
        path = ""
        for index in range(len(imageArray)):
            if index == len(imageArray) - 1:
                path += "-poster.jpg"
            elif index == len(imageArray) - 2:
                path += imageArray[index]
            else:
                path += imageArray[index] + "."
        path = path.replace(PNG, JPG)
        image = QPixmap(path)
    if image.isNull():
        return None
    if width != '' and height != '':
        image = QPixmap(path).scaled(width, height)
    return image


def getReverse(sort):
    if sort == ASC:
        return False
    elif sort == DESC:
        return True


def getSortField(key):
    if key == CODE:
        return operator.attrgetter("code", 'size', 'modify_time')
    elif key == SIZE:
        return operator.attrgetter('size', "code", 'modify_time')
    elif key == MODIFY_TIME:
        return operator.attrgetter('modify_time', "code", 'size')


def replaceSuffix(filename, suffix):
    """修改文件类型，特指修改后缀"""
    if filename is None or filename == '':
        return filename
    arr = filename.split(".")
    if len(arr) > 1:
        last_suffix = arr[-1]
        filename = filename.replace(last_suffix, suffix)
    return filename


def getSuffix(filename):
    """获取文件后缀"""
    if filename is None:
        return ""
    arr = filename.split(".")
    if len(arr) <= 1:
        return arr[0]
    return arr[-1]


def getTitle(filename):
    """获取文件名"""
    if filename is None:
        return ""
    arr = filename.split(".")
    if len(arr) > 1:
        last_suffix = '.' + arr[-1]
        filename = filename.replace(last_suffix, '')
    return filename


def getSizeFromNumber(fileSize):
    if fileSize <= 1024:
        result = str(int(fileSize))
    elif fileSize <= 1024 * 1024:
        result = str(int(fileSize / 1024)) + " k"
    elif fileSize <= 1024 * 1024 * 1024:
        result = str(round(fileSize / (1024 * 1024), 2)) + " M"
    elif fileSize <= 1024 * 1024 * 1024 * 1024:
        result = str(round(fileSize / (1024 * 1024 * 1024), 2)) + " G"
    elif fileSize <= 1024 * 1024 * 1024 * 1024 * 1024:
        result = str(round(fileSize / (1024 * 1024 * 1024 * 1024), 2)) + " T"
    else:
        result = str(round(fileSize / (1024 * 1024 * 1024 * 1024), 2)) + " T"
    return result


def getSizeStr(path):
    """获取文件大小 可视化"""
    fileSize = getSize(path)
    return getSizeFromNumber(fileSize)


def getSize(path):
    """获取文件大小 单位 b"""
    size = 0
    try:
        size = os.path.getsize(path)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return size


def getCreateTime(path):
    """创建时间"""
    creatTime = ""
    try:
        creatTime = os.path.getctime(path)
        creatTime = thisFormatTime(creatTime)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return creatTime


def getModifyTime(path):
    """修改时间"""
    modify_time = "0"
    try:
        modify_time = os.path.getmtime(path)
        modify_time = thisFormatTime(modify_time)
    except IOError as ioError:
        print("读取失败：" + ioError)
    finally:
        return modify_time


def getCode(fileName):
    """根据 文件名称  分析番号 [] 中包含 '-'符号    """
    code = None
    rights = fileName.split("[")
    if len(rights) <= 1:
        return getTitle(fileName)
    for index in range(len(rights)):
        if index == 0:
            continue
        right = rights[index]
        lefts = right.split("]")
        for left in lefts:
            if left.find("-") > 0:
                return left
    return code


def getActress(filename):
    """根据 文件名称  分析演员 [] 中不包含 '-'符号    """
    actress = ""
    rights = filename.split("[")
    if len(rights) <= 1:
        return actress
    for index in range(len(rights)):
        right = rights[index]
        lefts = right.split("]")
        for left in lefts:
            if left.find("-") > 0 or left == '':
                continue
            return left
    return actress


class File:
    table_name = "file"

    def __init__(self):
        """变量定义到 init 方法中 可用反射获取所有变量"""
        # 名称
        self.name = ''
        # 文件路径
        self.path = ''
        # 番号
        self.code = ''
        # 演员
        self.actress = ''
        # 类型
        self.fileType = ''
        # 文件夹路径
        self.dirPath = ''
        # 大小
        self.size = ''
        self.sizeStr = ''
        # 创建时间
        self.create_time = ''
        # 修改时间
        self.modify_time = ''

    def build(self, filename, type, dirpath):
        """单独构造方法 方便用__init__ 建新对象"""
        self.name = filename
        self.code = getCode(filename)
        self.actress = getActress(filename)
        self.fileType = type
        self.dirPath = dirpath
        path = dirpath + "\\" + filename
        self.path = path
        self.size = getSize(path)
        self.sizeStr = getSizeStr(path)
        self.create_time = getCreateTime(path)
        self.modify_time = getModifyTime(path)
        return self

    def getMemberInfo(self):
        result = []
        for name, value in vars(self).items():
            result.append([name, value if value is not None else ""])
        return result


class JavMovie:
    table_name = "movie"

    def __init__(self):
        """变量定义到 init 方法中 可用反射获取所有变量"""
        self.code = ""
        self.title = ""
        # cover
        self.cover = ""
        # 海报
        self.poster = ""
        # 演员
        self.actresses = ""
        self.actressesUrl = ""
        # 系列
        self.series = ""
        # 制作商
        self.studio = ""
        # 发行商
        self.maker = ""
        # 时长
        self.length = ""
        # 发行日期
        self.pdate = ""
        self.director = ""
        self.dirPath = ""

    def build(self, code, title, cover, poster, actress, actressurl, director, pdate, series, studio, maker, length,
              dirpath):
        """单独构造方法 方便用__init__ 建新对象"""
        self.code = code
        self.title = title
        self.cover = cover
        self.poster = poster
        self.actresses = actress
        self.actressesUrl = actressurl
        self.director = director
        self.pdate = pdate
        self.series = series
        self.studio = studio
        self.maker = maker
        self.length = length
        self.dirPath = dirpath
        return self

    def getActress(self):
        if len(self.actresses) == 0:
            return 'null'
        actress = ','.join(self.actresses)
        return actress
