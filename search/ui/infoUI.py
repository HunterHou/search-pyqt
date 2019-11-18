#!/usr/bin/python3
# encoding=utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.net.httpUitls import *


class InfoUI(QWidget):
    javMovie = None

    def __init__(self, javMovie):
        super(InfoUI, self).__init__()
        self.javMovie = javMovie
        self.infoInit()

    def infoInit(self):
        self.resize(850, 900)
        self.setWindowTitle(self.javMovie.code)

        self.layout = QGridLayout()
        cover = QLabel()
        try:
            path = self.javMovie.cover
            if path.find('http') >= 0:
                # 读取网络图片
                response = getResponse(path)
                if response.status == 200:
                    photo = QPixmap()
                    photo.loadFromData(response.read())
                    photo = photo.scaled(800, 500)
                    cover.setPixmap(photo)
            else:
                # 读取本地图片
                imgPath = self.javMovie.dirPath + path
                photo = QPixmap(imgPath)
                photo = photo.scaled(800, 500)
                cover.setPixmap(photo)
        except Exception as err:
            print(" InfoUI 读取图片失败:" + path)
            print(err)
        self.layout.addWidget(cover, 0, 0, 1, 5)

        self.layout.addWidget(QLabel("番号"), 1, 0, 1, 1)
        self.layout.addWidget(QLabel(self.javMovie.code), 1, 1, 1, 4)
        self.layout.addWidget(QLabel("标题"), 2, 0, 1, 1)
        title = QLabel(self.javMovie.title)
        title.setWordWrap(True)
        self.layout.addWidget(title, 2, 1, 1, 4)
        self.layout.addWidget(QLabel("演员"), 3, 0, 1, 1)
        self.layout.addWidget(QLabel(self.javMovie.getActress()), 3, 1, 1, 4)
        self.layout.addWidget(QLabel("制作商"), 4, 0, 1, 1)
        self.layout.addWidget(QLabel(self.javMovie.studio), 4, 1, 1, 4)
        self.layout.addWidget(QLabel("出品商"), 5, 0, 1, 1)
        self.layout.addWidget(QLabel(self.javMovie.maker), 5, 1, 1, 4)
        if len(self.javMovie.cutPic) > 0:
            for index in range(len(self.javMovie.cutPic)):
                cutPic = QLabel()
                try:
                    path = self.javMovie.cutPic[index]
                    # 读取网络图片
                    response = getResponse(path)
                    if response.status == 200:
                        curphoto = QPixmap()
                        curphoto.loadFromData(response.read())
                        curphoto = curphoto.scaled(800, 500)
                        cutPic.setPixmap(curphoto)
                except Exception as err:
                    print(" InfoUI 读取图片失败:" + path)
                    print(err)
                self.layout.addWidget(cutPic, 6 + index, 0, 1, 5)

        mainWidget = QWidget()
        scroll = QScrollArea()
        mainWidget.setLayout(self.layout)
        scroll.setWidget(mainWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)
