#!/usr/bin/python3


import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.const.FileConst import FileConst
from search.service.FileService import FileService


class SearchDir(QMainWindow):
    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        self.initUI()

    # 定义全局变量
    fileList = []
    searchWord = ""
    rootPath = ""
    # fileTypes = [FileConst.JPG, FileConst.GIF, FileConst.MP4, FileConst.TXT, FileConst.WMV, FileConst.XLSX]
    fileTypes = []

    # 填充数据

    def search(self, path):
        walk = FileService(path, self.fileTypes)
        self.fileList = []
        self.fileList = walk.getFiles()

    # 点击事件
    command = ""

    def clickPicture(self, event):
        col = self.dataGrid.currentColumn()
        index = self.dataGrid.currentRow()
        if col == 1:
            filepath = self.fileList[index].path
            self.command = '''start "" "''' + filepath + "\""
        if col == 2:
            dirPath = self.fileList[index].dirPath
            self.command = '''start "" "''' + dirPath + "\""
        if self.command != "":
            os.system(self.command)
            self.command = ""

    def clickSearchButton(self):
        self.searchWord = self.dirName.text()
        self.statusBar().showMessage('执行中')
        # 提示框测试
        # replay = QMessageBox.question(self, '提示',
        #                               self.searchWord, QMessageBox.Yes)
        # if replay == QMessageBox.Yes:
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
        data.setColumnCount(6)
        data.setRowCount(len(self.fileList))
        # 自适应列宽度
        # data.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data.setHorizontalHeaderLabels(['图片', '名称', "路径", "大小", "创建时间", "修改时间"])
        data.itemClicked.connect(self.clickPicture)
        data.setColumnWidth(0, 200)
        data.setColumnWidth(1, 130)
        data.setColumnWidth(2, 100)
        for index in range(len(self.fileList)):
            data.setRowHeight(index, 300)
            file = self.fileList[index]
            row_id = index
            row_name = QLabel()
            path = file.path.replace(".mp4", ".png")
            path = path.replace(".wmv", ".png")
            if not QPixmap(path).isNull():
                pic = QPixmap(path).scaled(200, 300)
                row_name.setPixmap(pic)
            data.setCellWidget(row_id, 0, row_name)
            data.setItem(row_id, 1, QTableWidgetItem(file.name))
            data.setItem(row_id, 2, QTableWidgetItem(file.path))
            data.setItem(row_id, 3, QTableWidgetItem(file.size))
            data.setItem(row_id, 4, QTableWidgetItem(file.createTime))
            data.setItem(row_id, 5, QTableWidgetItem(file.modifyTime))

        return data

    imageToggle = 0
    videoToggle = 1
    docsToggle = 0

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
