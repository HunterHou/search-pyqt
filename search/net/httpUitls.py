#!/usr/bin/python3
# encoding=utf-8
from urllib import request


def download(url, pathname):
    """ 用http请求多媒体 ， 并下载到本地 """
    fileResponse = getResponse(url)
    if fileResponse is None:
        return

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
    """发送http请求"""
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/6.0')
        response = request.urlopen(req, timeout=10)
        return response
    except Exception as err:
        print("getResponse 失败:" + url)
        print(err)
        return None
