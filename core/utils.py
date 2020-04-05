import logging
import os
import time

from os import path
from PIL import Image

logger = logging.getLogger(__name__)


def create_thumbnail(imagepath: str, basewidth: int, force=False) -> bool:  # TODO: Use f'strings' instead of % format
    thumbfilename = "%s_th%s" % (
        path.splitext(imagepath)[0],
        path.splitext(imagepath)[1],
    )
    if not path.exists(thumbfilename) or force:
        try:
            img = Image.open(imagepath)
            wpercent = basewidth / float(img.size[0])
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            thumbfilename = "%s_th%s" % (
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
            + time.strftime("%Y%m%d%H%M", time.localtime())
            + "_"
            + filename
        )
    return os.path.join(path, format)
