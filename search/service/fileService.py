#!/usr/bin/python3


import os

from search.model.file import File


def getFileFromFileName(filetypes, dirname, dirpath):
    nameSplit = dirpath.split(".")
    fileType = nameSplit[len(nameSplit) - 1]
    if len(filetypes) > 0 and fileType in filetypes:
        return File().build(dirpath, fileType, dirname)
    return 0


class FileService:
    files = []
    dirs = []
    fileTypes = []
    rootPath = ""

    def __init__(self, path, types):
        self.rootPath = path
        self.fileTypes = types
        self.files = []
        self.dirs = []

    # 累加上次查询结果
    def osWalkFiles(self):
        for dirpath, dirnames, filenames in os.walk(self.rootPath):
            for filename in filenames:
                file = getFileFromFileName(dirpath, filename)
                if file != 0:
                    self.files.append(file)

        return self.files

    def getFiles(self):
        return self.fileWalk(self.rootPath, self.dirs, self.files)

    # 查询结果
    def fileWalk(self, path, dirs, files):
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
                    self.fileWalk(folerpath, dirs, files)
                else:
                    dirname = os.path.dirname(folerpath)
                    file = getFileFromFileName(self.fileTypes, dirname, folder)
                    if file != 0:
                        files.append(file)
            except IOError as  ioError:
                print("文件读取失败：")
                print(ioError)
        return files
