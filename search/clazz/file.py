#!/usr/bin/python3


class File:
    name = ""
    path = ""
    fileType = ""
    dirPath = ""

    def __init__(self, name, path, type, dirPath):
        self.name = name
        self.path = path
        self.fileType = type
        self.dirPath = dirPath

    def getName(self):
        return self.name

    def getPath(self):
        return self.path

    def getFileType(self):
        return self.fileType

    def getDirPath(self):
        return self.dirPath
