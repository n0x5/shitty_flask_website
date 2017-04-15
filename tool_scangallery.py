import os
import sqlite3

cwd = r'/folder/image/gallery'

conn = sqlite3.connect('images.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE images (file text, fullpath text, subfolder text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fullpath = os.path.join(subdir, fn)
        subfolder = os.path.basename(os.path.join(subdir))
        if 'thumbs' not in subfolder:
            print(fullpath)
            cur.execute('INSERT INTO images (file, fullpath, subfolder) VALUES (?,?,?)', (fn, fullpath, subfolder))
            cur.connection.commit()

