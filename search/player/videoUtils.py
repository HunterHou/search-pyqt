#!/usr/bin/python3
# encoding=utf-8

import os

filename = "e:\\1.mp4"

if os.path.exists(filename):
    os.system("start " + filename)
