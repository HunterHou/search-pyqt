#!/usr/bin/python3
# encoding=utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from search.model.file import File


class InfoUI(QMainWindow):
    file = ""

    def __init__(self, file):
        super().__init__()
        self.file = file
        self.resize(800, 900)

        self.setWindowTitle("详情")
        self.show()
