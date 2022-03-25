import os
import sqlite3
import re
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from tqdm import tqdm

conn = sqlite3.connect('mp3-labels.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS mp3_list (release text unique, artist text, album text, year text, genre text, discogs_label text, discogs_country text, discogs_genres text, discogs_styles text, discogs_date text, discogs_catno text, dated datetime DEFAULT CURRENT_TIMESTAMP)')

conn2 = sqlite3.connect(r'F:\dev\hidden2final\databases\discogs_releases_new - Copy.db')
cur2 = conn2.cursor()

cwd = r'F:\archive\mp3\- discographies -\Nu-Metal'

for subdir, dirs, files in tqdm(os.walk(cwd)):
    f = 0
    for fn in files:
        file2 = os.path.join(subdir, fn)
        foldername = os.path.basename(subdir)
        if fn.endswith('.mp3'):
            while f < 1:
                f += 1
                full_file = os.path.join(subdir, fn)
                audio = EasyID3(full_file)
                try:
                    artist = audio['artist'][0]
                except:
                    artist = 'None'
                try:
                    album2 = audio['album'][0]
                    album = re.sub('\((.+?)\)', '', album2)
                except:
                    album = 'None'
                try:
                    year = audio['date'][0]
                except:
                    year = 'None'
                try:
                    genre = audio['genre'][0]
                except:
                    genre = 'None'

                cur.execute("SELECT EXISTS(SELECT 1 FROM mp3_list WHERE release=? LIMIT 1)", (foldername,))
                record = cur.fetchone()
                if record[0] == 1:
                    print('exists')
                else:
                    sql2 = "select discogs_releases.title, discogs_releases.released, discogs_releases.country, discogs_releases.genres, discogs_releases.styles, discogs_releases.label_name, discogs_releases.catno, discogs_rel_artists.artist_name from discogs_releases join discogs_rel_artists on discogs_releases.id = discogs_rel_artists.release_id where discogs_rel_artists.artist_name like '%{}%' and discogs_releases.title like '%{}%'" .format(artist, album)
                    try:
                        results = [item for item in conn2.execute(sql2)]
                        discogs_label = str(results[0][5])
                        discogs_country = str(results[0][2])
                        discogs_genres = str(results[0][3])
                        discogs_styles = str(results[0][4])
                        discogs_date = str(results[0][1])
                        discogs_catno = str(results[0][6])
                    except:
                        discogs_label = 'None'
                        discogs_country = 'None'
                        discogs_genres = 'None'
                        discogs_styles = 'None'
                        discogs_date = 'None'
                        discogs_catno = 'None'
                    stuff = foldername, artist, album.strip(), year, genre, discogs_label, discogs_country, discogs_genres, discogs_styles, discogs_date, discogs_catno
                    cur.execute('INSERT or ignore INTO mp3_list (release, artist, album, year, genre, discogs_label, discogs_country, discogs_genres, discogs_styles, discogs_date, discogs_catno) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (stuff))
                    cur.connection.commit()
                    print(stuff)


