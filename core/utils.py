import logging
import os
import time
import base64

from os import path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


logger = logging.getLogger(__name__)

if "core" in os.getcwd():
    FONT_PATH = "../static/fonts/Roboto-Regular.ttf"
else:
    FONT_PATH = "./static/fonts/Roboto-Regular.ttf"


def create_thumbnail(imagepath: str, basewidth: int, force=False) -> bool:
    thumbfilename = "{}_th{}".format(
        path.splitext(imagepath)[0],
        path.splitext(imagepath)[1],
    )
    if not path.exists(thumbfilename) or force:
        try:
            img = Image.open(imagepath)
            wpercent = basewidth / float(img.size[0])
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            thumbfilename = "{}_th{}".format(
                path.splitext(imagepath)[0],
                path.splitext(imagepath)[1],
            )
            img.save(thumbfilename)
            return True
        except Exception as e:
            logger.error(f"Error creaing thumbnail for {imagepath} - {repr(e)}")
    return False


def rename_img(instance, filename):  # TODO: Use f'strings' instead of % format
    path = "pedidos/"
    filename = filename.replace(" ", "_")
    if not instance.phone:
        format = time.strftime("%Y%m%d%H%M", time.localtime()) + "-" + filename
    else:
        format = (
            str(instance.phone)
            + "_"
            + time.strftime(f"%Y%m%d%H%M", time.localtime())
            + "_"
            + filename
        )
    return os.path.join(path, format)


def text_to_image(text, width, height) -> Image:
    img = Image.new('RGB', (width, height), color=(0, 209, 178))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(FONT_PATH, 30)
    w, h = d.textsize(text, font=fnt)
    d.text(((width-w)/2, (height-h)/2), text, font=fnt, align="center", fill=(255, 255, 255))
    return img


def image_to_base64(image):
    with BytesIO() as buffer:
        image.save(buffer, 'PNG')
        return base64.b64encode(buffer.getvalue()).decode()
