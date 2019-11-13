#!/usr/bin/python3
import _thread
import base64
import math
import webbrowser

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.const.ImgConst import PLAY_IMG, SYNC_IMG, OPEN_IMG
from search.model.file import *
from search.net.javTool import JavTool
from search.service.fileService import FileService, nfoToJavMovie
from search.ui.infoUI import InfoUI


def getStrJoin(list):
    result = ""
    for string in list:
        result += "【" + string + "】"
    return result


class MainUI(QMainWindow):
    # 定义全局变量
    # 载入数据
    tabDataList = []
    dataList = []
    dataLib = []
    rootPath = ['f:\\emby\\tomake']
    fileTypes = []
    tableData = None
    # 搜索文本框
    dirName = None
    # 布局 0 栅格 1 表格 3 网页
    layoutType = '表格'
    # 0 海报模式 还是 1 封面模式 2 无图
    post_cover = NOPIC
    scan_status = 0

    # 缓存信息
    codeInput = None
    titleInput = None
    actressInput = None
    curCode = None
    curActress = None
    curPicUrl = None
    curFilePath = None
    curDirPath = None
    curTitle = None
    curDisk = "F:\\emby"

    # 默认勾选
    curTaskCount = 0
    imageToggle = 0
    videoToggle = 1
    docsToggle = 1
    sortType = DESC
    sortField = MODIFY_TIME
    webUrl = "https://www.cdnbus.in/"

    # 分页
    totalSize = 0
    totalRow = 0
    totalPage = 0
    pageNo = 1
    pageSize = 200
    tabTitle = ""
    pageTool = None

    # loading

    def getFirstRow(self):
        return self.pageSize * (self.pageNo - 1)

    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        self.fileAct = QToolBar("文件")
        self.displayAct = QToolBar("显示")
        self.addToolBar(Qt.TopToolBarArea, self.fileAct)
        self.addToolBar(Qt.BottomToolBarArea, self.displayAct)
        self._reset_path_action()
        self.infoLayout = QHBoxLayout()
        self.tableData = QTableWidget()
        self.codeInput = QLineEdit()
        self.titleInput = QTextEdit()
        self.actressInput = QLineEdit()
        self._initUI()

    # 载入UI窗口
    def _initUI(self):
        self.setWindowTitle("文件目录")
        self.resize(1400, 900)
        # 创建搜索按钮
        if self.dirName is None:
            self.dirName = QLineEdit()
        okButton = QPushButton("搜索")
        okButton.setShortcut(QKeySequence(str("Return")))
        okButton.clicked[bool].connect(self._search_button_click)

        openFile = QPushButton("打开文件")
        openFile.clicked[bool].connect(self._open_file)
        openDir = QPushButton("打开文件夹")
        openDir.clicked[bool].connect(self._open_file)
        codeSearch = QPushButton("番号搜索")
        codeSearch.clicked[bool].connect(self._search_code)
        infoButton = QPushButton("info")
        infoButton.clicked[bool].connect(self._click_info)

        syncJav = QPushButton("数据同步")
        syncJav.clicked[bool].connect(self._click_sync_movie)

        # 布局 0 栅格 1 表格 3 网页
        grid_layout = QRadioButton(GRID)
        web_layout = QRadioButton(WEB)
        table_layout = QRadioButton(TABLE)
        if self.layoutType == GRID:
            grid_layout.toggle()
        elif self.layoutType == TABLE:
            table_layout.toggle()
        elif self.layoutType == WEB:
            web_layout.toggle()
        grid_layout.clicked[bool].connect(self._choose_layout)
        table_layout.clicked[bool].connect(self._choose_layout)
        web_layout.clicked[bool].connect(self._choose_layout)
        self.layoutGroup = QButtonGroup()
        self.layoutGroup.addButton(grid_layout, 0)
        self.layoutGroup.addButton(table_layout, 1)
        self.layoutGroup.addButton(web_layout, 2)

        postButton = QRadioButton(POSTER)
        coverButton = QRadioButton(COVER)
        noPicButton = QRadioButton(NOPIC)

        if self.post_cover == POSTER:
            postButton.toggle()
        elif self.post_cover == COVER:
            coverButton.toggle()
        elif self.post_cover == NOPIC:
            noPicButton.toggle()

        postButton.clicked[bool].connect(self._choose_post_cover)
        coverButton.clicked[bool].connect(self._choose_post_cover)
        noPicButton.clicked[bool].connect(self._choose_post_cover)
        self.displayGroup = QButtonGroup()
        self.displayGroup.addButton(postButton, 0)
        self.displayGroup.addButton(coverButton, 1)
        self.displayGroup.addButton(noPicButton, 2)

        asc = QRadioButton(ASC)
        desc = QRadioButton(DESC)
        if self.sortType == ASC:
            asc.toggle()
        elif self.sortType == DESC:
            desc.toggle()
        asc.clicked[bool].connect(self._sort_type_change)
        desc.clicked[bool].connect(self._sort_type_change)
        self.sortTypeGroup = QButtonGroup()
        self.sortTypeGroup.addButton(asc, 0)
        self.sortTypeGroup.addButton(desc, 1)
        code = QRadioButton(CODE)
        size = QRadioButton(SIZE)
        mtime = QRadioButton(MODIFY_TIME)
        if self.sortField == CODE:
            code.toggle()
        elif self.sortField == SIZE:
            size.toggle()
        elif self.sortField == MODIFY_TIME:
            mtime.toggle()
        code.clicked[bool].connect(self._sort_field_change)
        size.clicked[bool].connect(self._sort_field_change)
        mtime.clicked[bool].connect(self._sort_field_change)
        self.sortFieldGroup = QButtonGroup()
        self.sortFieldGroup.addButton(code, 0)
        self.sortFieldGroup.addButton(size, 1)
        self.sortFieldGroup.addButton(mtime, 2)

        # 复选框
        image = QCheckBox("图片", self)
        image.stateChanged.connect(self._choose_image)
        video = QCheckBox("视频", self)
        video.stateChanged.connect(self._choose_video)
        docs = QCheckBox("文档", self)
        docs.stateChanged.connect(self._choose_docs)

        if self.imageToggle == 1:
            image.toggle()
        if self.videoToggle == 1:
            video.toggle()
        if self.docsToggle == 1:
            docs.toggle()
        # 创建左侧组件
        left_widget = QWidget()
        left_layout = QGridLayout()

        left_layout.addWidget(grid_layout, 1, 0)
        left_layout.addWidget(table_layout, 1, 1)
        left_layout.addWidget(web_layout, 1, 2)
        left_layout.addWidget(image, 2, 0)
        left_layout.addWidget(video, 2, 1)
        left_layout.addWidget(docs, 2, 2)

        left_layout.addWidget(self.dirName, 3, 0, 1, 2)
        left_layout.addWidget(okButton, 3, 2, 1, 1)

        left_layout.addWidget(postButton, 4, 0, 1, 1)
        left_layout.addWidget(coverButton, 4, 1, 1, 1)
        left_layout.addWidget(noPicButton, 4, 2, 1, 1)

        left_layout.addWidget(QLabel('排序类型'), 5, 0, 1, 1)
        left_layout.addWidget(asc, 5, 1, 1, 1)
        left_layout.addWidget(desc, 5, 2, 1, 1)
        left_layout.addWidget(code, 6, 0, 1, 1)
        left_layout.addWidget(size, 6, 1, 1, 1)
        left_layout.addWidget(mtime, 6, 2, 1, 1)
        left_layout.addWidget(QLabel(""), 7, 0, 1, 3)
        left_layout.addWidget(infoButton, 8, 0, 1, 1)
        left_layout.addWidget(codeSearch, 8, 2, 1, 1)
        left_layout.addWidget(QLabel("番号"), 9, 0, 1, 1)
        left_layout.addWidget(self.codeInput, 9, 1, 1, 2)

        left_layout.addWidget(QLabel("标题"), 10, 0, 1, 1)
        self.titleInput.setMaximumHeight(60)
        self.titleInput.setMaximumWidth(160)
        left_layout.addWidget(self.titleInput, 10, 1, 2, 2)
        left_layout.addWidget(QLabel("演员"), 14, 0, 1, 1)
        left_layout.addWidget(self.actressInput, 14, 1, 1, 2)
        self.curPic = QLabel()
        self.curPic.setMinimumHeight(380)
        self.curPic.setMinimumWidth(240)
        left_layout.addWidget(self.curPic, 15, 0, 15, 3)

        # left_layout.addWidget(openFile)
        # left_layout.addWidget(openDir)
        # left_layout.addWidget(syncJav)

        self.webUrlLable = QLabel(self.webUrl)

        left_layout.addWidget(QLabel("数据源:"), 0, 0, 1, 1)
        left_layout.addWidget(self.webUrlLable, 0, 1, 1, 2)
        # self.diskLabel = QLabel(getStrJoin(self.rootPath))
        # self.diskLabel.setWordWrap(True)
        # self.diskLabel.setMaximumWidth(240)
        # left_layout.addWidget(self.diskLabel, 20, 0, 1, 3)

        # 创建右侧组件
        self.tab_widget = QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabShape(QTabWidget.Triangular)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._tab_close)
        self.tab_widget.currentChanged.connect(self._tab_change)

        # 创建主窗口组件 挂载布局
        main_widget = QWidget()
        main_layout = QGridLayout()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 0, 0)
        main_layout.addWidget(self.tab_widget, 0, 1)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self._menu_button_add()

        self.show()

    # 点击搜索

    def _search_button_click(self):
        self.statusBar().showMessage('执行中')
        self.tabTitle = self.dirName.text()
        self._search_from_Lib()
        # 计算总容量
        message = "库文件数:【" + str(self.totalRow) + " | " + str(self.totalSize) + "】"
        message += '搜索结果:【' + str(len(self.dataList)) + " | " + self._get_total_size(self.dataList) + '】   执行完毕！！！'
        self.statusBar().showMessage(message)
        self._load_context()

    def _get_total_size(self, dataList):
        totalSize = 0
        for data in dataList:
            if data.size:
                totalSize += data.size
        return getSizeFromNumber(totalSize)

    def _choose_post_cover(self):
        #  0 海报 1 封面
        self.post_cover = self.displayGroup.checkedButton().text()
        # index = self.tab_widget.currentIndex()
        # self.tab_widget.removeTab(self.tab_widget.count() - 1)
        self._load_context()

    def _sort_type_change(self):
        print(self.sortTypeGroup.checkedButton().text())
        self.sortType = self.sortTypeGroup.checkedButton().text()
        self._load_context()

    def _sort_field_change(self):
        print(self.sortFieldGroup.checkedButton().text())
        self.sortField = self.sortFieldGroup.checkedButton().text()
        self._load_context()

    # 选择布局
    def _choose_layout(self):
        # 布局 0 栅格 1 表格 3 网页
        self.layoutType = self.layoutGroup.checkedButton().text()
        self._load_context()

    def _load_context(self, isNew=True):
        try:
            self._load_context_thread(isNew)
        except Exception as err:
            print("load_context has error")
            print(err)

    def _load_context_thread(self, isNew):
        self._sort_files_list()
        if self.tabTitle == '' or self.tabTitle is None:
            title = str(self.pageNo) + "/" + str(self.totalPage)
            firstRow = self.pageSize * (self.pageNo - 1) + 1
            lastRow = self.pageSize * (self.pageNo) if self.pageSize * (self.pageNo) <= self.totalRow else self.totalRow
            title += "--" + str(firstRow) + "/" + str(lastRow)
            title += "--" + str(self.totalRow)
            self.tabTitle = title
        if len(self.dataList) == 0:
            self._tab_close_all()
            return
        if self.layoutType == WEB:
            # 打开浏览器
            webbrowser.open(self.webUrl)
            return
        if self.layoutType == '栅格':
            gridData = self._load_grid()
            if isNew:
                self._tab_add(gridData, self.tabTitle)
            else:
                self.tab_widget.setCurrentWidget(gridData)
        elif self.layoutType == '表格':
            tableData = self._load_table()
            if isNew:
                self._tab_add(tableData, self.tabTitle)
            else:
                self.tab_widget.setCurrentWidget(tableData)

    # 搜饭
    def _search_code(self):
        tool = JavTool(self.webUrl)
        code = self.codeInput.text()
        movie = tool.getJavInfo(code)
        if movie is None:
            QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
        else:
            self.curCode = code
            self.curActress = movie.getActress()
            self.curPicUrl = movie.cover
            self.curTitle = movie.title
            self._load_info_to_left()

    # 填充数据
    def _search_from_Lib(self):
        word = self.tabTitle
        result = []
        if word == '' or word is None:
            if self.pageNo == self.totalPage:
                result = self.dataLib[self.getFirstRow():]
            else:
                first = self.getFirstRow()
                last = self.getFirstRow() + self.pageSize
                result = self.dataLib[first:last]
        else:
            for files in self.dataLib:
                if (files.name is not None and files.name.find(word) >= 0) or (
                        files.code is not None and files.code.find(word) >= 0) or (
                        files.actress is not None and files.actress.find(word) >= 0) or word == '' or word is None:
                    if files.fileType in self.fileTypes:
                        result.append(files)
        self.dataList = result

    def _excute__search_from_disk(self):
        self.dataLib = []
        if len(self.rootPath) > 0:
            for path in self.rootPath:
                if os.path.exists(path):
                    walk = FileService().build(path, self.fileTypes)
                    curList = walk.getFiles()
                    self.dataLib.extend(curList)
        self.totalRow = len(self.dataLib)
        self.totalPage = math.ceil(self.totalRow / self.pageSize)
        self.totalSize = self._get_total_size(self.dataLib)

        if self.pageTool is None or self.pageTool == '':
            self.pageTool = self.addToolBar("分页")
        else:
            self.pageTool.clear()
        nextPage = QAction("下一页", self)
        nextPage.triggered[bool].connect(self._change_Page)
        prePage = QAction("上一页", self)
        prePage.triggered[bool].connect(self._change_Page)
        firstPage = QAction("首页", self)
        firstPage.triggered[bool].connect(self._change_Page)
        lastPage = QAction("末页", self)
        lastPage.triggered[bool].connect(self._change_Page)
        self.pageTool.addAction(firstPage)
        self.pageTool.addAction(nextPage)
        self.pageTool.addAction(prePage)
        self.pageTool.addAction(lastPage)
        for index in range(self.totalPage):
            curPage = QAction(str(index + 1), self)
            curPage.triggered[bool].connect(self._change_Page)
            self.pageTool.addAction(curPage)

        self.scan_status = 0
        self._search_button_click()

    def _scan_disk(self):
        if self.scan_status == 0:
            self.scan_status = 1
            message = "开始搜索..."
            self.statusBar().showMessage(message)
            self._tab_close_all()
            self._excute__search_from_disk()
            # th = threading.Thread(target=self._excute__search_from_disk, name='funciton')
            # th.start()
            # _thread.start_new_thread(self._excute__search_from_disk())
        else:
            message = "搜索中..."
            self.statusBar().showMessage(message)

    def _sort_files_list(self):
        if len(self.dataList) > 0:
            self.dataList.sort(key=getSortField(self.sortField), reverse=getReverse(self.sortType))

    def _tab_close_all(self):
        '''关闭所有Tab'''
        self.tab_widget.clear()
        self.tabDataList = []

    def _tab_close(self, index):
        '''关闭指定Tab'''
        self.tab_widget.removeTab(index)
        if index < len(self.tabDataList):
            del self.tabDataList[index]
        index = self.tab_widget.currentIndex()
        if index > 0:
            self.dataList = self.tabDataList[index]

    def _tab_change(self, index):
        self.dataList = self.tabDataList[index]

    def _tab_add(self, widget, title):
        """ # 单页应用 添加前删除所有Tab页"""
        if title == '' or title is None:
            title = '全部'
        try:
            self.tabDataList.append(self.dataList)
            self.tab_widget.addTab(widget, title)
            self.tab_widget.setCurrentWidget(widget)
        except Exception as err:
            print("_tab_add")
            print(err)

    # 选择框
    def _open_path(self):
        pathname = QFileDialog.getExistingDirectory(self, "选择文件夹", self.curDisk)
        if pathname == '' or pathname is None:
            return
        else:
            self.rootPath.append(pathname)
            if len(pathname.split("/")) > 1:
                arr = pathname.split("/")
                pathname = pathname.replace(arr[-1], '')
                self.curDisk = pathname
            self._reset_path_action()
            self.curDisk = pathname
            self._open_path()

    def _reset_path_action(self):
        '''重置工具栏 路径按钮'''
        if self.displayAct != "" and self.displayAct is not None:
            self.displayAct.clear()
        if len(self.rootPath) > 0:
            for path in self.rootPath:
                pathAct = QAction(path, self)
                pathAct.triggered[bool].connect(self._path_click)
                self.displayAct.addAction(pathAct)

    def _path_click(self):
        text = self.sender().text()
        self.rootPath.remove(text)
        self._reset_path_action()
        self._tab_close_all()

    def _clear_path(self):
        self.rootPath = []
        self.dataLib = []
        self.dataList = []
        self._reset_path_action()
        self._tab_close_all()

    def _change_Page(self):
        text = self.sender().text()
        if self.dirName.text() == '' or self.dirName.text() is None:
            # 搜索框为空的时候执行翻页 否则只进行搜索
            if text == '首页':
                self.pageNo = 1
            elif text == '下一页':
                if self.totalPage == 1:
                    return
                self.pageNo = self.pageNo + 1
            elif text == '上一页':
                if self.pageNo == 1:
                    return
                self.pageNo = self.pageNo - 1
            elif text == '末页':
                self.pageNo = self.totalPage
            else:
                self.pageNo = int(text)
        self._search_button_click()

    # 点击事件
    def _open_file(self):
        choose = self.sender().text()
        if choose == '打开文件':
            if self.curFilePath is None or self.curFilePath == '':
                return
            command = '''start "" "''' + self.curFilePath + "\""
            os.system(command)
        if choose == '打开文件夹':
            if self.curDirPath is None or self.curDirPath == '':
                return
            command = '''start "" "''' + self.curDirPath
            os.system(command)

    # 点击事件
    def _table_line_click(self):
        index = self.tableData.currentRow()
        self._set_curinfo(index)

    def _table_line_double_click(self):
        self._table_line_click()
        col = self.tableData.currentColumn()
        if col == 1 or col == 0:
            if self.curFilePath is None or self.curFilePath == '':
                return
            command = '''start "" "''' + self.curFilePath + "\""
            os.system(command)
        if col == 3 or col == 2:
            if self.curDirPath is None or self.curDirPath == '':
                return
            command = '''start "" "''' + self.curDirPath + "\""
            os.system(command)

    def _set_curinfo(self, index):
        if index is None:
            return
        targetfile = self.dataList[index]
        nfopath = replaceSuffix(targetfile.path, "nfo")
        movieInfo = nfoToJavMovie(nfopath)
        if movieInfo is not None:
            self.curCode = movieInfo.code
            self.curActress = movieInfo.getActress()
            self.curFilePath = targetfile.path
            self.curPicUrl = None
            self.curDirPath = movieInfo.dirPath
            self.curTitle = movieInfo.title
        else:
            self.curCode = targetfile.code
            self.curActress = targetfile.actress
            self.curFilePath = targetfile.path
            self.curPicUrl = None
            self.curDirPath = targetfile.dirPath
            self.curTitle = targetfile.name

        self._load_info_to_left()

    def _grid_click(self):
        text = self.sender().text()
        index = int(text)
        if index > len(self.dataList) - 1:
            return
        self._set_curinfo(index)

    def _load_info_to_left(self):
        if self.curCode is not None:
            self.codeInput.setText(self.curCode)
        else:
            title = getTitle(self.curTitle)
            self.codeInput.setText(title)
        self.titleInput.setText(self.curTitle)
        self.actressInput.setText(self.curActress)
        try:
            if self.curPicUrl is not None:
                pic = getPixMapFromNet(self.curPicUrl, 240, 380)
                if pic is not None and not pic.isNull():
                    self.curPic.setPixmap(pic)
            else:
                pic = getPixMap(self.curFilePath, 240, 380)
                if pic is not None and not pic.isNull():
                    self.curPic.setPixmap(pic)

        except Exception as err:
            print("_load_info_to_left")
            print("文件打开失败")
            print(err)

    # loading 数据
    def _load_grid(self):
        scroll = QScrollArea()
        self.gridData = QWidget()
        self.gridLayout = QGridLayout()
        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().deleteLater()
        width = 200 if self.post_cover == POSTER else (500 if self.post_cover == COVER else 300)
        each = int(self.tab_widget.width() / width)

        for index in range(len(self.dataList)):
            data = self.dataList[index]
            item = QToolButton()
            item.setText(str(index))
            if self.post_cover != NOPIC:
                try:
                    if self.post_cover == POSTER:
                        iconPath = replaceSuffix(data.path, PNG)
                        if os.path.exists(iconPath):
                            pass
                        else:
                            iconPath = replaceSuffix(data.path, JPG)
                    else:
                        iconPath = replaceSuffix(data.path, JPG)
                    icon = QIcon(iconPath)
                    if icon is not None and not icon.isNull():
                        item.setIcon(icon)
                except Exception as err:
                    print("_load_grid_data")
                    print(err)
                item.setIconSize(QSize(width, 300))
            item.setToolButtonStyle(Qt.ToolButtonIconOnly)
            item.setToolTip(data.name)
            item.clicked[bool].connect(self._grid_click)

            title = QLabel(data.name)
            title.setMaximumHeight(40)
            title.setWordWrap(True)
            title.setMaximumWidth(width)
            title.setMinimumWidth(width)

            play = QToolButton()
            play.clicked[bool].connect(self._click_play_button)
            play.setText(str(index))
            playPhoto = QPixmap()
            playStr = base64.b64decode(PLAY_IMG)
            playPhoto.loadFromData(playStr)
            play.setIcon(QIcon(playPhoto))
            play.setIconSize(QSize(20, 20))
            play.setToolTip("播放")
            play.setToolButtonStyle(Qt.ToolButtonIconOnly)
            openF = QToolButton()
            openF.clicked[bool].connect(self._click_openF_button)
            openF.setText(str(index))
            openPhoto = QPixmap()
            openStr = base64.b64decode(OPEN_IMG)
            openPhoto.loadFromData(openStr)
            openF.setIcon(QIcon(openPhoto))
            openF.setIconSize(QSize(20, 20))
            openF.setToolTip("打开文件夹")
            openF.setToolButtonStyle(Qt.ToolButtonIconOnly)

            sync = QToolButton()
            sync.clicked[bool].connect(self._click_sync_button)
            sync.setText(str(index))
            syncPhoto = QPixmap()
            syncStr = base64.b64decode(SYNC_IMG)
            syncPhoto.loadFromData(syncStr)
            sync.setIcon(QIcon(syncPhoto))
            sync.setIconSize(QSize(20, 20))
            sync.setToolTip("同步")
            sync.setToolButtonStyle(Qt.ToolButtonIconOnly)
            row = int(index / each)
            cols = index % each
            colspan = cols * 3
            rowspan = row * 3 if self.post_cover != NOPIC else row * 2
            if self.post_cover != NOPIC:
                self.gridLayout.addWidget(item, rowspan, colspan, 1, 3)
            self.gridLayout.addWidget(play, rowspan + 1, colspan, 1, 1)
            self.gridLayout.addWidget(openF, rowspan + 1, colspan + 1, 1, 1)
            self.gridLayout.addWidget(sync, rowspan + 1, colspan + 2, 1, 1)
            self.gridLayout.addWidget(title, rowspan + 2, colspan, 1, 3)
        self.gridData.setLayout(self.gridLayout)
        scroll.setWidget(self.gridData)
        scroll.setAutoFillBackground(True)
        return scroll

    # 载入数据 表格形式
    def _load_table(self):
        tableData = self.tableData
        tableData.setRowCount(0)
        tableData.setColumnCount(0)
        tableData.setColumnCount(8)
        tableData.setRowCount(len(self.dataList))
        # 自适应列宽度

        tableData.setHorizontalHeaderLabels(['图片', NAME, "番号", "路径", "优优", "大小", "创建时间", "修改时间"])
        tableData.doubleClicked.connect(self._table_line_double_click)
        tableData.itemClicked.connect(self._table_line_click)
        tableData.setColumnWidth(0, 200 if self.post_cover != NOPIC else 80)
        tableData.setColumnWidth(1, 180)
        tableData.setColumnWidth(2, 80)
        tableData.setColumnWidth(3, 200)
        # tableData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for index in range(len(self.dataList)):
            file = self.dataList[index]
            row_id = index
            if self.post_cover != NOPIC:
                tableData.setRowHeight(index, 300)
                row_name = QLabel()
                pic = getPixMap(file.path, 200, 300)
                if pic is not None:
                    row_name.setPixmap(pic)
                tableData.setCellWidget(row_id, 0, row_name)
            else:
                tableData.setItem(row_id, 0, QTableWidgetItem("无图模式"))
            tableData.setItem(row_id, 1, QTableWidgetItem(file.name))
            tableData.setItem(row_id, 2, QTableWidgetItem(file.code))
            tableData.setItem(row_id, 3, QTableWidgetItem(file.path))
            tableData.setItem(row_id, 4, QTableWidgetItem(file.actress))
            tableData.setItem(row_id, 5, QTableWidgetItem(file.sizeStr))
            tableData.setItem(row_id, 6, QTableWidgetItem(file.create_time))
            tableData.setItem(row_id, 7, QTableWidgetItem(file.modify_time))

        return tableData

    def _click_sync_movie(self):
        '''点击同步数据 按钮'''
        code = self.codeInput.text()
        if code is None or code == '':
            return
            # 获取影片信息
        self._pull_move_movie(self.curDirPath, self.curFilePath, code)

    def _sync_movie_info_new_thread(self, targetfile):
        '''同步数据 开启线程'''
        self._pull_move_movie(targetfile.dirPath, targetfile.path, targetfile.code)

    def _pull_move_movie(self, dirPath, filePath, code):
        '''  pull数据并移动  '''

        self.curTaskCount = self.curTaskCount + 1
        message = "当前任务数:" + str(self.curTaskCount) + "【" + code + '】 添加成功！'
        self.statusBar().showMessage(message)

        tool = JavTool(self.webUrl)
        movie = tool.getJavInfo(code)

        if movie is None:
            # QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
            self.curTaskCount = self.curTaskCount - 1
            message = "当前任务数:" + str(self.curTaskCount) + "【" + filePath + '】 匹配失敗！'
            self.statusBar().showMessage(message)
            return
        if tool is None:
            tool = JavTool(self.webUrl)
        # 生成目录下载图片并切图png
        make_ok = tool.makeActress(dirPath, movie)
        self.curTaskCount = self.curTaskCount - 1
        message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 同步成功！'
        if make_ok:
            # 移动源文件到目标目录 并重命名
            if tool.dirpath is not None and tool.fileName is not None:
                newfilepath = tool.dirpath + "\\" + tool.fileName + "." + getSuffix(filePath)
                os.rename(filePath, newfilepath)
                print("文件移动重命名成功:" + newfilepath)
        else:
            message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 同步失败！'
        self.statusBar().showMessage(message)
        # QMessageBox().about(self, "提示", "同步成功!!!")

    def _click_play_button(self):
        '''执行播放'''
        text = self.sender().text()
        self._set_curinfo(int(text))
        if self.curFilePath is None or self.curFilePath == '':
            return
        command = '''start "" "''' + self.curFilePath + "\""
        os.system(command)

    def _click_openF_button(self):
        '''执行打开文件夹'''
        text = self.sender().text()
        self._set_curinfo(int(text))
        if self.curDirPath is None or self.curDirPath == '':
            return
        command = '''start "" "''' + self.curDirPath
        os.system(command)

    def _click_sync_button(self):
        '''执行同步数据'''
        text = self.sender().text()
        targetfile = self.dataList[int(text)]
        _thread.start_new_thread(self._pull_move_movie, (targetfile.dirPath, targetfile.path, targetfile.code))

    def _click_info(self):

        javMovie = None
        nfoPath = replaceSuffix(self.curFilePath, 'nfo')
        if nfoPath is not None and nfoPath != '' and os.path.exists(nfoPath):
            javMovie = nfoToJavMovie(nfoPath)
        elif self.codeInput.text() is not None and self.codeInput.text() != '':
            tool = JavTool(self.webUrl)
            javMovie = tool.getJavInfo(self.codeInput.text())
        if javMovie is not None:
            info = InfoUI(javMovie)
            self._tab_add(info, javMovie.code)

    # 添加菜单按钮
    def _menu_button_add(self):
        bar = self.menuBar()
        # 文件
        openAction = QAction("打开路径", self)
        openAction.setShortcut(QKeySequence.Open)
        quitAction = QAction("退出", self)
        quitAction.setShortcut(QKeySequence(str("ctrl+Q")))

        file = bar.addMenu("文件")
        file.setShortcutEnabled(1)
        file.addAction(openAction)
        file.addAction(quitAction)
        file.triggered[QAction].connect(self._menu_process_file)
        # 设置
        changeUrlAction = QAction("切换数据源", self)
        changePageSizeAction = QAction("切换分页", self)

        setting = bar.addMenu("设置")
        setting.setShortcutEnabled(1)
        setting.addAction(changeUrlAction)
        setting.addAction(changePageSizeAction)
        setting.triggered[QAction].connect(self._menu_process_file)

        clearDisk = QAction("清空路径", self)
        clearDisk.setShortcut(QKeySequence.Save)
        scanDisk = QAction("扫描路径", self)
        openAction.triggered[bool].connect(self._open_path)
        scanDisk.triggered[bool].connect(self._scan_disk)
        clearDisk.triggered[bool].connect(self._clear_path)
        self.fileAct.addAction(openAction)
        self.fileAct.addAction(clearDisk)
        self.fileAct.addAction(scanDisk)

    # 菜单按钮处理
    def _menu_process_file(self, action):
        if action.text() == "退出":
            self.close()
        if action.text() == "切换数据源":
            text, ok = QInputDialog.getText(self, "设置数据源", "网址:")
            if ok:
                self.webUrl = text
                self.webUrlLable.setText(text)
            return
        elif action.text() == "切换分页":
            text, ok = QInputDialog.getText(self, "切换分页", "每页显示:")
            if ok:
                self.pageSize = int(text)
            return
        elif action.text() == "扫描路径":
            self._scan_disk()
        elif action.text() == "清空路径":
            self._clear_path()

    # 点击图片box

    def _choose_image(self, state):

        if state == Qt.Checked:
            self.imageToggle = 1
            if not set(IMAGE_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(IMAGE_TYPES)
        else:
            self.imageToggle = 0
            if set(IMAGE_TYPES) < set(self.fileTypes):
                for image in IMAGE_TYPES:
                    self.fileTypes.remove(image)

    # 点击视频box
    def _choose_video(self, state):

        if state == Qt.Checked:
            self.videoToggle = 1
            if not set(VIDEO_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(VIDEO_TYPES)
        else:
            self.videoToggle = 0
            if set(VIDEO_TYPES) < set(self.fileTypes):
                for video in VIDEO_TYPES:
                    self.fileTypes.remove(video)

    # 点击文档box

    def _choose_docs(self, state):

        if state == Qt.Checked:
            self.docsToggle = 1
            if not set(DOCS_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(DOCS_TYPES)
        else:
            self.docsToggle = 0
            if set(DOCS_TYPES) < set(self.fileTypes):
                for doc in DOCS_TYPES:
                    self.fileTypes.remove(doc)
