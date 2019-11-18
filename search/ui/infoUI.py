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
        self.resize(800, 900)
        self.setWindowTitle("详情")
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("番号"), 0, 0, 1, 1)
        layout.addWidget(QLabel(self.javMovie.code), 0, 1, 1, 1)
        layout.addWidget(QLabel("标题"), 1, 0, 1, 1)
        title = QLabel(self.javMovie.title)
        title.setWordWrap(True)
        layout.addWidget(title, 1, 1, 1, 1)
        layout.addWidget(QLabel("演员"), 2, 0, 1, 1)
        layout.addWidget(QLabel(self.javMovie.getActress()), 2, 1, 1, 1)
        layout.addWidget(QLabel("制作商"), 3, 0, 1, 1)
        layout.addWidget(QLabel(self.javMovie.studio), 3, 1, 1, 1)
        layout.addWidget(QLabel("出品商"), 4, 0, 1, 1)
        layout.addWidget(QLabel(self.javMovie.maker), 4, 1, 1, 1)
        layout.addWidget(QLabel(), 5, 0, 25, 4)
        cover = QLabel()
        try:
            path = self.javMovie.cover
            if path.find('http') >= 0:
                # 读取网络图片
                response = getResponse(path)
                if response.status == 200:
                    photo = QPixmap()
                    photo.loadFromData(response.read())
                    photo = photo.scaled(600, 400)
                    cover.setPixmap(photo)
            else:
                # 读取本地图片
                imgPath = self.javMovie.dirPath + path
                photo = QPixmap(imgPath)
                photo = photo.scaled(600, 400)
                cover.setPixmap(photo)
        except Exception as err:
            print(" InfoUI 读取图片失败:" + path)
            print(err)
        layout.addWidget(cover, 0, 3, 15, 4)
