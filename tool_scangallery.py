import re
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import calendar
import sqlite3
from PIL import Image
import pyexiv2

#from gi.repository import GExiv2

cwd = r'/gallery/folder/'

conn = sqlite3.connect('imagesnew3.db')
cur = conn.cursor()
#cur.execute('''CREATE TABLE images
#             (file text, fullpath text unique, subfolder text, sizewidth int, sizeheight int, ftime int, exifd text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fullpath = os.path.join(subdir, fn)
        subfolder = os.path.basename(os.path.join(subdir))
        if 'thumbs' not in subfolder and 'subgallery' in fullpath:
            imh = Image.open(fullpath).size
            ims = str(os.path.getmtime(fullpath)).replace('.', '')
            ex2 = pyexiv2.ImageMetadata(fullpath)
            ex2.read()
            try:
                ex4 = [str(ex2[item]) for item in ex2.iptc_keys]
                ex5 = [str(ex2[item]) for item in ex2.exif_keys]
                ex6 = ex4, ex5
            except:
                pass
            imh2 = re.sub('[(/:)"]', '', str(imh).replace(', ', 'x'))
            swidth = imh2.split('x')
            try:
                print(fullpath, swidth, ims, str(ex6))
                cur.execute('INSERT INTO images (file, fullpath, subfolder, sizewidth, sizeheight, ftime, exifd) VALUES (?,?,?,?,?,?,?)', (fn, fullpath, subfolder, int(swidth[0]), int(swidth[1]), int(ims), str(ex6)))
                cur.connection.commit()
            except:
                pass
