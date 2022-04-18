import sys
sys.path.append("/mnt/python3/site-packages/site-packages")
import os
import bottle
from PIL import Image
import numpy as np
from model import Generator
import torch
from torchvision.transforms.functional import to_tensor, to_pil_image
import base64
import json
import random
import io

torch.backends.cudnn.enabled = False
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

cacheDir = '/tmp/'
randomStr = lambda num=5: "".join(random.sample('abcdefghijklmnopqrstuvwxyz', num))

def load_image(image_path, x32=False):
    img = Image.open(image_path).convert("RGB")

    if x32:
        def to_32s(x):
            return 256 if x < 256 else x - x % 32
        w, h = img.size
        img = img.resize((to_32s(w), to_32s(h)))

    return img

@bottle.route('/images/comic_style', method='POST')
def getComicStyle():
    result = {}
    postData = json.loads(bottle.request.body.read().decode("utf-8"))
    image = postData.get("image")
    localName = randomStr(10) + ".jpg"

    # 图片获取
    imagePath = cacheDir + localName
    with open(imagePath, 'wb') as f:
        f.write(base64.b64decode(image))
    device = 'cpu'
    net = Generator()
    net.load_state_dict(torch.load('./weights/paprika.pt', map_location="cpu"))
    net.to(device).eval()
    
    image = load_image(imagePath)
    with torch.no_grad():
        image = to_tensor(image).unsqueeze(0) * 2 - 1
        out = net(image.to(device), False).cpu()
        out = out.squeeze(0).clip(-1, 1) * 0.5 + 0.5
        out = to_pil_image(out)
    img_buffer = io.BytesIO()
    out.save(img_buffer, format='JPEG')
    byte_data = img_buffer.getvalue()
    img_buffer.close()
    result["photo"] = 'data:image/jpg;base64, %s' % base64.b64encode(byte_data).decode()
        
        # imgAttr = Image.open(imagePath).convert("RGB")
        # outAttr = face2paint(model, imgAttr)
        # img_buffer = io.BytesIO()
        # outAttr.save(img_buffer, format='JPEG')
        # byte_data = img_buffer.getvalue()
        # img_buffer.close()
        # result["photo"] = 'data:image/jpg;base64, %s' % base64.b64encode(byte_data).decode()
    # except Exception as e:
    #     print("ERROR: ", e)
    #     result["error"] = True

    return result


app = bottle.default_app()
if __name__ == "__main__":
    bottle.run(host='localhost', port=8099)