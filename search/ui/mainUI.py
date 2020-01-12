#!/usr/bin/python3
# encoding=utf-8
import _thread
import base64
import logging
import math
import webbrowser

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.const.ImgConst import *
from search.model.file import *
from search.net.javTool import JavTool
from search.service.fileService import FileService, nfoToJavMovie
from search.ui.infoUI import InfoUI

logger = logging.getLogger("search")


def getStrJoin(list):
    result = ""
    for string in list:
        result += "【" + string + "】"
    return result


def _get_total_size(dataList):
    totalSize = 0
    for data in dataList:
        if data.size:
            totalSize += data.size
    return getSizeFromNumber(totalSize)


class MainUI(QMainWindow):
    # 定义全局变量
    # 载入数据
    tabDataList = []
    dataList = []
    dataLib = []
    actressLib = {}
    actressNames = {}
    rootPath = ['e:\\emby\\tomake', 'f:\\emby\\tomake', 'f:\\emby\\emby-rename', 'h:\\emby\\tomake',
                'h:\\emby\\emby-rename']
    fileTypes = []
    tableData = None
    # 搜索文本框
    dirName = None
    # 布局 0 栅格 1 表格 3 网页
    layoutType = GRID
    # 0 海报模式 还是 1 封面模式 2 无图
    post_cover = POSTER
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
    pageSize = 100
    tabTitle = ""
    pageTool = None

    # loading

    def _getFirstRow(self):
        return self.pageSize * (self.pageNo - 1)

    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        logger.info("页面初始化...")
        self.fileAct = QToolBar("文件")
        self.displayAct = QToolBar("显示")
        self.addToolBar(Qt.TopToolBarArea, self.fileAct)
        self.addToolBar(Qt.BottomToolBarArea, self.displayAct)
        self._resetPathTool()
        self.infoLayout = QHBoxLayout()
        self.tableData = QTableWidget()
        self.codeInput = QLineEdit()
        self.titleInput = QTextEdit()
        self.actressInput = QLineEdit()
        self._initUI()

    # 载入UI窗口
    def _initUI(self):
        iconStr = base64.b64decode(YELLOW)
        iconPhoto = QPixmap()
        iconPhoto.loadFromData(iconStr)
        icon = QIcon(iconPhoto)
        self.setWindowIcon(icon)
        self.setWindowTitle("文件搜索")
        self.resize(1400, 900)
        # 创建搜索按钮
        if self.dirName is None:
            self.dirName = QLineEdit()
        okButton = QPushButton("搜索")
        okButton.setShortcut(QKeySequence(str("Return")))
        okButton.clicked[bool].connect(self._clickSearchButton)

        openFile = QPushButton("打开文件")
        openFile.clicked[bool].connect(self._open_file)
        openDir = QPushButton("打开文件夹")
        openDir.clicked[bool].connect(self._open_file)
        codeSearch = QPushButton("番号搜索")
        codeSearch.clicked[bool].connect(self._ClickSearchCode)
        infoButton = QPushButton("优优")
        infoButton.clicked[bool].connect(self._clickInfo)

        syncJav = QPushButton("数据同步")
        syncJav.clicked[bool].connect(self._clickSyncMovie)

        # 布局 0 栅格 1 表格 3 网页
        grid_layout = QRadioButton(GRID)
        web_layout = QRadioButton(ACTRESS)
        table_layout = QRadioButton(TABLE)
        if self.layoutType == GRID:
            grid_layout.toggle()
        elif self.layoutType == TABLE:
            table_layout.toggle()
        elif self.layoutType == ACTRESS:
            web_layout.toggle()
        grid_layout.clicked[bool].connect(self._chooseLayout)
        table_layout.clicked[bool].connect(self._chooseLayout)
        web_layout.clicked[bool].connect(self._chooseLayout)
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

        postButton.clicked[bool].connect(self._choosePostCover)
        coverButton.clicked[bool].connect(self._choosePostCover)
        noPicButton.clicked[bool].connect(self._choosePostCover)
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
        asc.clicked[bool].connect(self._sortTypeChange)
        desc.clicked[bool].connect(self._sortTypeChange)
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
        code.clicked[bool].connect(self._sortFieldChange)
        size.clicked[bool].connect(self._sortFieldChange)
        mtime.clicked[bool].connect(self._sortFieldChange)
        self.sortFieldGroup = QButtonGroup()
        self.sortFieldGroup.addButton(code, 0)
        self.sortFieldGroup.addButton(size, 1)
        self.sortFieldGroup.addButton(mtime, 2)

        # 复选框
        image = QCheckBox("图片", self)
        image.stateChanged.connect(self._chooseImage)
        video = QCheckBox("视频", self)
        video.stateChanged.connect(self._chooseVideo)
        docs = QCheckBox("文档", self)
        docs.stateChanged.connect(self._chooseDocs)

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

        self._initMenuButton()

        self.show()

    # 点击搜索

    def _clickSearchButton(self):
        self.statusBar().showMessage('执行中')
        self.tabTitle = self.dirName.text()
        self._searchFromLib()
        # 计算总容量
        message = "库文件数:【" + str(self.totalRow) + " | " + str(self.totalSize) + "】"
        message += '搜索结果:【' + str(len(self.dataList)) + " | " + _get_total_size(self.dataList) + '】   执行完毕！！！'
        self.statusBar().showMessage(message)
        self._loadContext()
        self.dirName.setText("")

    def _choosePostCover(self):
        #  0 海报 1 封面
        self.post_cover = self.displayGroup.checkedButton().text()
        self._loadContext()

    def _sortTypeChange(self):
        print(self.sortTypeGroup.checkedButton().text())
        self.sortType = self.sortTypeGroup.checkedButton().text()
        self._sort_files_list(self.dataLib)
        self._loadContext()

    def _sortFieldChange(self):
        print(self.sortFieldGroup.checkedButton().text())
        self.sortField = self.sortFieldGroup.checkedButton().text()
        self._sort_files_list(self.dataLib)
        self._loadContext()

    # 选择布局
    def _chooseLayout(self):
        # 布局 0 栅格 1 表格 3 网页
        self.layoutType = self.layoutGroup.checkedButton().text()

        self._loadContext()

    def _loadContext(self, isNew=True):
        try:
            self._loadContextThread(isNew)
        except Exception as err:
            print("load_context has error" + str(err))
            logger.error("load_context has error" + str(err))

    def _loadContextThread(self, isNew):
        self._sort_files_list(self.dataList)
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
        if self.layoutType == ACTRESS:
            self._tab_close_all()
            gridData = self._initGridActress()
            if isNew:
                self._tab_add(gridData, 'YY:' + str(len(self.actressLib)))
            else:
                self.tab_widget.setCurrentWidget(gridData)
        if self.layoutType == GRID:
            gridData = self._initGrid()
            if isNew:
                self._tab_add(gridData, self.tabTitle)
            else:
                self.tab_widget.setCurrentWidget(gridData)
        elif self.layoutType == TABLE:
            tableData = self._initTable()
            if isNew:
                self._tab_add(tableData, self.tabTitle)
            else:
                self.tab_widget.setCurrentWidget(tableData)

    # 搜饭
    def _ClickSearchCode(self):

        code = self.codeInput.text()
        if code is None or code == '':
            QMessageBox().about(self, "提示", "请输入番号")
            return
        url = self.webUrl + code
        webbrowser.open(url)

    # 填充数据
    def _searchFromLib(self):
        word = self.tabTitle
        result = []
        self._sort_files_list(self.dataLib)
        if word == '' or word is None:
            if self.pageNo == self.totalPage:
                result = self.dataLib[self._getFirstRow():]
            else:
                first = self._getFirstRow()
                last = self._getFirstRow() + self.pageSize
                result = self.dataLib[first:last]
        else:
            for files in self.dataLib:
                if (files.name is not None and files.name.find(word) >= 0) or (
                        files.code is not None and files.code.find(word) >= 0) or (
                        files.actress is not None and files.actress.find(word) >= 0) or word == '' or word is None:
                    if files.fileType in self.fileTypes:
                        result.append(files)
        self.dataList = result

    def _excuteSearchFromDisk(self):
        self.dataLib.clear()
        self.actressLib.clear()
        self.actressNames = {}
        if len(self.rootPath) > 0:
            for path in self.rootPath:
                if os.path.exists(path):
                    walk = FileService().build(path, self.fileTypes)
                    curList, curAcrtess = walk.getFiles(self.dataLib, self.actressNames, self.actressLib)

                    # self.dataLib.extend(curList)
                    # self.actressLib.extend(curAcrtess)
        self.actressNames = sorted(self.actressNames.items(), key=lambda x: (x[1], x[0]),
                                   reverse=getReverse(self.sortType))
        self.scan_status = 0
        self._initPageTools()

        self._clickSearchButton()

    def _initPageTools(self):
        '''分页初始化'''
        self.totalRow = len(self.dataLib)
        self.totalPage = math.ceil(self.totalRow / self.pageSize)
        self.totalSize = _get_total_size(self.dataLib)
        if self.pageTool is None or self.pageTool == '':
            self.pageTool = self.addToolBar("分页")
        else:
            self.pageTool.clear()
        nextPage = QAction("下一页", self)
        nextStr = base64.b64decode(FORWARD)
        nextPhoto = QPixmap()
        nextPhoto.loadFromData(nextStr)
        nextPage.setIcon(QIcon(nextPhoto))
        nextPage.triggered[bool].connect(self._changePage)
        prePage = QAction("上一页", self)
        preStr = base64.b64decode(BACK)
        prePhoto = QPixmap()
        prePhoto.loadFromData(preStr)
        prePage.setIcon(QIcon(prePhoto))
        prePage.triggered[bool].connect(self._changePage)
        firstPage = QAction("首页", self)
        firstStr = base64.b64decode(LAST)
        firstPhoto = QPixmap()
        firstPhoto.loadFromData(firstStr)
        firstPage.setIcon(QIcon(firstPhoto))
        firstPage.triggered[bool].connect(self._changePage)
        lastPage = QAction("末页", self)
        lastStr = base64.b64decode(NEXT)
        lastPhoto = QPixmap()
        lastPhoto.loadFromData(lastStr)
        lastPage.setIcon(QIcon(lastPhoto))
        lastPage.triggered[bool].connect(self._changePage)
        self.pageTool.addAction(firstPage)
        self.pageTool.addAction(prePage)
        self.pageTool.addAction(nextPage)
        self.pageTool.addAction(lastPage)
        for index in range(self.totalPage):
            curPage = QAction(str(index + 1), self)
            curPage.triggered[bool].connect(self._changePage)
            self.pageTool.addAction(curPage)

    def _searchDisk(self):
        if self.scan_status == 0:
            self.scan_status = 1
            message = "开始搜索..."
            self.statusBar().showMessage(message)
            self._tab_close_all()
            self._excuteSearchFromDisk()
            # th = threading.Thread(target=self._excute__search_from_disk, name='funciton')
            # th.start()
            # _thread.start_new_thread(self._excute__search_from_disk())
        else:
            message = "搜索中..."
            self.statusBar().showMessage(message)

    def _sort_files_list(self, dataList):
        if len(dataList) > 0:
            # logger.info("当前排序：" + self.sortField + self.sortType)
            dataList.sort(key=getSortField(self.sortField), reverse=getReverse(self.sortType))

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
            logger.error("_tab_add" + str(err))

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
            self._resetPathTool()
            self.curDisk = pathname
            self._open_path()

    def _resetPathTool(self):
        '''重置工具栏 路径按钮'''
        if self.displayAct != "" and self.displayAct is not None:
            self.displayAct.clear()
        if len(self.rootPath) > 0:
            for path in self.rootPath:
                pathAct = QAction(path, self)
                pathAct.triggered[bool].connect(self._clickPathTool)
                self.displayAct.addAction(pathAct)

    def _clickPathTool(self):
        text = self.sender().text()
        self.rootPath.remove(text)
        self._resetPathTool()
        self._tab_close_all()

    def _clickClearPath(self):
        self.rootPath = []
        self.dataLib = []
        self.dataList = []
        self._resetPathTool()
        self._tab_close_all()
        self.pageTool.clear()

    def _repeatCheck(self):
        if len(self.dataLib) == 0:
            QMessageBox.about(self, "提示", "请先扫描")
            return
        repeatFile = []
        tempDict = {}
        for item in self.dataLib:
            code = item.code
            if tempDict.get(code) is not None:
                if repeatFile.count(item) == 0:
                    repeatFile.append(tempDict[code])
                repeatFile.append(item)
            else:
                tempDict[code] = item

        if len(repeatFile) == 0:
            message = '暂无重复'
            QMessageBox.about(self, "重复番号", message)
        else:
            self.dataList = repeatFile
            self._loadContext()

    def _changePage(self):
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
        self.post_cover = POSTER
        self._clickSearchButton()

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
        self.curFile = targetfile
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

    def _clickGrid(self):
        text = self.sender().text()
        index = int(text)
        if index > len(self.dataList) - 1:
            return
        self._set_curinfo(index)

    def _clickGridActress(self):
        text = self.sender().text()
        # index = int(text)
        # if index > len(self.actressLib) - 1:
        #     return
        # name = self.actressLib[index][0]
        self.dirName.setText(text)
        self.layoutType = GRID
        self.post_cover = POSTER
        self._clickSearchButton()

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
            logger.error("_load_info_to_left" + str(err))

    # loading 数据
    def _initGrid(self):
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
            showMessage = "【" + data.sizeStr + "】" + data.name
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
                    logger.error("_load_grid_data" + str(err))
                item.setIconSize(QSize(width, 300))
            item.setToolButtonStyle(Qt.ToolButtonIconOnly)
            item.setToolTip(showMessage)
            item.clicked[bool].connect(self._clickGrid)

            item.setContextMenuPolicy(Qt.CustomContextMenu)
            item.customContextMenuRequested.connect(self._rightClick)

            title = QLabel(showMessage)
            title.setMaximumHeight(40)
            title.setWordWrap(True)
            title.setMaximumWidth(width)
            title.setMinimumWidth(width)

            play = QToolButton()
            play.clicked[bool].connect(self._clickPlaybutton)
            play.setText(str(index))
            playPhoto = QPixmap()
            playStr = base64.b64decode(PLAY)
            playPhoto.loadFromData(playStr)
            play.setIcon(QIcon(playPhoto))
            play.setIconSize(QSize(20, 20))
            play.setToolTip("播放")
            play.setToolButtonStyle(Qt.ToolButtonIconOnly)

            info = QToolButton()
            info.clicked[bool].connect(self._clickLocalInfo)
            info.setText(str(index))
            infoPhoto = QPixmap()
            infoStr = base64.b64decode(CHANGE)
            infoPhoto.loadFromData(infoStr)
            info.setIcon(QIcon(infoPhoto))
            info.setIconSize(QSize(20, 20))
            info.setToolTip("详情")
            info.setToolButtonStyle(Qt.ToolButtonIconOnly)

            openF = QToolButton()
            openF.clicked[bool].connect(self._clickOpenButton)
            openF.setText(str(index))
            openPhoto = QPixmap()
            openStr = base64.b64decode(OPEN)
            openPhoto.loadFromData(openStr)
            openF.setIcon(QIcon(openPhoto))
            openF.setIconSize(QSize(20, 20))
            openF.setToolTip("打开文件夹")
            openF.setToolButtonStyle(Qt.ToolButtonIconOnly)

            sync = QToolButton()
            sync.clicked[bool].connect(self._clickSyncButton)
            sync.setText(str(index))
            syncPhoto = QPixmap()
            syncStr = base64.b64decode(REPLAY)
            syncPhoto.loadFromData(syncStr)
            sync.setIcon(QIcon(syncPhoto))
            sync.setIconSize(QSize(20, 20))
            sync.setToolTip("同步")
            sync.setToolButtonStyle(Qt.ToolButtonIconOnly)

            # delete = QToolButton()
            # delete.clicked[bool].connect(self._clickDeleteButton)
            # delete.setText(str(index))
            # deletePhoto = QPixmap()
            # deleteStr = base64.b64decode(CLOSE)
            # deletePhoto.loadFromData(deleteStr)
            # delete.setIcon(QIcon(deletePhoto))
            # delete.setIconSize(QSize(20, 20))
            # delete.setToolTip("删除")
            # delete.setToolButtonStyle(Qt.ToolButtonIconOnly)
            row = int(index / each)
            cols = index % each
            colspan = cols * 4
            rowspan = row * 3 if self.post_cover != NOPIC else row * 2
            if self.post_cover != NOPIC:
                self.gridLayout.addWidget(item, rowspan, colspan, 1, 4)
            self.gridLayout.addWidget(play, rowspan + 1, colspan, 1, 1)
            self.gridLayout.addWidget(info, rowspan + 1, colspan + 1, 1, 1)
            # self.gridLayout.addWidget(delete, rowspan + 1, colspan + 2, 1, 1)
            self.gridLayout.addWidget(openF, rowspan + 1, colspan + 2, 1, 1)
            self.gridLayout.addWidget(sync, rowspan + 1, colspan + 3, 1, 1)
            self.gridLayout.addWidget(title, rowspan + 2, colspan, 1, 4)
        self.gridData.setLayout(self.gridLayout)
        scroll.setWidget(self.gridData)
        scroll.setAutoFillBackground(True)
        return scroll

    def _rightClick(self, point):
        text = self.sender().text()
        self._set_curinfo(int(text))
        self.popMenu = QMenu()
        rename = QAction(u'重命名', self)
        rename.triggered[bool].connect(self._clickRename)
        self.popMenu.addAction(rename)
        delete = QAction(u'删除', self)
        delete.triggered[bool].connect(self._clickDeleteButton)
        self.popMenu.addAction(delete)
        self.showContextMenu(QCursor.pos())

    def showContextMenu(self, pos):
        self.popMenu.move(pos)
        self.popMenu.show()

    def _clickRename(self, slot):
        text, ok = QInputDialog.getText(self, "重命名", "名称:", QLineEdit.Normal, self.curTitle)
        self
        if ok:
            oldpath = self.curFilePath
            if getSuffix(text) is None:
                text = text + "." + self.curFile.fileType
            # 当前文件重命名
            newFileName = self.curDirPath + "\\" + text
            logger.info("重命名:" + oldpath + " => " + newFileName)
            os.rename(oldpath, newFileName)
            self.curFilePath = newFileName
            # 相关文件重命名
            oldsuffix = getSuffix(oldpath)
            if oldsuffix is not None:
                oldsuffix = "." + oldsuffix
                suffixes = ['.jpg', '.png', '.mp4', '.nfo', '.wmv', '.mkv']
                for suffix in suffixes:
                    itempath = oldpath.replace(oldsuffix, suffix)
                    if os.path.exists(itempath):
                        newitempath = newFileName.replace(oldsuffix, suffix)
                        os.rename(itempath, newitempath)

            QMessageBox.about(self, "提示", "重命名成功，请刷新")

    def _initGridActress(self):
        scroll = QScrollArea()
        self.gridData = QWidget()
        self.gridLayout = QGridLayout()
        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().deleteLater()
        width = 120
        each = int(self.tab_widget.width() / width) - 1
        self.actressNames = sorted(self.actressNames, key=lambda x: (x[1], x[0]), reverse=getReverse(self.sortType))
        index = 0
        for item in self.actressNames:

            actressname = item[0]
            tips = actressname + " x" + str(item[1])
            data = self.actressLib[actressname]
            actresspath = data[1]
            item = QToolButton()
            item.setText(actressname)
            try:
                iconPath = replaceSuffix(actresspath, PNG)
                if os.path.exists(iconPath):
                    pass
                else:
                    iconPath = replaceSuffix(actresspath, JPG)
                icon = QIcon(iconPath)
                if icon is not None and not icon.isNull():
                    item.setIcon(icon)
            except Exception as err:
                logger.error("_load_grid_data" + str(err))
            item.setIconSize(QSize(width, 180))
            item.setToolButtonStyle(Qt.ToolButtonIconOnly)
            item.setToolTip(tips)
            item.clicked[bool].connect(self._clickGridActress)
            title = QLabel(tips)
            title.setMaximumHeight(40)
            title.setWordWrap(True)
            title.setMaximumWidth(width)
            title.setMinimumWidth(width)
            row = int(index / each)
            cols = index % each
            colspan = cols * 1
            rowspan = row * 2
            self.gridLayout.addWidget(item, rowspan, colspan, 1, 1)
            self.gridLayout.addWidget(title, rowspan + 1, colspan, 1, 1)
            index += 1
        self.gridData.setLayout(self.gridLayout)
        scroll.setWidget(self.gridData)
        scroll.setAutoFillBackground(True)
        return scroll

    def _initList(self):
        listData = QListWidget()
        item = QListWidgetItem()
        listData.addItem(item)

    # 载入数据 表格形式
    def _initTable(self):
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
        tableData.setColumnWidth(1, 300)
        tableData.setColumnWidth(2, 80)
        tableData.setColumnWidth(3, 200)
        tableData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    def _clickSyncMovie(self):
        '''点击同步数据 按钮'''
        code = self.codeInput.text()
        if code is None or code == '':
            return
            # 获取影片信息
        self._sync_move_movie(self.curDirPath, self.curFilePath, code)

    def _sync_movie_info_new_thread(self, targetfile):
        '''同步数据 开启线程'''
        self._sync_move_movie(targetfile.dirPath, targetfile.path, targetfile.code)

    def _sync_move_movie(self, dirPath, filePath, code):
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
                try:
                    newfilepath = tool.dirpath + "\\" + tool.fileName + "." + getSuffix(filePath)
                    os.rename(filePath, newfilepath)
                    logger.info("文件移动重命名成功:" + newfilepath)
                except OSError as err:
                    message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 移动失败！'
                    logger.error("文件移动失败:" + newfilepath + str(err))
        else:
            message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 同步失败！'
        self.statusBar().showMessage(message)
        # QMessageBox().about(self, "提示", "同步成功!!!")

    def _clickPlaybutton(self):
        '''执行播放'''
        text = self.sender().text()
        self._set_curinfo(int(text))
        if self.curFilePath is None or self.curFilePath == '':
            return
        command = '''start "" "''' + self.curFilePath + "\""
        os.system(command)

    def _clickDeleteButton(self):
        # text = self.sender().text()
        targetfile = self.curFile
        filepath = targetfile.path
        ok = QMessageBox().question(self, "提示", "确定删除 " + targetfile.name, QMessageBox.Yes, QMessageBox.No)
        if ok == QMessageBox.No:
            return
        suffixes = ['.jpg', '.png', '.mp4', '.nfo', '.wmv', '.mkv']
        for suffix in suffixes:
            thispath = filepath.replace('.mp4', suffix)
            if os.path.exists(thispath):
                os.remove(thispath)
        if os.path.getsize(targetfile.dirPath) == 0:
            os.removedirs(targetfile.dirPath)
        QMessageBox().about(self, "提示", "删除成功")

    def _clickOpenButton(self):
        '''执行打开文件夹'''
        text = self.sender().text()
        self._set_curinfo(int(text))
        if self.curDirPath is None or self.curDirPath == '':
            return
        command = '''start "" "''' + self.curDirPath
        os.system(command)

    def _clickSyncButton(self):
        '''执行同步数据'''
        text = self.sender().text()
        targetfile = self.dataList[int(text)]
        _thread.start_new_thread(self._sync_move_movie, (targetfile.dirPath, targetfile.path, targetfile.code))

    def _clickInfo(self):
        self.dirName.setText(self.curActress)
        self.layoutType = GRID
        self.post_cover = POSTER
        self._clickSearchButton()

    def _openNewWindow(self, javMovie):
        try:
            self.info = InfoUI(javMovie)
            self.info.show()
        except Exception as err:
            logger.error('弹窗失败 ' + str(err))

    def _clickLocalInfo(self):

        text = self.sender().text()
        if text:
            targetFile = self.dataList[int(text)]
            curFilePath = targetFile.path
            # self._set_curinfo(int(text))
        javMovie = None
        nfoPath = replaceSuffix(curFilePath, 'nfo')
        if nfoPath is not None and nfoPath != '' and os.path.exists(nfoPath):
            javMovie = nfoToJavMovie(nfoPath)
        if javMovie is not None:
            self._openNewWindow(javMovie)

    # 添加菜单按钮
    def _initMenuButton(self):
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
        file.triggered[QAction].connect(self._clickMenu)
        # 设置
        changeUrlAction = QAction("切换数据源", self)
        changePageSizeAction = QAction("切换分页", self)

        setting = bar.addMenu("设置")
        setting.setShortcutEnabled(1)
        setting.addAction(changeUrlAction)
        setting.addAction(changePageSizeAction)
        setting.triggered[QAction].connect(self._clickMenu)

        clearDisk = QAction("清空路径", self)
        clearDisk.setShortcut(QKeySequence.Save)
        scanDisk = QAction("扫描路径", self)
        repeatCheck = QAction("重复校验", self)
        openAction.triggered[bool].connect(self._open_path)
        scanDisk.triggered[bool].connect(self._searchDisk)
        clearDisk.triggered[bool].connect(self._clickClearPath)
        repeatCheck.triggered[bool].connect(self._repeatCheck)
        self.fileAct.addAction(openAction)
        self.fileAct.addAction(clearDisk)
        self.fileAct.addAction(scanDisk)
        self.fileAct.addAction(repeatCheck)

    # 菜单按钮处理
    def _clickMenu(self, action):
        if action.text() == "退出":
            self.close()
        if action.text() == "切换数据源":
            text, ok = QInputDialog.getText(self, "设置数据源", "网址:")
            if ok:
                self.webUrl = text
                self.webUrlLable.setText(text)
                logger.info("切换数据源:" + text)
            return
        elif action.text() == "切换分页":
            text, ok = QInputDialog.getText(self, "切换分页", "每页显示:")
            if ok:
                self.pageSize = int(text)
                logger.info("切换分页:" + text)
            return
        elif action.text() == "扫描路径":
            self._searchDisk()
            logger.info("扫描路径")
        elif action.text() == "清空路径":
            self._clickClearPath()
            logger.info("清空路径")

    # 点击图片box

    def _chooseImage(self, state):

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
    def _chooseVideo(self, state):

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

    def _chooseDocs(self, state):

        if state == Qt.Checked:
            self.docsToggle = 1
            if not set(DOCS_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(DOCS_TYPES)
        else:
            self.docsToggle = 0
            if set(DOCS_TYPES) < set(self.fileTypes):
                for doc in DOCS_TYPES:
                    self.fileTypes.remove(doc)
