#!/usr/bin/python
# encoding=utf-8


class JavMovie:
    code = ""
    title = ""
    image = ""
    actresses = ""
    series = ""
    studio = ""
    supplier = ""
    length = ""
    pdate = ""

    director = ""

    def __init__(self, code, title, image, actress, director, pdate, series, studio, supplier, length):
        self.code = code
        self.title = title
        self.image = image
        self.actresses = actress
        self.director = director
        self.pdate = pdate
        self.series = series
        self.studio = studio
        self.supplier = supplier
        self.length = length

    def getActress(self):
        actress = ','.join(self.actresses)
        return actress
