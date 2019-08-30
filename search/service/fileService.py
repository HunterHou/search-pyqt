#!/usr/bin/python3


import os
from xml.dom.minidom import parse

from search.model.file import File, JavMovie


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
        print(err)
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

    def getFiles(self):
        '''获取文件列表，前提必须先 build '''
        return self.fileWalk(self.rootPath, self.dirs, self.files)

    def osWalkFiles(self):
        '''累加上次查询结果'''
        for dirpath, dirnames, filenames in os.walk(self.rootPath):
            for filename in filenames:
                file = buildFileFromFilename(dirpath, filename)
                if file != 0:
                    self.files.append(file)

        return self.files

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
                    file = buildFileFromFilename(self.fileTypes, dirname, folder)
                    if file != 0:
                        files.append(file)
            except IOError as  ioError:
                print("文件读取失败：")
                print(ioError)
        return files


def nfoToJavMovie(path):
    if path is None or path == '' or not os.path.exists(path):
        return None
    arr = path.split("\\")
    dirpath = path.replace(arr[len(arr) - 1], "")
    domTree = parse(path)
    collect = domTree.documentElement
    title = collect.getElementsByTagName('title')[0].childNodes[0].data
    code = collect.getElementsByTagName('num')[0].childNodes[0].data
    cover = collect.getElementsByTagName('fanart')[0].childNodes[0].data
    poster = collect.getElementsByTagName('poster')[0].childNodes[0].data
    director = collect.getElementsByTagName('director')[0].childNodes[0].data
    pdate = collect.getElementsByTagName('release')[0].childNodes[0].data
    series = collect.getElementsByTagName('plot')[0].childNodes[0].data
    studio = collect.getElementsByTagName('studio')[0].childNodes[0].data
    maker = collect.getElementsByTagName('maker')[0].childNodes[0].data
    length = collect.getElementsByTagName('runtime')[0].childNodes[0].data

    actresses = []
    actors = collect.getElementsByTagName('name')
    for actor in actors:
        actress = actor.childNodes[0].data
        actresses.append(actress)
    return JavMovie().build(code, title, cover, poster, actresses, director, pdate, series, studio, maker,
                            length, dirpath)
    # BeautifulSoup 模式 读取xml 但是要求安装 pip install lxml
    # nfoXML = readInfo(path)
    # xmlBs = BeautifulSoup(nfoXML, 'xml')
    # title = xmlBs.find('title').get_text()
    # code = xmlBs.find('num').get_text()
    # cover = xmlBs.find('fanart').get_text()
    # poster = xmlBs.find('poster').get_text()
    # director = xmlBs.find('director').get_text()
    # pdate = xmlBs.find('premiered').get_text()
    # series = xmlBs.find('premiered').get_text()
    # studio = xmlBs.find('studio').get_text()
    # maker = xmlBs.find('maker').get_text()
    # length = xmlBs.find('runtime').get_text()
    # actresses = []
    # actors = xmlBs.find_all('name')
    # for actor in actors:
    #     actresses.append(actor.get_text())
    #
    # return JavMovie().build(code, title, cover, poster, actresses, director, pdate, series, studio, maker,
    #                         length)

# info = 'E:\emby\高橋しょう子\Moodyz\[MIDE-670] 【元年キャンペーン】彼女が四日間、旅行で留守の間、彼女のグラドルお姉さんとハメまくったドエロ純愛記録。 [高橋しょう子]\\[MIDE-670] 【元年キャンペーン】彼女が四日間、旅行で留守の間、彼女のグラドルお姉さんとハメまくったドエロ純愛記録。 [高橋しょう子].nfo'
# print(nfoToJavMovie(info))
