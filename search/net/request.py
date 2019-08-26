#!/usr/bin/python3

from urllib import request
from bs4 import BeautifulSoup


def getResponse(url):
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/6.0')
    response = request.urlopen(req)
    return response


url = 'https://www.cdnbus.in/JUY-951'
avResponse = getResponse(url)
print(avResponse.status)
html = avResponse.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
titleNode = soup.find("h3")
filename = titleNode.get_text()

imgNode = soup.find('a', class_='bigImage')
imgUrl = imgNode.get("href")

actress_div = soup.find('div', class_='star-name')
actress_link = actress_div.find('a')
actress = actress_link.get_text()
filename = "[" + actress + "]" + filename
imgend = ".jpg"
dirName = 'e:\\'
pathname = dirName + filename + imgend
fileResponse = getResponse(imgUrl)
if fileResponse.status == 200:
    try:
        with open(pathname, 'wb') as f:
            f.write(fileResponse.read())
        print("下载完毕")
    except Exception as excep:
        print("下载失败")
        print(excep)
