#!/usr/bin/python3
# encoding=utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class InfoUI(QWidget):
    javMovie = None

    def __init__(self, javMovie):
        super().__init__()
        self.javMovie = javMovie
        self.resize(800, 900)
        self.setWindowTitle("详情")
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("番号"), 0, 0, 1, 1)
        layout.addWidget(QLabel(javMovie.code), 0, 1, 1, 1)
        layout.addWidget(QLabel("标题"), 1, 0, 1, 1)
        title = QLabel(javMovie.title)
        title.setWordWrap(True)
        layout.addWidget(title, 1, 1, 1, 1)
        layout.addWidget(QLabel("演员"), 2, 0, 1, 1)
        layout.addWidget(QLabel(javMovie.getActress()), 2, 1, 1, 1)
        layout.addWidget(QLabel("制作商"), 3, 0, 1, 1)
        layout.addWidget(QLabel(javMovie.studio), 3, 1, 1, 1)
        layout.addWidget(QLabel("出品商"), 4, 0, 1, 1)
        layout.addWidget(QLabel(javMovie.maker), 4, 1, 1, 1)
        layout.addWidget(QLabel(), 5, 0, 25, 4)
        cover = QLabel()
        try:
            imgPath = javMovie.dirPath + javMovie.cover
            # coverImg = Image.open(imgPath)
            photo = QPixmap(imgPath)
            photo = photo.scaled(600, 400)
            cover.setPixmap(photo)
            # moviePath = imgPath.replace('.jpg', '.mp4')
            # movie = QMovie(moviePath)
            # movie.start()
            # cover.setMovie(movie)
        except Exception as err:
            print(err)
        layout.addWidget(cover, 0, 3, 15, 4)
