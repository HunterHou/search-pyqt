#!/usr/bin/python3
# encoding=utf-8

import logging
import os
import sys

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5.QtWidgets import QApplication
from search.ui.mainUI import MainUI


def main():
    try:
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filename="search.log")

        app = QApplication(sys.argv)
        sd = MainUI()
        sys.exit(app.exec_())
    except Exception as err:
        print("主线程错误")
        print(err)


if __name__ == '__main__':
    main()
