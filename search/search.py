#!/usr/bin/python3
# encoding=utf-8

import logging
import os
import sys

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5.QtWidgets import QApplication
from search.ui.mainUI import MainUI


# pyinstaller.exe -F -w   .\search.py

def loggerInit():
    rootLevel = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
    logger = logging.getLogger("search")
    logger.setLevel(rootLevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console = logging.StreamHandler()
    console.setLevel(rootLevel)
    filehandler = logging.FileHandler("search.log", mode='a', encoding=None, delay=False)
    filehandler.setLevel(rootLevel)
    # 定义handler的输出格式
    console.setFormatter(formatter)
    filehandler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(filehandler)


def main():
    try:
        loggerInit()
        app = QApplication(sys.argv)
        logging.info("服务启动中...")
        sd = MainUI()
        sys.exit(app.exec_())
    except Exception as err:
        logging.error("主线程错误" + str(err))


if __name__ == '__main__':
    main()
