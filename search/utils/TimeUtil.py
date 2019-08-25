#!/usr/bin/python3
import datetime


def getFormatTime(longTime):
    local = datetime.datetime.fromtimestamp(longTime)
    return local.strftime("%Y-%m-%d %H:%M:%S")
