#!/usr/bin/python3

import os

from PIL import Image
from bs4 import BeautifulSoup

from search.model.file import JavMovie
from search.net.httpUitls import *


class JavTool:
    webRoot = "https://www.cdnbus.in/"
    fileName = None
    dirpath = None
    filepath = None

    def __init__(self, root):
        self.webRoot = root

    def getJavInfo(self, code):
        """   http请求，  刮蹭 movie相关信息  """
        url = self.webRoot + code
        avResponse = getResponse(url)
        if avResponse is None:
            return None
        print(avResponse.status)
        try:
            html = avResponse.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            # imageNode
            a_img_node = soup.find('a', class_='bigImage')
            if a_img_node is None:
                return None
            img_node = a_img_node.find('img')
            # title
            img_title = img_node.get("title")
            # image
            image = a_img_node.get("href")
            # actress
            actresses = []
            actresses_urls = []
            actress_divs = soup.find_all('div', class_='star-name')
            for div in actress_divs:
                actress_link = div.find('a')
                actresses.append(actress_link.get_text())
                actresses_url = actress_link.get('href')
                actresses_urls.append(actresses_url)
            text_node = soup.find_all('span', class_='header')
            code = text_node[0].find_next('span').get_text()
            pdate_span = text_node[1]
            pdate_p = text_node[1].find_previous('p')
            pdate_span.extract()
            pdate = pdate_p.get_text()
            length_span = text_node[2]
            length_p = text_node[2].find_previous('p')
            length_span.extract()
            length = length_p.get_text()
            director = text_node[3].find_next("a").get_text()
            studio = text_node[4].find_next("a").get_text()
            supplier = text_node[5].find_next("a").get_text()
            series = text_node[6].find_next("a").get_text()
            return JavMovie().build(code, img_title, image, "", actresses, actresses_urls, director, pdate, series,
                                    studio,
                                    supplier,
                                    length, '')
        except Exception as err:
            print(avResponse)
            print("html解析失败")
            print(err)

    def makeActress(self, rootpath, movie):
        """
        1、 根据刮蹭的信息 创建目录结构
        2、 下载封面 jpg，制作海报切图png
         """
        try:
            os.chdir(rootpath)
            dirPath = rootpath + "\\" + movie.getActress()
            # 创建目录结构：演员
            if os.path.exists(dirPath):
                pass
            else:
                os.mkdir(movie.getActress())
            os.chdir(movie.getActress())
            # 创建目录结构：发行商
            dirPath = dirPath + "\\" + movie.maker
            if os.path.exists(dirPath):
                pass
            else:
                os.mkdir(movie.maker)
            os.chdir(movie.maker)
            # 创建目录结构：电影信息
            fileName = "[" + movie.getActress() + "]" + " [" + movie.code + "]" + movie.title
            dirPath = dirPath + "\\" + fileName
            if os.path.exists(dirPath):
                pass
            else:
                os.mkdir(fileName)
            os.chdir(fileName)
            # 下载图片
            pic_end = ".jpg"
            filepath = dirPath + "\\" + fileName + pic_end
            download(movie.cover, filepath)
            # 图片切割成 png
            img = Image.open(filepath)
            widthPos = int((img.width / 80) * 42)
            cropped = img.crop((widthPos, 0, img.width, img.height))  # (left, upper, right, lower)
            croppedName = filepath.replace(".jpg", '.png')
            cropped.save(croppedName)
            # 返回信息
            self.dirpath = dirPath
            self.filepath = filepath
            self.fileName = fileName
        except Exception as err:
            print("生成目录信息")
            print(err)
