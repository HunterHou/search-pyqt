#!/usr/bin/python3
# encoding=utf-8
from urllib import request


def download(url, pathname):
    fileResponse = getResponse(url)
    if fileResponse.status == 200:
        try:
            with open(pathname, 'wb') as f:
                f.write(fileResponse.read())
            print("下载完毕")
        except Exception as excep:
            print("下载失败" + url)
            print(excep)
    else:
        print("下载图片连接失败:" + url)


def getResponse(url):
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/6.0')
    response = request.urlopen(req)
    return response
