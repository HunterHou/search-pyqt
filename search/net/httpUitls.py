#!/usr/bin/python3
# encoding=utf-8
from urllib import request
from urllib.request import urlretrieve


def download(url, pathname):
    """ 用http请求多媒体 ， 并下载到本地 """

    try:
        urlretrieve(url, pathname)
        print("文件创建成功...")
        return True
    except Exception as err:
        print("文件创建失败..." + url)
        print(err)
        return False
    # fileResponse = getResponse(url)
    # if fileResponse is None:
    #     return False
    #
    # if fileResponse.status == 200:
    #     try:
    #         with open(pathname, 'xb') as f:
    #             f.write(fileResponse.read())
    #         print("文件创建成功...")
    #         return True
    #     except Exception as err:
    #         print("文件创建失败..." + url)
    #         print(err)
    #         return False
    # else:
    #     print("下载图片连接失败..." + url)
    #     return False


def getResponse(url):
    """发送http请求"""
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/6.0')
        response = request.urlopen(req, timeout=10)
        if response.status == 200:
            print("请求成功..." + url)
        else:
            print("请求失败..." + url)
        return response
    except Exception as err:
        print("请求失败...:" + url)
        print(err)
        return None
