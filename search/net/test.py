from bs4 import BeautifulSoup
from urllib import request

docs = '<a class="bigImage" href="https://pics.javcdn.pw/cover/79vy_b.jpg"><img src="https://pics.javcdn.pw/cover/79vy_b.jpg" title="あの頃、制服美少女と。 美月はとり"/></a>'
bs = BeautifulSoup(docs, 'html.parser')
imgNode = bs.find('a', class_='bigImage')
imgUrl = imgNode.get('href')
req = request.Request(imgUrl)
req.add_header('User-Agent', 'Mozilla/6.0')
response = request.urlopen(req)
fname = 'E:\\test.jpg'
if response.status == 200:
    try:
        with open(fname, 'wb') as f:
            f.write(response.read())
        print("ok")
    except:
        print("fail")
