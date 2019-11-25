#!/usr/bin/python3


import logging
import os
from xml.dom.minidom import parse

from search.model.file import File, JavMovie

logger = logging.getLogger("search")


def readInfo(path):
    context = ""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            # file = open(path, 'r', encoding='utf-8')
            while True:
                string = file.readline()
                context += string
                if len(string) == 0:
                    break
        # file.close()
        return context
    except Exception as err:
        logger.error("readInfo" + str(err))
        return context


def buildFileFromFilename(filetypes, dirname, dirpath):
    name_array = dirpath.split(".")
    fileType = name_array[-1]
    if len(filetypes) > 0 and fileType in filetypes:
        return File().build(dirpath, fileType, dirname)
    return 0


class FileService:
    files = []
    dirs = []
    names = []
    actress = []
    fileTypes = []
    rootPath = ""

    def __init__(self):
        pass

    def build(self, path, types):
        self.rootPath = path
        self.fileTypes = types
        self.files = []
        self.dirs = []
        return self

    def getFiles(self, files, names, actress):
        '''获取文件列表，前提必须先 build '''
        return self.fileWalk(self.rootPath, self.dirs, files, names, actress)

    def osWalkFiles(self):
        '''累加上次查询结果'''
        for dirpath, dirnames, filenames in os.walk(self.rootPath):
            for filename in filenames:
                file = buildFileFromFilename(dirpath, filename)
                if file != 0:
                    self.files.append(file)

        return self.files

    # 查询结果
    def fileWalk(self, path, dirs, files, names, actresses):
        if not path:
            return self.files
        listFolder = os.listdir(path)
        for folder in listFolder:

            folerpath = path + "\\" + folder

            try:
                if not os.access(folerpath, os.R_OK):
                    continue
                if os.path.isdir(folerpath):
                    dirs.append(folerpath)
                    self.fileWalk(folerpath, dirs, files, names, actresses)
                else:
                    dirname = os.path.dirname(folerpath)
                    file = buildFileFromFilename(self.fileTypes, dirname, folder)
                    if file != 0:
                        files.append(file)
                        actressname = file.actress
                        if actressname is not None:
                            actressname = actressname.strip()
                            if actressname == '':
                                actressname = '未知'
                        if actressname in names and actressname:
                            names[actressname] = int(names[actressname]) + 1
                        else:
                            names[actressname] = 1
                            actresses[actressname] = (actressname, file.path, file.modify_time)
                            # actresses.append((actressname, file.path, file.modify_time))
            except IOError as  ioError:
                logger.error("文件读取失败" + str(ioError))
        return files, actresses


def getElementsByTagName(collect, name):
    try:
        return collect.getElementsByTagName(name)[0].childNodes[0].data
    except Exception as err:
        # logger.info(name + "获取失败:" + str(err))
        return ''


def nfoToJavMovie(path):
    if path is None or path == '' or not os.path.exists(path):
        return None
    arr = path.split("\\")
    dirpath = path.replace(arr[len(arr) - 1], "")
    domTree = parse(path)
    collect = domTree.documentElement
    title = getElementsByTagName(collect, 'title')
    code = getElementsByTagName(collect, 'num')
    cover = getElementsByTagName(collect, 'fanart')
    poster = getElementsByTagName(collect, 'poster')
    director = getElementsByTagName(collect, 'director')
    pdate = getElementsByTagName(collect, 'release')
    series = getElementsByTagName(collect, 'plot')
    studio = getElementsByTagName(collect, 'studio')
    maker = getElementsByTagName(collect, 'maker')
    length = getElementsByTagName(collect, 'runtime')

    actresses = []
    actors = collect.getElementsByTagName('name')
    for actor in actors:
        if len(actor.childNodes) > 0:
            actress = actor.childNodes[0].data
            actresses.append(actress)
    return JavMovie().build(code, title, cover, poster, actresses, "", director, pdate, series, studio, maker,
                            length, dirpath, [])
