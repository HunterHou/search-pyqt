#!/usr/bin/python3
import webbrowser

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from search.model.file import *
from search.net.javTool import JavTool
from search.service.fileService import FileService, nfoToJavMovie
from search.ui.infoUI import InfoUI


class MainUI(QMainWindow):
    # 初始化 loadUI
    def __init__(self):
        super().__init__()
        self.infoLayout = QHBoxLayout()
        self.tableData = QTableWidget()
        self.codeInput = QLineEdit()
        self.titleInput = QTextEdit()
        self.actressInput = QLineEdit()
        self._initUI()
        self._click_search_button()

    # 定义全局变量
    tabDataList = []
    dataList = []
    rootPath = ''
    fileTypes = []
    # 载入数据
    # 布局 0 栅格 1 表格 3 网页
    layoutType = '栅格'
    # 0 海报模式 还是 1 封面模式
    post_cover = POSTER

    tableData = None
    codeInput = None
    titleInput = None
    actressInput = None
    curCode = None
    curActress = None
    curFilePath = None
    curDirPath = None
    curTitle = None
    sortType = DESC
    sortField = MODIFY_TIME
    # 默认勾选
    imageToggle = 0
    videoToggle = 1
    docsToggle = 0

    webUrl = "https://www.cdnbus.in/"

    # 搜索文本框
    dirName = None

    # 载入UI窗口
    def _initUI(self):
        self.setWindowTitle("文件目录")
        self.resize(1400, 900)
        # 创建搜索按钮
        if self.dirName is None:
            self.dirName = QLineEdit()
        openFolder = QPushButton("点我")
        # openFolder.setShortcut(QKeySequence.Open)
        openFolder.clicked[bool].connect(self._open_path)
        okButton = QPushButton("搜索")
        okButton.setShortcut(QKeySequence(str("Return")))
        okButton.clicked[bool].connect(self._click_search_button)

        openFile = QPushButton("打开文件")
        openFile.clicked[bool].connect(self._open_file)
        openDir = QPushButton("打开文件夹")
        openDir.clicked[bool].connect(self._open_file)
        codeSearch = QPushButton("番号搜索")
        codeSearch.clicked[bool].connect(self._code_search)
        infoButton = QPushButton("info")
        infoButton.clicked[bool].connect(self._click_info)

        syncJav = QPushButton("数据同步")
        syncJav.clicked[bool].connect(self._sync_javmovie_info)

        # 布局 0 栅格 1 表格 3 网页
        grid_layout = QRadioButton("栅格")
        web_layout = QRadioButton("网页")
        table_layout = QRadioButton("表格")
        if self.layoutType == "栅格":
            grid_layout.toggle()
        elif self.layoutType == "表格":
            table_layout.toggle()
        elif self.layoutType == "网页":
            web_layout.toggle()
        grid_layout.clicked[bool].connect(self._choose_layout)
        table_layout.clicked[bool].connect(self._choose_layout)
        web_layout.clicked[bool].connect(self._choose_layout)
        self.layoutGroup = QButtonGroup()
        self.layoutGroup.addButton(grid_layout, 0)
        self.layoutGroup.addButton(table_layout, 1)
        self.layoutGroup.addButton(web_layout, 2)

        postButton = QRadioButton("海报")
        coverButton = QRadioButton("封面")
        if self.post_cover == POSTER:
            postButton.toggle()
        elif self.post_cover == '封面':
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
        image.stateChanged.connect(self._image_choose)
        video = QCheckBox("视频", self)
        video.stateChanged.connect(self._video_choose)
        docs = QCheckBox("文档", self)
        docs.stateChanged.connect(self._docs_choose)
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
        left_layout.addWidget(web_layout, 0, 2)
        left_layout.addWidget(image, 1, 0)
        left_layout.addWidget(video, 1, 1)
        left_layout.addWidget(docs, 1, 2)

        left_layout.addWidget(openFolder, 2, 0, 1, 1)
        left_layout.addWidget(self.dirName, 2, 1, 1, 2)

        left_layout.addWidget(postButton, 3, 0, 1, 1)
        left_layout.addWidget(coverButton, 3, 1, 1, 1)
        left_layout.addWidget(okButton, 3, 2, 1, 1)
        left_layout.addWidget(infoButton, 4, 0, 1, 1)
        left_layout.addWidget(codeSearch, 4, 2, 1, 1)

        left_layout.addWidget(QLabel(""), 5, 0, 1, 3)

        left_layout.addWidget(QLabel('排序类型'), 6, 0, 1, 1)
        left_layout.addWidget(asc, 6, 1, 1, 1)
        left_layout.addWidget(desc, 6, 2, 1, 1)
        left_layout.addWidget(name, 7, 0, 1, 1)
        left_layout.addWidget(size, 7, 1, 1, 1)
        left_layout.addWidget(mtime, 7, 2, 1, 1)

        left_layout.addWidget(QLabel(""), 8, 0, 1, 3)

        left_layout.addWidget(QLabel("番号"))
        left_layout.addWidget(self.codeInput)

        left_layout.addWidget(QLabel("标题"), 11, 0, 1, 1)
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

        left_layout.addWidget(QLabel("数据源:"))
        self.webUrlLable = QLabel(self.webUrl)
        left_layout.addWidget(self.webUrlLable)

        # 创建右侧组件
        self.tab_widget = QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabShape(QTabWidget.Triangular)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._change_tab)

        # 创建主窗口组件 挂载布局
        main_widget = QWidget()
        main_layout = QGridLayout()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 0, 1, 1, 16)
        main_layout.addWidget(self.tab_widget, 0, 0, 1, 1)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self._add_menu_button()

        self.show()

    # 点击搜索

    def _click_search_button(self):
        self.statusBar().showMessage('执行中')
        # 提示框测试
        # replay = QMessageBox.question(self, '提示',
        #                               self.dirName.text(), QMessageBox.Yes)
        # if replay == QMessageBox.Yes:
        title = self.dirName.text()
        if title is None or title == '':
            return
        self._search(title)
        message = '总数:' + str(len(self.dataList)) + '   执行完毕！！！'
        self.statusBar().showMessage(message)
        self._reload_context()

    def _choose_post_cover(self):
        #  0 海报 1 封面
        self.post_cover = self.displayGroup.checkedButton().text()
        # index = self.tab_widget.currentIndex()
        # self.tab_widget.removeTab(self.tab_widget.count() - 1)
        self._reload_context()

    def _sort_type_change(self):
        print(self.sortTypeGroup.checkedButton().text())
        self.sortType = self.sortTypeGroup.checkedButton().text()
        self._reload_context()

    def _sort_field_change(self):
        print(self.sortFieldGroup.checkedButton().text())
        self.sortField = self.sortFieldGroup.checkedButton().text()
        self._reload_context()

    # 选择布局
    def _choose_layout(self):
        # 布局 0 栅格 1 表格 3 网页
        self.layoutType = self.layoutGroup.checkedButton().text()
        self._reload_context()

    def _reload_context(self):
        try:
            self._sort_files_list()
            self._load_context_thread()
        except Exception as err:
            print(err)
        # if __name__ == 'search.ui.mainUI':
        #     freeze_support()
        #     pool = Pool(processes=1)
        #     pool.map_async(, [])
        #     pool.close()
        #     pool.join()

    def _load_context_thread(self):
        title = self.dirName.text()
        if title is None or title == '':
            if self.layoutType == WEB:
                # 打开浏览器
                webbrowser.open(self.webUrl)
                # self.webview = WebEngineView(self)  # self必须要有，是将主窗口作为参数，传给浏览器
                # self.webview.load(QUrl("http://www.baidu.com"))
                # self.addAloneTab(self.loadGridData(), "栅格")
        else:
            if self.layoutType == '栅格':
                self._this_add_tab(self._load_grid_data(), title)
            elif self.layoutType == '表格':
                self._this_add_tab(self._load_table_data(), title)

    def _this_add_tab(self, widget, title):
        # # 单页应用 添加前删除所有Tab页
        # for index in range(self.tab_widget.count()):
        #     # 删除Tab页时 同步删除当前Tab页对应的数据
        #     self.close_Tab_item(index)
        self.tab_widget.addTab(widget, title)
        self.tab_widget.setCurrentWidget(widget)

    # 搜饭
    def _code_search(self):
        tool = JavTool(self.webUrl)
        code = self.codeInput.text()
        movie = tool.getJavInfo(code)
        if movie is None:
            QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
        else:
            self.curCode = code
            self.curActress = movie.getActress()
            self.curFilePath = movie.cover
            self.curTitle = movie.title
            self._load_info_to_left()

    # 填充数据
    def _search(self, path):

        walk = FileService().build(path, self.fileTypes)
        self.dataList = []
        self.dataList = walk.getFiles()
        self.tabDataList.append(self.dataList)

    def _sort_files_list(self):
        if len(self.dataList) > 0:
            print('排序：' + self.sortField + ' ' + self.sortType)
            self.dataList.sort(key=getSortField(self.sortField), reverse=getReverse(self.sortType))

    def _close_tab_item(self, index):
        self.tab_widget.removeTab(index)
        del self.tabDataList[index]

    def _close_tab(self, index):
        self._close_tab_item(index)
        index = self.tab_widget.currentIndex()
        self.dataList = self.tabDataList[index]

    def _change_tab(self, index):
        self.dataList = self.tabDataList[index]

    # 选择框
    def _open_path(self):
        pathname = QFileDialog.getExistingDirectory(self, "选择文件夹", "E:\\")
        # if not pathname:
        #     QMessageBox().about(self, "提示", "打开文件失败，可能是文件内型错误")
        # else:
        self.dirName.setText(pathname)
        self._click_search_button()

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
            command = '''start "" "''' + self.curDirPath + "\""
            os.system(command)

    # 点击事件
    def _click_table_line(self):
        index = self.tableData.currentRow()
        self._set_curinfo(self.dataList[index])
        self._load_info_to_left()

    def _click_table_line_double(self):
        self._click_table_line()
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
        self.curCode = targetfile.code
        self.curActress = targetfile.actress
        self.curFilePath = targetfile.path
        self.curDirPath = targetfile.dirPath
        self.curTitle = targetfile.name

    def _click_grid(self):
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
            path = self.curFilePath
            if path.find("http") < 0:
                pic = getPixMap(path, 250, 400)
                if not pic.isNull():
                    self.curPic.setPixmap(pic)
            else:
                pic = getPixMapFromNet(path, 250, 400)
                if not pic.isNull():
                    self.curPic.setPixmap(pic)
        except Exception as err:
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
            iconPath = replaceSuffix(data.path, PNG if self.post_cover == POSTER else JPG)
            icon = QIcon(iconPath)
            if not icon.isNull():
                item.setIcon(icon)
            item.setIconSize(QSize(width, 300))
            item.setToolButtonStyle(Qt.ToolButtonIconOnly)
            item.setToolTip(data.name)
            item.clicked[bool].connect(self._click_grid)
            row = int(index / each)
            cols = index % each
            title = QTextEdit(data.name)
            title.setMaximumHeight(40)
            title.setMaximumWidth(200)
            self.gridLayout.addWidget(item, row * 2, cols)
            self.gridLayout.addWidget(title, row * 2 + 1, cols)
        self.gridData.setLayout(self.gridLayout)
        scroll.setWidget(self.gridData)
        scroll.setAutoFillBackground(True)
        return scroll

    # 载入数据 表格形式
    def _load_table_data(self):
        tableData = self.tableData
        tableData.setRowCount(0)
        tableData.setColumnCount(0)
        if len(self.dataList) == 0:
            self._search(self.rootPath)
        tableData.setColumnCount(8)
        tableData.setRowCount(len(self.dataList))
        # 自适应列宽度

        tableData.setHorizontalHeaderLabels(['图片', NAME, "番号", "路径", "优优", "大小", "创建时间", "修改时间"])
        tableData.doubleClicked.connect(self._click_table_line_double)
        tableData.itemClicked.connect(self._click_table_line)
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
        tool = JavTool(self.webUrl)
        code = self.codeInput.text()
        if code is None or code == '':
            return
            # 获取影片信息
        movie = tool.getJavInfo(code)
        if movie is None:
            QMessageBox().about(self, "提示", "匹配不到影片，请检查番号")
            return
        # 生成目录下载图片并切图png
        tool.makeActress(self.curDirPath, movie)
        # 移动源文件到目标目录 并重命名
        if tool.dirpath is not None and tool.fileName is not None:
            os.rename(self.curFilePath, tool.dirpath + "\\" + tool.fileName + "." + getSuffix(self.curFilePath))
        # shutil.move(, )
        QMessageBox().about(self, "提示", "同步成功!!!")

    def _click_info(self):

        javMovie = None
        nfoPath = replaceSuffix(self.curFilePath, 'nfo')
        if nfoPath is not None and nfoPath != '':
            javMovie = nfoToJavMovie(nfoPath)
        elif self.codeInput.text() is not None and self.codeInput.text() != '':
            tool = JavTool(self.webUrl)
            javMovie = tool.getJavInfo(self.codeInput.text())
        if javMovie is not None:
            info = InfoUI(javMovie)
            self._this_add_tab(info, javMovie.code)

    # 添加菜单按钮
    def _add_menu_button(self):
        bar = self.menuBar()
        # 文件
        file = bar.addMenu("文件")
        file.setShortcutEnabled(1)
        openAction = QAction("打开", self)
        openAction.setShortcut(QKeySequence.Open)
        file.addAction(openAction)
        quitAction = QAction("退出", self)
        quitAction.setShortcut(QKeySequence(str("ctrl+Q")))
        file.addAction(quitAction)

        file.triggered[QAction].connect(self._file_menu_process)
        # 设置
        setting = bar.addMenu("设置")
        setting.setShortcutEnabled(1)
        changeUrlAction = QAction("切换数据源", self)
        changeUrlAction.setShortcut(QKeySequence.Save)
        setting.addAction(changeUrlAction)
        setting.triggered[QAction].connect(self._file_menu_process)

    # 菜单按钮处理
    def _file_menu_process(self, action):
        if action.text() == "打开":
            self._open_path()
        if action.text() == "退出":
            self.close()
        if action.text() == "切换数据源":
            text, ok = QInputDialog.getText(self, "设置数据源", "网址:", )
            if ok:
                self.webUrl = text
                self.webUrlLable.setText(text)

    # 点击图片box

    def _image_choose(self, state):

        if state == Qt.Checked:
            self.imageToggle = 1
            if not set(IMAGE_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(IMAGE_TYPES)
        else:
            self.imageToggle = 0
            if set(IMAGE_TYPES) < set(self.fileTypes):
                if set(VIDEO_TYPES) < set(self.fileTypes):
                    for image in IMAGE_TYPES:
                        self.fileTypes.remove(image)

    # 点击视频box
    def _video_choose(self, state):

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
    def _docs_choose(self, state):

        if state == Qt.Checked:
            self.docsToggle = 1
            if not set(DOCS_TYPES) < set(self.fileTypes):
                self.fileTypes.extend(DOCS_TYPES)
        else:
            self.docsToggle = 0
            if not set(DOCS_TYPES) < set(self.fileTypes):
                for doc in DOCS_TYPES:
                    self.fileTypes.remove(doc)
