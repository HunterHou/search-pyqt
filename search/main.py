#!/usr/bin/python3

import sys
import os
from PyQt5.QtWidgets import QApplication
from .ui.mainWindow import SearchDir

app = QApplication(sys.argv)
sd= SearchDir()
sys.exit(app.exec_())