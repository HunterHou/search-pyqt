#!/usr/bin/python3
import _thread
import base64
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
    layoutType = '栅格'
    # 0 海报模式 还是 1 封面模式
    post_cover = POSTER

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

    # 默认勾选
    curTaskCount = 0
    imageToggle = 0
    videoToggle = 1
    docsToggle = 1
    sortType = DESC
    sortField = MODIFY_TIME
    webUrl = "https://www.cdnbus.in/"

    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        # self.rootPath = getPath()
        self.infoLayout = QHBoxLayout()
        self.tableData = QTableWidget()
        self.codeInput = QLineEdit()
        self.titleInput = QTextEdit()
        self.actressInput = QLineEdit()
        self._initUI()
        self._search_from_disk()

    # 载入UI窗口
    def _initUI(self):
        self.setWindowTitle("文件目录")
        self.resize(1400, 900)
        # 创建搜索按钮
        if self.dirName is None:
            self.dirName = QLineEdit()
        scanFolder = QPushButton("扫描路径")
        # openFolder.setShortcut(QKeySequence.Open)
        scanFolder.clicked[bool].connect(self._scan_disk)
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
        syncJav.clicked[bool].connect(self._sync_javmovie_info)

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
        if self.post_cover == POSTER:
            postButton.toggle()
        elif self.post_cover == COVER:
            coverButton.toggle()
        postButton.clicked[bool].connect(self._choose_post_cover)
        coverButton.clicked[bool].connect(self._choose_post_cover)
        self.displayGroup = QButtonGroup()
        self.displayGroup.addButton(postButton, 0)
        self.displayGroup.addButton(coverButton, 1)

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
        name = QRadioButton(NAME)
        size = QRadioButton(SIZE)
        mtime = QRadioButton(MODIFY_TIME)
        if self.sortField == NAME:
            name.toggle()
        elif self.sortField == SIZE:
            size.toggle()
        elif self.sortField == MODIFY_TIME:
            mtime.toggle()
        name.clicked[bool].connect(self._sort_field_change)
        size.clicked[bool].connect(self._sort_field_change)
        mtime.clicked[bool].connect(self._sort_field_change)
        self.sortFieldGroup = QButtonGroup()
        self.sortFieldGroup.addButton(name, 0)
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

        left_layout.addWidget(QLabel("数据源:"), 0, 0, 1, 1)
        self.webUrlLable = QLabel(self.webUrl)
        left_layout.addWidget(self.webUrlLable, 0, 1, 1, 2)
        left_layout.addWidget(scanFolder, 1, 0, 1, 1)
        self.diskLabel = QLabel(getStrJoin(self.rootPath))
        self.diskLabel.setWordWrap(True)
        left_layout.addWidget(self.diskLabel, 1, 1, 1, 2)
        left_layout.addWidget(QLabel(""), 2, 0, 1, 3)

        left_layout.addWidget(grid_layout, 3, 0)
        left_layout.addWidget(table_layout, 3, 1)
        left_layout.addWidget(web_layout, 3, 2)
        left_layout.addWidget(image, 4, 0)
        left_layout.addWidget(video, 4, 1)
        left_layout.addWidget(docs, 4, 2)

        left_layout.addWidget(self.dirName, 5, 0, 1, 2)
        left_layout.addWidget(okButton, 5, 2, 1, 1)

        left_layout.addWidget(postButton, 6, 0, 1, 1)
        left_layout.addWidget(coverButton, 6, 1, 1, 1)

        left_layout.addWidget(QLabel('排序类型'), 7, 0, 1, 1)
        left_layout.addWidget(asc, 7, 1, 1, 1)
        left_layout.addWidget(desc, 7, 2, 1, 1)
        left_layout.addWidget(name, 8, 0, 1, 1)
        left_layout.addWidget(size, 8, 1, 1, 1)
        left_layout.addWidget(mtime, 8, 2, 1, 1)
        left_layout.addWidget(QLabel(""), 9, 0, 1, 3)
        left_layout.addWidget(infoButton, 10, 0, 1, 1)
        left_layout.addWidget(codeSearch, 10, 2, 1, 1)
        left_layout.addWidget(QLabel("番号"), 11, 0, 1, 1)
        left_layout.addWidget(self.codeInput, 11, 1, 1, 2)

        left_layout.addWidget(QLabel("标题"), 12, 0, 1, 1)
        self.titleInput.setMaximumHeight(60)
        self.titleInput.setMaximumWidth(160)
        left_layout.addWidget(self.titleInput, 12, 1, 2, 2)
        left_layout.addWidget(QLabel("演员"), 14, 0, 1, 1)
        left_layout.addWidget(self.actressInput, 14, 1, 1, 2)
        self.curPic = QLabel()
        left_layout.addWidget(self.curPic, 15, 0, 15, 3)
        left_layout.addWidget(openFile)
        left_layout.addWidget(openDir)
        left_layout.addWidget(syncJav)

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
        main_layout.addWidget(left_widget, 0, 1, 1, 16)
        main_layout.addWidget(self.tab_widget, 0, 0, 1, 1)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self._menu_button_add()

        self.show()

    # 点击搜索

    def _search_button_click(self):
        self.statusBar().showMessage('执行中')
        # 提示框测试
        # replay = QMessageBox.question(self, '提示',
        #                               self.dirName.text(), QMessageBox.Yes)
        # if replay == QMessageBox.Yes:
        title = self.dirName.text()
        # if title is None or title == '':
        #     self.statusBar().showMessage('等待执行...')
        #     return
        self._search_from_result(title)
        totalSize = 0
        for data in self.dataList:
            if data.size:
                totalSize += data.size
        message = '文件:' + str(len(self.dataList)) + " 合计：" + getSizeFromNumber(totalSize) + '   执行完毕！！！'
        self.statusBar().showMessage(message)
        self._load_context()

    def _choose_post_cover(self):
        #  0 海报 1 封面
        self.post_cover = self.displayGroup.checkedButton().text()
        # index = self.tab_widget.currentIndex()
        # self.tab_widget.removeTab(self.tab_widget.count() - 1)
        if self.layoutType == GRID:
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
            self._sort_files_list()
            self._load_context_thread(isNew)
        except Exception as err:
            print("_load_context")
            print(err)
        # if __name__ == 'search.ui.mainUI':
        #     freeze_support()
        #     pool = Pool(processes=1)
        #     pool.map_async(, [])
        #     pool.close()
        #     pool.join()

    def _load_context_thread(self, isNew):
        title = self.dirName.text()
        if self.layoutType == WEB:
            # 打开浏览器
            webbrowser.open(self.webUrl)
            # self.webview = WebEngineView(self)  # self必须要有，是将主窗口作为参数，传给浏览器
            # self.webview.load(QUrl("http://www.baidu.com"))
            # self.addAloneTab(self.loadGridData(), "栅格")
            return
        if self.layoutType == '栅格':
            gridData = self._load_grid_data()
            if isNew:
                self._tab_add(gridData, title)
            else:
                self.tab_widget.setCurrentWidget(gridData)
        elif self.layoutType == '表格':
            tableData = self._load_table_data()
            if isNew:
                self._tab_add(tableData, title)
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
    def _search_from_result(self, word):
        result = []
        for files in self.dataLib:
            if (files.name is not None and files.name.find(word) >= 0) or (
                    files.code is not None and files.code.find(word) >= 0) or (
                    files.actress is not None and files.actress.find(word) >= 0) or word == '' or word is None:
                if files.fileType in self.fileTypes:
                    result.append(files)
        self.dataList = result

    # 填充数据
    def _search_from_disk(self):
        self.dataLib = []
        for path in self.rootPath:
            if os.path.exists(path):
                walk = FileService().build(path, self.fileTypes)
                curList = walk.getFiles()
                self.dataLib.extend(curList)
        self.dataList = self.dataLib

    def _scan_disk(self):
        self._search_from_disk()
        self._search_button_click()

    def _sort_files_list(self):
        if len(self.dataList) > 0:
            print('排序：' + self.sortField + ' ' + self.sortType)
            self.dataList.sort(key=getSortField(self.sortField), reverse=getReverse(self.sortType))

    def _tab_item_close(self, index):
        # self.tab_widget.removeTab(index)
        self.tab_widget.removeTab(index)
        del self.tabDataList[index]

    def _tab_close(self, index):
        self._tab_item_close(index)
        index = self.tab_widget.currentIndex()
        print("当前页:" + str(index))
        print("Tab总数:" + str(len(self.tabDataList)))
        if index > 0:
            self.dataList = self.tabDataList[index]

    def _tab_change(self, index):
        self.dataList = self.tabDataList[index]

    def _tab_add(self, widget, title):
        """ # 单页应用 添加前删除所有Tab页"""
        # for index in range(self.tab_widget.count()):
        #     # 删除Tab页时 同步删除当前Tab页对应的数据
        #     self.close_Tab_item(index)
        try:
            self.tabDataList.append(self.dataList)
            self.tab_widget.addTab(widget, title)
            self.tab_widget.setCurrentWidget(widget)
        except Exception as err:
            print("_tab_add")
            print(err)

    # 选择框
    def _open_path(self):
        pathname = QFileDialog.getExistingDirectory(self, "选择文件夹", "E:\\")
        # if not pathname:
        #     QMessageBox().about(self, "提示", "打开文件失败，可能是文件内型错误")
        # else:
        self.rootPath.append(pathname)

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
        self._set_curinfo(self.dataList[index])
        self._load_info_to_left()

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

    def _set_curinfo(self, targetfile):
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

    def _grid_click(self):
        text = self.sender().text()
        self._set_curinfo(self.dataList[int(text)])
        self._load_info_to_left()

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
                pic = getPixMapFromNet(self.curPicUrl, 250, 400)
                if pic is not None and not pic.isNull():
                    self.curPic.setPixmap(pic)
            else:
                pic = getPixMap(self.curFilePath, 250, 400)
                if pic is not None and not pic.isNull():
                    self.curPic.setPixmap(pic)

        except Exception as err:
            print("_load_info_to_left")
            print("文件打开失败")
            print(err)

    # loading 数据
    def _load_grid_data(self):
        scroll = QScrollArea()
        self.gridData = QWidget()
        self.gridLayout = QGridLayout()
        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().deleteLater()
        width = 200 if self.post_cover == POSTER else 500
        each = int(self.tab_widget.width() / width)
        for index in range(len(self.dataList)):
            data = self.dataList[index]
            item = QToolButton()
            item.setText(str(index))
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
            title = QTextEdit(data.name)
            title.setMaximumHeight(40)
            title.setMaximumWidth(width)

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
            colscols = cols * 3

            self.gridLayout.addWidget(item, row * 3, colscols, 1, 3)
            self.gridLayout.addWidget(play, row * 3 + 1, colscols, 1, 1)
            self.gridLayout.addWidget(openF, row * 3 + 1, colscols + 1, 1, 1)
            self.gridLayout.addWidget(sync, row * 3 + 1, colscols + 2, 1, 1)
            self.gridLayout.addWidget(title, row * 3 + 2, colscols, 1, 3)
        self.gridData.setLayout(self.gridLayout)
        scroll.setWidget(self.gridData)
        scroll.setAutoFillBackground(True)
        return scroll

    # 载入数据 表格形式
    def _load_table_data(self):
        tableData = self.tableData
        tableData.setRowCount(0)
        tableData.setColumnCount(0)
        tableData.setColumnCount(8)
        tableData.setRowCount(len(self.dataList))
        # 自适应列宽度

        tableData.setHorizontalHeaderLabels(['图片', NAME, "番号", "路径", "优优", "大小", "创建时间", "修改时间"])
        tableData.doubleClicked.connect(self._table_line_double_click)
        tableData.itemClicked.connect(self._table_line_click)
        tableData.setColumnWidth(0, 200)
        tableData.setColumnWidth(1, 180)
        tableData.setColumnWidth(2, 80)
        tableData.setColumnWidth(3, 200)
        # tableData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for index in range(len(self.dataList)):
            tableData.setRowHeight(index, 300)
            file = self.dataList[index]
            row_id = index
            row_name = QLabel()
            pic = getPixMap(file.path, 200, 300)
            if pic is not None:
                row_name.setPixmap(pic)
            tableData.setCellWidget(row_id, 0, row_name)
            tableData.setItem(row_id, 1, QTableWidgetItem(file.name))
            tableData.setItem(row_id, 2, QTableWidgetItem(file.code))
            tableData.setItem(row_id, 3, QTableWidgetItem(file.path))
            tableData.setItem(row_id, 4, QTableWidgetItem(file.actress))
            tableData.setItem(row_id, 5, QTableWidgetItem(file.size))
            tableData.setItem(row_id, 6, QTableWidgetItem(file.create_time))
            tableData.setItem(row_id, 7, QTableWidgetItem(file.modify_time))

        return tableData

    # 同步数据
    def _sync_javmovie_info(self):
        code = self.codeInput.text()
        if code is None or code == '':
            return
            # 获取影片信息
        self.curTaskCount = self.curTaskCount + 1
        message = "当前任务数:" + str(self.curTaskCount) + "【" + code + '】 添加成功！'
        self.statusBar().showMessage(message)
        tool = JavTool(self.webUrl)
        movie = tool.getJavInfo(code)
        self._sync_move_movie(self.curDirPath, self.curFilePath, movie, tool)

    def _sync_move_movie(self, dirPath, filePath, movie, tool):
        '''  同步数据并移动  '''
        if movie is None:
            # QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
            self.curTaskCount = self.curTaskCount - 1
            message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 匹配失敗！'
            self.statusBar().showMessage(message)
            return
        if tool is None:
            tool = JavTool(self.webUrl)
        # 生成目录下载图片并切图png
        tool.makeActress(dirPath, movie)
        # 移动源文件到目标目录 并重命名
        if tool.dirpath is not None and tool.fileName is not None:
            os.rename(filePath, tool.dirpath + "\\" + tool.fileName + "." + getSuffix(filePath))
        # shutil.move(, )
        self.curTaskCount = self.curTaskCount - 1
        message = "当前任务数:" + str(self.curTaskCount) + "【" + movie.title + '】 同步成功！'
        self.statusBar().showMessage(message)
        # QMessageBox().about(self, "提示", "同步成功!!!")

    def _click_play_button(self):
        text = self.sender().text()
        self._set_curinfo(self.dataList[int(text)])
        self._load_info_to_left()
        if self.curFilePath is None or self.curFilePath == '':
            return
        command = '''start "" "''' + self.curFilePath + "\""
        os.system(command)

    def _click_openF_button(self):
        text = self.sender().text()
        self._set_curinfo(self.dataList[int(text)])
        self._load_info_to_left()
        if self.curDirPath is None or self.curDirPath == '':
            return
        command = '''start "" "''' + self.curDirPath
        os.system(command)

    def _click_sync_button(self):
        text = self.sender().text()
        targetfile = self.dataList[int(text)]
        _thread.start_new_thread(self._sync_thread, (targetfile,))

    def _sync_thread(self, targetfile):
        self.curTaskCount = self.curTaskCount + 1
        message = "当前任务数:" + str(self.curTaskCount) + "【" +  targetfile.code + '】 添加成功！'
        self.statusBar().showMessage(message)
        tool = JavTool(self.webUrl)
        movie = tool.getJavInfo(targetfile.code)
        self._sync_move_movie(targetfile.dirPath, targetfile.path, movie, tool)

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
        file = bar.addMenu("文件")
        file.setShortcutEnabled(1)
        openAction = QAction("打开", self)
        openAction.setShortcut(QKeySequence.Open)
        file.addAction(openAction)

        quitAction = QAction("退出", self)
        quitAction.setShortcut(QKeySequence(str("ctrl+Q")))

        addDisk = QAction("添加路径", self)
        addDisk.setShortcut(QKeySequence.Save)
        file.addAction(addDisk)

        clearDisk = QAction("清空路径", self)
        clearDisk.setShortcut(QKeySequence.Save)
        file.addAction(clearDisk)

        file.addAction(quitAction)
        file.triggered[QAction].connect(self._menu_process_file)
        # 设置
        setting = bar.addMenu("设置")
        setting.setShortcutEnabled(1)
        changeUrlAction = QAction("切换数据源", self)
        setting.addAction(changeUrlAction)

        setting.triggered[QAction].connect(self._menu_process_file)

    # 菜单按钮处理
    def _menu_process_file(self, action):
        if action.text() == "打开":
            self._open_path()
        if action.text() == "退出":
            self.close()
        if action.text() == "切换数据源":
            text, ok = QInputDialog.getText(self, "设置数据源", "网址:")
            if ok:
                self.webUrl = text
                self.webUrlLable.setText(text)
        if action.text() == "添加路径":
            self._open_path()
            self.diskLabel.setText(getStrJoin(self.rootPath))
            self._search_from_disk()
        if action.text() == "清空路径":
            self.rootPath = []
            self.dataLib = []
            self.dataList = []
            self.diskLabel.setText("暂无路径")
            self._search_from_disk()

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
