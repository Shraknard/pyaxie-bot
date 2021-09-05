# uncompyle6 version 3.7.4
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.10 (default, Jun  2 2021, 10:49:15) 
# [GCC 9.4.0]
# Embedded file name: /home/vi/pyaxie/pyaxie_utils.py
# Compiled at: 2021-08-31 23:29:51
# Size of source mod 2**32: 1305 bytes
from mnemonic import Mnemonic
from PIL import Image
import string, random

def gen_pass_phrase():
    mnemo = Mnemonic('english')
    return mnemo.generate(strength=128)


def gen_password(n=0):
    """
    Generate a random password
    :param n:
    :return:
    """
    n = 20 if n <= 10 else n
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation.replace(';', '')
    res = ''
    for i in range(n):
        res += random.choice(chars)
    else:
        return res


def merge_images(path1, path2, path3, name):
    """
    Merge 3 axies pictures into one image in line
    :param path1: Path of the 1st axie image (usually './img/axies/AXIE-ID.jpg')
    :param path2: Path of the 2nd axie image
    :param path3: Path of the 3rd axie image
    :param name: Name of the scholar
    :return: Path of the freshly created image
    """
    img = Image.open(path1).convert('RGBA')
    img2 = Image.open(path2).convert('RGBA')
    img3 = Image.open(path3).convert('RGBA')
    dst = Image.new('RGB', (img.width * 3, img.height)).convert('RGBA')
    final = './img/axies/' + name + '.png'
    dst.paste(img, (0, 0))
    dst.paste(img2, (img.width, 0))
    dst.paste(img3, (img.width * 2, 0))
    dst.save(final)
    return final
# okay decompiling pyaxie_utils.cpython-38.pyc
