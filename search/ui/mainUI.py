#!/usr/bin/python3


from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.const.FileConst import FileConst
from search.model.file import *
from search.net.javTool import JavTool, getResponse
from search.service.fileService import FileService


class MainUI(QMainWindow):
    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        self.tableData = QTableWidget()
        self.gridData = QWidget()
        self.infoLayout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        self.codeInput = QLineEdit()
        self.titleInput = QTextEdit()
        self.actressInput = QLineEdit()
        self.initUI()

    # 定义全局变量
    dataList = []
    rootPath = "E:/"
    fileTypes = []
    # 载入数据
    tableData = None
    isTableData = 1
    isGridData = 0
    gridData = None
    gridLayout = None
    codeInput = None
    titleInput = None
    actressInput = None
    curCode = None
    curActress = None
    curFilePath = None
    curDirPath = None
    curTitle = None
    # 默认勾选
    imageToggle = 0
    videoToggle = 1
    docsToggle = 0

    # 搜索文本框
    dirName = None

    # 载入UI窗口
    def initUI(self):
        self.setWindowTitle("文件目录")
        self.resize(1400, 900)
        # 创建搜索按钮
        if self.dirName is None:
            self.dirName = QLineEdit()
        openFolder = QPushButton("点我")
        openFolder.clicked[bool].connect(self.openPath)
        okButton = QPushButton("搜索")
        okButton.clicked[bool].connect(self.clickSearchButton)

        openFile = QPushButton("打开文件")
        openFile.clicked[bool].connect(self.openFile)
        openDir = QPushButton("打开文件夹")
        openDir.clicked[bool].connect(self.openFile)
        codeSearch = QPushButton("番号搜索")
        codeSearch.clicked[bool].connect(self.codeSearch)

        syncJav = QPushButton("数据同步")
        syncJav.clicked[bool].connect(self.syncJav)

        # 单选框
        grid_layout = QRadioButton("网格", )
        if self.isGridData == 1:
            grid_layout.toggle()
        table_layout = QRadioButton("表格")
        if self.isTableData == 1:
            table_layout.toggle()
        grid_layout.clicked[bool].connect(self.chooseLayout)
        table_layout.clicked[bool].connect(self.chooseLayout)
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
        # 创建左侧组件
        left_widget = QWidget()
        left_layout = QGridLayout()
        left_layout.addWidget(grid_layout, 0, 0)
        left_layout.addWidget(table_layout, 0, 1)
        left_layout.addWidget(image, 1, 0)
        left_layout.addWidget(video, 1, 1)
        left_layout.addWidget(docs, 1, 2)

        left_layout.addWidget(openFolder, 2, 0, 1, 1)
        left_layout.addWidget(self.dirName, 2, 1, 1, 2)

        left_layout.addWidget(okButton, 3, 2, 1, 1)
        # left_layout.addWidget(QLabel(""), 4, 0, 3, 3)
        left_layout.addWidget(codeSearch, 4, 2, 1, 1)
        left_layout.addWidget(QLabel("番号"), 5, 0, 1, 1)
        left_layout.addWidget(self.codeInput, 5, 1, 1, 2)

        left_layout.addWidget(QLabel("标题"), 6, 0, 1, 1)
        self.titleInput.setMaximumHeight(60)
        self.titleInput.setMaximumWidth(160)
        left_layout.addWidget(self.titleInput, 6, 1, 2, 2)
        left_layout.addWidget(QLabel("演员"), 8, 0, 1, 1)
        left_layout.addWidget(self.actressInput, 8, 1, 1, 2)
        self.curPic = QLabel()
        left_layout.addWidget(self.curPic, 9, 0, 15, 3)
        left_layout.addWidget(openFile)
        left_layout.addWidget(openDir)
        left_layout.addWidget(syncJav)

        # 创建右侧组件
        right_widget = QWidget()
        right_layout = QGridLayout()

        # loading 选择表格布局 还是 网格布局
        right_layout.addWidget(self.loadTableData(), 0, 0, 1, 1)
        scroll = QScrollArea()
        scroll.setWidget(self.loadGridData())
        right_layout.addWidget(scroll, 1, 0, 1, 1)
        if self.isTableData == 1:
            self.loadTableData().setMaximumHeight(900)
            scroll.setMaximumHeight(0)
        elif self.isGridData == 1:
            self.loadTableData().setMaximumHeight(0)
            scroll.setMaximumHeight(900)

        # 创建主窗口组件 挂载布局
        main_widget = QWidget()
        main_layout = QGridLayout()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 0, 1, 1, 16)
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 0, 0, 1, 1)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        bar = self.menuBar()
        file = bar.addMenu("文件")
        file.setShortcutEnabled(1)
        qu = QAction("退出", self)
        qu.setShortcut("q")
        file.addAction(qu)
        file.triggered[QAction].connect(self.fileMenuProcess)
        self.show()

    def syncJav(self):
        tool = JavTool("https://www.cdnbus.in/")
        code = self.codeInput.text()
        movie = tool.getJavInfo(code)
        if movie is None:
            QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
        tool.makeAcctress(self.curDirPath, movie)
        if tool.dirpath is not None and tool.fileName is not None:
            os.rename(self.curFilePath, tool.dirpath + "\\" + tool.fileName + getSuffix(self.curFilePath))
        # shutil.move(, )
        QMessageBox().about(self, "提示", "同步成功!!!")

    def codeSearch(self):
        tool = JavTool("https://www.cdnbus.in/")
        code = self.codeInput.text()
        movie = tool.getJavInfo(code)
        if movie is None:
            QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
        else:
            self.curCode = code
            self.curActress = movie.getActress()
            self.curFilePath = movie.image
            # self.curDirPath = targetfile.dirPath
            self.curTitle = movie.title
            self.infoToLeft()

    def loadGridData(self):

        gridData = self.gridData
        if len(self.dataList) == 0:
            # self.search("G:/emby/emby-rename")
            return gridData
        gridLayout = self.gridLayout
        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().deleteLater()
        for index in range(len(self.dataList)):
            data = self.dataList[index]
            item = QToolButton()
            item.setText(str(index))
            item.setIcon(QIcon(getPng(data.path, '.png')))
            item.setIconSize(QSize(200, 300))
            item.setToolButtonStyle(Qt.ToolButtonIconOnly)
            item.setToolTip(data.name)
            item.clicked[bool].connect(self.clickGrid)
            row = int(index / 4)
            cols = index % 4
            title = QTextEdit(data.name)
            title.setMaximumHeight(40)
            gridLayout.addWidget(item, row * 2, cols)
            gridLayout.addWidget(title, row * 2 + 1, cols)
        gridData.setLayout(self.gridLayout)
        return gridData

    # 填充数据
    def search(self, path):
        walk = FileService(path, self.fileTypes)
        self.dataList = []
        self.dataList = walk.getFiles()

    # 菜单按钮处理
    def fileMenuProcess(self, action):
        print(action.text())
        if action.text() == "退出":
            self.close()

    # 点击搜索
    def clickSearchButton(self):
        self.statusBar().showMessage('执行中')
        # 提示框测试
        # replay = QMessageBox.question(self, '提示',
        #                               self.dirName.text(), QMessageBox.Yes)
        # if replay == QMessageBox.Yes:
        self.search(self.dirName.text())
        message = '总数:' + str(len(self.dataList)) + '   执行完毕！！！'
        self.statusBar().showMessage(message)

        if self.isGridData == 1:
            self.loadGridData()
        if self.isTableData == 1:
            self.loadTableData()
        self.initUI()

    # 选择框
    def openPath(self):
        fname = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        if not fname:
            QMessageBox().about(self, "提示", "打开文件失败，可能是文件内型错误")
        else:
            self.dirName.setText(fname)
        self.clickSearchButton()

    # 点击事件
    def openFile(self):
        choose = self.sender().text()
        if choose == '打开文件':
            command = '''start "" "''' + self.curFilePath + "\""
            os.system(command)
        if choose == '打开文件夹':
            command = '''start "" "''' + self.curDirPath + "\""
            os.system(command)

    # 点击事件
    def clickLine(self):
        col = self.tableData.currentColumn()
        index = self.tableData.currentRow()
        self.setCurInfo(self.dataList[index])
        self.infoToLeft()
        if col == 1 or col == 0:
            command = '''start "" "''' + self.curFilePath + "\""
            os.system(command)
        if col == 3 or col == 2:
            command = '''start "" "''' + self.curDirPath + "\""
            os.system(command)

    def setCurInfo(self, targetfile):
        self.curCode = targetfile.code
        self.curActress = targetfile.actress
        self.curFilePath = targetfile.path
        self.curDirPath = targetfile.dirPath
        self.curTitle = targetfile.name

    def clickGrid(self):
        text = self.sender().text()
        self.setCurInfo(self.dataList[int(text)])
        self.infoToLeft()

    def infoToLeft(self):
        if self.curCode is not None:
            self.codeInput.setText(self.curCode)
        else:
            self.codeInput.setText(getTitle(self.curTitle))
        self.titleInput.setText(self.curTitle)
        self.actressInput.setText(self.curActress)
        try:
            path = self.curFilePath
            if path.find("http") < 0:
                path = getPng(path, '.png')
                pic = Image.open(path)
                pic = pic.resize((250, 400))
                self.curPic.setPixmap(pic.toqpixmap())
            else:
                response = getResponse(path)
                if response.status == 200:
                    photo = QPixmap()
                    photo.loadFromData(response.read())
                    photo = photo.scaled(250, 400)
                    self.curPic.setPixmap(photo)

        except Exception as err:
            print("文件打开失败")
            print(err)
        # self.curPic.setMaximumWidth(250)
        # self.curPic.setMaximumHeight(400)

    # 载入数据 表格形式
    def loadTableData(self):
        data = self.tableData
        data.setRowCount(0)
        data.setColumnCount(0)
        if len(self.dataList) == 0:
            self.search(self.rootPath)
        data.setColumnCount(8)
        data.setRowCount(len(self.dataList))
        # 自适应列宽度
        # data.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data.setHorizontalHeaderLabels(['图片', '名称', "番号", "路径", "优优", "大小", "创建时间", "修改时间"])
        data.itemClicked.connect(self.clickLine)
        data.setColumnWidth(0, 200)
        data.setColumnWidth(1, 130)
        data.setColumnWidth(2, 100)
        for index in range(len(self.dataList)):
            data.setRowHeight(index, 300)
            file = self.dataList[index]
            row_id = index
            row_name = QLabel()
            path = getPng(file.path, ".png")
            if QPixmap(path).isNull():
                path = path.replace("png", "jpg")
            if QPixmap(path).isNull():
                imageArray = path.split(".")
                path = ""
                for index in range(len(imageArray)):
                    if index == len(imageArray) - 1:
                        path += "-poster.jpg"
                    elif index == len(imageArray) - 2:
                        path += imageArray[index]
                    else:
                        path += imageArray[index] + "."
                path = path.replace("png", "jpg")
            if not QPixmap(path).isNull():
                pic = QPixmap(path).scaled(200, 300)
                row_name.setPixmap(pic)
            data.setCellWidget(row_id, 0, row_name)
            data.setItem(row_id, 1, QTableWidgetItem(file.name))
            data.setItem(row_id, 2, QTableWidgetItem(file.code))
            data.setItem(row_id, 3, QTableWidgetItem(file.path))
            data.setItem(row_id, 4, QTableWidgetItem(file.actress))
            data.setItem(row_id, 5, QTableWidgetItem(file.size))
            data.setItem(row_id, 6, QTableWidgetItem(file.createTime))
            data.setItem(row_id, 7, QTableWidgetItem(file.modifyTime))

        return data

    # 选择布局
    def chooseLayout(self):
        button = self.sender().text()
        if button == '表格':
            self.isTableData = 1
            self.isGridData = 0
            self.loadTableData()
        if button == '网格':
            self.isTableData = 0
            self.isGridData = 1
        self.initUI()

    # 点击图片box
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

    # 点击视频box
    def videoChoose(self, state):
        if state == Qt.Checked:
            self.videoToggle = 1
            if FileConst.MP4 not in self.fileTypes:
                self.fileTypes.append(FileConst.MP4)
            if FileConst.WMV not in self.fileTypes:
                self.fileTypes.append(FileConst.WMV)
            if FileConst.MKV not in self.fileTypes:
                self.fileTypes.append(FileConst.MKV)
            if FileConst.AVI not in self.fileTypes:
                self.fileTypes.append(FileConst.AVI)

        else:
            self.videoToggle = 0
            if FileConst.MP4 in self.fileTypes:
                self.fileTypes.remove(FileConst.MP4)
            if FileConst.WMV in self.fileTypes:
                self.fileTypes.remove(FileConst.WMV)
            if FileConst.MKV in self.fileTypes:
                self.fileTypes.remove(FileConst.MKV)
            if FileConst.AVI in self.fileTypes:
                self.fileTypes.remove(FileConst.AVI)

    # 点击文档box
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
