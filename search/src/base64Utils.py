import base64
import os

from search.const.ImgConst import *


def getBase64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read())


outpath = "e:\\"


def testout():
    for file in os.listdir(os.path.curdir):
        if file.endswith(".jpg"):
            name = file.title().replace(".Jpg", "")
            name = name.upper()
            str64 = getBase64(file.casefold())
            print(name + ' = ' + "'''" + str(str64) + "''")
            with open(outpath + file.title(), 'wb') as file:
                file.write(base64.b64decode(str64))


print(OPEN)
with open('e:\\test.jpg', 'wb') as file:
    file.write(base64.b64decode(OPEN))
