#!/usr/bin/python3


import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from ..service.FileService import FileService
from ..const.FileConst import FileConst


class SearchDir(QMainWindow):
    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        self.initUI()

    # 定义全局变量
    fileList = []
    searchWord = ""
    rootPath = "G:\\emby\\emby-rename"
    # fileTypes = [FileConst.JPG, FileConst.GIF, FileConst.MP4, FileConst.TXT, FileConst.WMV, FileConst.XLSX]
    fileTypes = []

    # 填充数据

    def search(self, path):
        walk = FileService(path, self.fileTypes)
        self.fileList = []
        self.fileList = walk.getFiles()

    # 点击事件

    def clickPicture(self, event):
        item = self.dataGrid.currentItem()
        col = self.dataGrid.currentColumn()
        index = self.dataGrid.currentRow()

        if col == 1:
            filepath = self.fileList[index].getPath()
            # url = filepath.replace(".jpg", ".mp4")
            url = filepath
            cmd = '''start "" "''' + url + "\""
        if col == 2:
            url = self.fileList[index].getDirPath()
            cmd = '''start "" "''' + url + "\""

        os.system(cmd)

    def clickSearchButton(self):
        self.searchWord = self.dirName.text()
        self.statusBar().showMessage('执行中')
        replay = QMessageBox.question(self, '提示',
                                      self.searchWord, QMessageBox.Yes)
        if replay == QMessageBox.Yes:
            self.search(self.searchWord)
            self.initUI()
        self.statusBar().showMessage('执行完毕！！！')

    # 载入数据
    dataGrid = ""

    def loadData(self):
        if self.dataGrid == "":
            self.dataGrid = QTableWidget()
        data = self.dataGrid
        data.setRowCount(0)
        data.setColumnCount(0)
        if len(self.fileList) == 0:
            self.search(self.rootPath)
        data.setColumnCount(3)
        data.setRowCount(len(self.fileList))
        # 自适应列宽度
        # data.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data.setHorizontalHeaderLabels(['图片', '名称', "路径"])
        data.itemClicked.connect(self.clickPicture)
        data.setColumnWidth(0, 500)
        data.setColumnWidth(1, 130)
        data.setColumnWidth(2, 100)
        for index in range(len(self.fileList)):
            data.setRowHeight(index, 300)
            file = self.fileList[index]
            row_id = index
            row_name = QLabel()
            path = file.getPath().replace(".mp4", ".png")
            path = path.replace(".mp4", ".png")
            if not QPixmap(path).isNull():
                pic = QPixmap(path).scaled(500, 300)
                row_name.setPixmap(pic)
            file_name = QTableWidgetItem(file.getName())
            file_path = QTableWidgetItem(file.getPath())
            # file_type = QTableWidgetItem(file.getFileType())
            data.setCellWidget(row_id, 0, row_name)
            data.setItem(row_id, 1, file_name)
            data.setItem(row_id, 2, file_path)

        return data

    imageToggle = 1
    videoToggle = 1
    docsToggle = 1

    def imageChoose(self, state):
        if state == Qt.Checked:
            self.imageToggle = 1
            if FileConst.JPG not in self.fileTypes:
                self.fileTypes.append(FileConst.JPG)
            if FileConst.GIF not in self.fileTypes:
                self.fileTypes.append(FileConst.GIF)
        else:
            self.imageToggle = 0
            if FileConst.JPG in self.fileTypes:
                self.fileTypes.remove(FileConst.JPG)
            if FileConst.GIF in self.fileTypes:
                self.fileTypes.remove(FileConst.GIF)

    def videoChoose(self, state):
        if state == Qt.Checked:
            self.videoToggle = 1
            if FileConst.MP4 not in self.fileTypes:
                self.fileTypes.append(FileConst.MP4)
            if FileConst.WMV not in self.fileTypes:
                self.fileTypes.append(FileConst.WMV)

        else:
            self.videoToggle = 0
            if FileConst.MP4 in self.fileTypes:
                self.fileTypes.remove(FileConst.MP4)
            if FileConst.WMV in self.fileTypes:
                self.fileTypes.remove(FileConst.WMV)

    def docsChoose(self, state):
        if state == Qt.Checked:
            self.docsToggle = 1
            if FileConst.XLSX not in self.fileTypes:
                self.fileTypes.append(FileConst.XLSX)
            if FileConst.TXT not in self.fileTypes:
                self.fileTypes.append(FileConst.TXT)

        else:
            self.docsToggle = 0
            if FileConst.XLSX in self.fileTypes:
                self.fileTypes.remove(FileConst.XLSX)
            if FileConst.TXT in self.fileTypes:
                self.fileTypes.remove(FileConst.TXT)

    # 载入UI窗口
    dirName = ""

    def initUI(self):
        self.setWindowTitle("文件目录")
        self.resize(800, 900)
        # 创建搜索按钮
        if self.dirName == "":
            self.dirName = QLineEdit(self.searchWord)
        title = QLabel('请输入')
        okButton = QPushButton("搜索")
        okButton.clicked[bool].connect(self.clickSearchButton)
        # 复选框
        image = QCheckBox("图片", self)
        image.stateChanged.connect(self.imageChoose)
        video = QCheckBox("视频", self)
        video.stateChanged.connect(self.videoChoose)
        docs = QCheckBox("文档", self)
        docs.stateChanged.connect(self.docsChoose)
        if self.imageToggle == 1:
            image.toggle()
        if self.videoToggle == 1:
            video.toggle()
        if self.docsToggle == 1:
            docs.toggle()

        # 创建栅格布局
        headGrid = QGridLayout()
        headGrid.addWidget(title, 0, 0)
        headGrid.addWidget(self.dirName, 0, 1)
        headGrid.addWidget(okButton, 0, 2)
        headGrid.addWidget(image, 0, 3)
        headGrid.addWidget(video, 0, 4)
        headGrid.addWidget(docs, 0, 5)
        # loading
        headGrid.addWidget(self.loadData(), 1, 0, 2, 6)
        # 创建窗口挂件
        head_widget = QWidget()
        head_widget.setLayout(headGrid)
        # scroll = QScrollArea()
        # scroll.setWidget(headWidget)
        self.setCentralWidget(head_widget)

        self.show()
