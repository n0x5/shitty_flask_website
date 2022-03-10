import os
import re
from tqdm import tqdm
import sqlite3


sql_db = os.path.join(os.path.dirname( __file__ ), 'discogs-releases2.db')
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists discogs_releases
        (id text, country text, released text,
         genres text, styles text, title text, label_name text, catno text, label_id text, format_name text,
        format_qty text, data_quality text, notes text, track_p text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

cur.execute('''CREATE TABLE if not exists discogs_rel_artists
        (release_id text, artist_id text, artist_name text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')


xmlfile = 'discogs_20220301_releases.xml'

def read1():
    return xml.read(291910611)

with open(xmlfile, 'r', encoding="utf=8") as xml:
    for fname in iter(read1, ''):
        labels = re.findall(r'<release id="(\d+)" status="(.+?)">(.+?)<\/release>', fname)
        for item in tqdm(labels):
            try:
                id = item[0]
                try:
                    country = re.search(r'<country>(.+?)<\/country>', str(item))
                    country = country.group(1)
                except:
                    country = 'None'
                try:
                    label = re.search(r'<label name="(.+?)" catno="(.+?)" id="(.+?)"\/>', str(item))
                    try:
                        label_name = label.group(1)
                    except:
                        label_name = 'None'
                    try:
                        catno = label.group(2)
                    except:
                        catno = 'None'
                    try:
                        label_id = label.group(3)
                    except:
                        label_id = 'None'
                except:
                    label = 'None'
                try:
                    artist_id = re.findall(r'<artist><id>(.+?)<\/id><name>(.+?)<\/name>', str(item))
                    for item8 in artist_id:
                        stuffdis = id, item8[0], item8[1]
                        cur.execute('insert into discogs_rel_artists (release_id, artist_id, artist_name) VALUES (?,?,?)', (stuffdis))
                        cur.connection.commit()
                except:
                    artist_id = 'none'
                try:
                    genres = re.findall(r'<genre>(.+?)<\/genre>', str(item))
                except:
                    genres = 'None'
                try:
                    styles = re.findall(r'<style>(.+?)<\/style>', str(item))
                except:
                    styles = 'None'
                try:
                    year = re.search(r'<year>(.+?)<\/year>', str(item))
                    year = year.group(1)
                except:
                    year = 'None'
                try:
                    title = re.search(r'<title>(.+?)<\/title>', str(item))
                    title = title.group(1)
                except:
                    title = 'None'
                try:
                    data_quality = re.search(r'<data_quality>(.+?)<\/data_quality>', str(item))
                    data_quality = data_quality.group(1)
                except:
                    data_quality = 'None'
                try:
                    formats = re.search(r'<format name="(.+?)" qty="(\d{0,5}?)"', str(item))
                    try:
                        format_name = formats.group(1)
                    except:
                        format_name = 'None'
                    try:
                        format_qty = formats.group(2)
                    except:
                        format_qty = 'None'
                except:
                    formats = 'None'
                try:
                    released = re.search(r'<released>(.+?)<\/released>', str(item))
                    released = released.group(1)
                except:
                    released = 'None'
                try:
                    notes = re.search(r'<notes>(.+?)<\/notes>', str(item))
                    notes = notes.group(1)
                except:
                    notes = 'None'
                try:
                    tracklist = re.search(r'<tracklist>(.+?)<\/tracklist>', str(item))
                    tracks = re.findall(r'<track>(.+?)<\/track>', str(tracklist.group(1)))
                    track_p = []
                    for item9 in tracks:
                        try:
                            position = re.search(r'<position>(.+?)<\/position>', str(item9))
                            track_title = re.search(r'<title>(.+?)<\/title>', str(item9))
                            duration = re.search(r'<duration>(.+?)<\/duration>', str(item9))
                            track_p.append([position.group(1), track_title.group(1), duration.group(1)])
                        except:
                            track_p = 'None'

                except:
                    tracklist = 'None'
                if 'US' in country or 'UK' in country or 'Europe' in country:
                    stuff = id, country, str(released), ', '.join(genres), ', '.join(styles), title, label_name, catno, label_id, format_name, format_qty, data_quality, notes, str(track_p)
                    cur.execute('insert into discogs_releases (id, country, released, genres, styles, title, label_name, catno,\
                                label_id, format_name, format_qty, data_quality, notes, track_p) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (stuff))
                    cur.connection.commit()
                    #print(stuff)
            except Exception as e:
                pass
                #print(e)

