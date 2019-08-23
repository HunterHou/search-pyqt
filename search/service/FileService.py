#!/usr/bin/python3


import os

from ..clazz.file import File


class FileService:
    files = []
    fileTypes = []
    rootPath = ""

    def __init__(self, path, types):
        self.rootPath = path
        self.fileTypes = types

    def getFiles(self):
        for dirpath, dirnames, filenames in os.walk(self.rootPath):
            # print("路径："+dirpath)
            # for dirname in dirnames:
            #     print("文件夹："+dirname)
            for filename in filenames:
                nameSplit = filename.split(".")
                fileType = nameSplit[len(nameSplit) - 1]
                if len(self.fileTypes) > 0 and fileType in self.fileTypes:
                    filepath = dirpath + "\\" + filename
                    file = File(filename, filepath, fileType, dirpath)
                    self.files.append(file)

        return self.files
