#!/usr/bin/python3

import sys

from PyQt5.QtWidgets import QApplication

from .ui.mainWindow import SearchDir

app = QApplication(sys.argv)
sd = SearchDir()
sys.exit(app.exec_())
