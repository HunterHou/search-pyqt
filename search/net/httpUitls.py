#!/usr/bin/python3
# encoding=utf-8
import logging
from urllib import request

opener = request.build_opener()
opener.addheaders = [('User-Agent',
                      'Mozilla/6.0')]
request.install_opener(opener)


def download(url, pathname):
    """ 用http请求多媒体 ， 并下载到本地 """
    try:
        request.urlretrieve(url, pathname)
        logging.info("文件创建成功...")
        return True
    except Exception as err:
        logging.error("文件创建失败..." + url, err)
        return False


def getResponse(url):
    """发送http请求"""
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/6.0')
        response = request.urlopen(req, timeout=10)
        if response.status == 200:
            logging.info("请求成功..." + url)
        else:
            logging.info("请求失败..." + url)
        return response
    except Exception as err:
        logging.error("请求失败...:" + url + str(err))
        return None
