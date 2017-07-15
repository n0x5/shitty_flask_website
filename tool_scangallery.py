import re
import os
from PIL import Image
import sqlite3

cwd = r'/folder/image/gallery'

conn = sqlite3.connect('images.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE images
             (file text, fullpath text, subfolder text, size text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fullpath = os.path.join(subdir, fn)
        subfolder = os.path.basename(os.path.join(subdir))
        if 'thumbs' not in subfolder:
            imh = Image.open(fullpath).size
            imh2 = re.sub('[(/:)"]', '', str(imh).replace(', ', 'x'))
            print(fullpath, imh2)
            cur.execute('INSERT INTO images (file, fullpath, subfolder, size) VALUES (?,?,?,?)', (fn, fullpath, subfolder, imh2))
            cur.connection.commit()
