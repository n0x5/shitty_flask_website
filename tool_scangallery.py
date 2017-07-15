import re
import os
from PIL import Image
import sqlite3

cwd = r'/folder/image/gallery'

conn = sqlite3.connect('images.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE images
             (file text, fullpath text, subfolder text, sizewidth int, sizeheight int, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fullpath = os.path.join(subdir, fn)
        subfolder = os.path.basename(os.path.join(subdir))
        if 'thumbs' not in subfolder:
            imh = Image.open(fullpath).size
            imh2 = re.sub('[(/:)"]', '', str(imh).replace(', ', 'x'))
            swidth = imh2.split('x')
            print(fullpath, swidth)
            cur.execute('INSERT INTO images (file, fullpath, subfolder, sizewidth, sizeheight) VALUES (?,?,?,?,?)', (fn, fullpath, subfolder, int(swidth[0]), int(swidth[1])))
            cur.connection.commit()
