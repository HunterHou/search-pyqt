#!/usr/bin/python3

import os
import sys

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5.QtWidgets import QApplication

from search.ui.mainUI import MainUI

try:
    app = QApplication(sys.argv)
    sd = MainUI()
    sys.exit(app.exec_())
except Exception as err:
    print(err)
