#!/usr/bin/python3
# encoding=utf-8

from PyQt5.QtWidgets import *


class InfoUI(QWidget):
    file = None

    def __init__(self, file):
        super().__init__()
        self.file = file
        self.resize(800, 900)
        self.setWindowTitle("详情")
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("番号"), 0, 0, 1, 1)
        layout.addWidget(QLabel(file.code), 0, 0, 1, 1)
        layout.addWidget(QLabel("标题"), 0, 0, 1, 1)
        layout.addWidget(QLabel("演员"), 0, 0, 1, 1)
        layout.addWidget(QLabel("制作商"), 0, 0, 1, 1)
        layout.addWidget(QLabel("出品商"), 0, 0, 1, 1)
