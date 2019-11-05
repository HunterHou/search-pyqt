import base64

from ImgConst import PLAY_IMG

url = 'E:\\sync.png'

play = base64.b64decode(PLAY_IMG)
with open("e:\\test.png", "wb") as f:
    f.write(play)
