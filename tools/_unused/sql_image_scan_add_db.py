import re
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import calendar
import sqlite3
from PIL import Image
import pyexiv2
from tqdm import tqdm

#from gi.repository import GExiv2

cwd = r'/path/to/folder'

conn = sqlite3.connect('imagesnew3111.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE images
             (file text, fullpath text unique, subfolder text, sizewidth int, sizeheight int, ftime int, exifd text, celebname text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagename5.db'))
cursor2 = connection2.cursor()



def getname(fullpath, ex6):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'celeblist.db'))
    cursor = connection.cursor()
    cursor.execute("select celebname from celebslist")
    results = [item[0] for item in cursor.fetchall()]
    filn = os.path.basename(fullpath)
    celeb_list = []

    for adds2 in results:
        adds3 = adds2.split(' ')
        try:
            name1 = adds3[0]
            name2 = adds3[1]
        except:
            pass

        if name1.lower() in filn.lower() and name2.lower() in filn.lower() \
        or name1.lower() in str(ex6).lower() and name2.lower() in str(ex6).lower() \
        or name1.lower() in fullpath.lower() and name2.lower() in fullpath.lower():
            celeb_list.append(name1+' '+name2)
            cursor2.execute('INSERT INTO celebs (cname, subfolder, fn) VALUES (?,?,?)', (name1+' '+name2, fullpath, filn))
            cursor2.connection.commit()

    return celeb_list


for subdir, dirs, files in os.walk(cwd):
    for fn in tqdm(files):
        fullpath = os.path.join(subdir, fn)
        subfolder = os.path.basename(os.path.join(subdir))
        if 'thumbs' not in subfolder and 'sister_decadence' in subfolder or 'yuccama' in subfolder or 'bandido' in subfolder or 'christof_mib' in subfolder or 'f2k' in subfolder:
            try:
                imh = Image.open(fullpath).size
                ims = str(os.path.getmtime(fullpath)).replace('.', '')
                ex2 = pyexiv2.ImageMetadata(fullpath)
                ex2.read()
                ex4 = [str(ex2[item]) for item in ex2.iptc_keys]
                ex5 = [str(ex2[item]) for item in ex2.exif_keys]
                ex6 = ex4, ex5
                celebname = getname(fullpath, ex6)

            except:
                pass
            imh2 = re.sub('[(/:)"]', '', str(imh).replace(', ', 'x'))
            swidth = imh2.split('x')
            try:
                print(celebname, fullpath, swidth, ims, str(ex6))
                cur.execute('INSERT INTO images (file, fullpath, subfolder, sizewidth, sizeheight, ftime, exifd, celebname) VALUES (?,?,?,?,?,?,?,?)', (fn, fullpath, subfolder, int(swidth[0]), \
                             int(swidth[1]), int(ims), str(ex6), str(celebname)))
                cur.connection.commit()
            except:
                pass

cursor2.close()
cur.close()
