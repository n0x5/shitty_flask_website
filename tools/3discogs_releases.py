import os
import re
from tqdm import tqdm
import sqlite3
from lxml import etree

sql_db = os.path.join(os.path.dirname( __file__ ), 'discogs-releases-new.db')
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists discogs_releases
        (id text unique, country text, released text,
         genres text, styles text, title text, label_name text, catno text, label_id text, format_name text,
        format_qty text, data_quality text, notes text, track_p text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

cur.execute('''CREATE TABLE if not exists discogs_rel_artists
        (release_id text, artist_id text, artist_name text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')


xmlfile = 'discogs_20220301_releases.xml'


context = etree.iterparse(xmlfile, tag='release')
for event, elem in tqdm(context):
    tree = etree.tostring(elem).decode()
    release = re.search(r'<release id="(\d+)" status="(.+?)">', tree)
    release_id = release.group(1)
    try:
        country = re.search(r'<country>(.+?)<\/country>', tree)
        country = country.group(1)
    except:
        country = 'None'
    try:
        label = re.search(r'<label name="(.+?)" catno="(.+?)" id="(.+?)"\/>', tree)
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
        artist_id = re.findall(r'<artist><id>(.+?)<\/id><name>(.+?)<\/name>', tree)
        for item8 in artist_id:
            stuffdis = release_id, item8[0], item8[1]
            cur.execute('insert into discogs_rel_artists (release_id, artist_id, artist_name) VALUES (?,?,?)', (stuffdis))
            cur.connection.commit()
    except:
        artist_id = 'none'
    try:
        genres = re.findall(r'<genre>(.+?)<\/genre>', tree)
    except:
        genres = 'None'
    try:
        styles = re.findall(r'<style>(.+?)<\/style>', tree)
    except:
        styles = 'None'
    try:
        year = re.search(r'<year>(.+?)<\/year>', tree)
        year = year.group(1)
    except:
        year = 'None'
    try:
        title = re.search(r'<title>(.+?)<\/title>', tree)
        title = title.group(1)
    except:
        title = 'None'
    try:
        data_quality = re.search(r'<data_quality>(.+?)<\/data_quality>', tree)
        data_quality = data_quality.group(1)
    except:
        data_quality = 'None'
    try:
        formats = re.search(r'<format name="(.+?)" qty="(\d{0,5}?)"', tree)
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
        released = re.search(r'<released>(.+?)<\/released>', tree)
        released = released.group(1)
    except:
        released = 'None'
    try:
        notes = re.search(r'<notes>(.+?)<\/notes>', tree)
        notes = notes.group(1)
    except:
        notes = 'None'
    try:
        tracklist = re.search(r'<tracklist>(.+?)<\/tracklist>', tree)
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
        stuff = release_id, country, str(released), ', '.join(genres), ', '.join(styles), title, label_name, catno, label_id, format_name, format_qty, data_quality, notes, str(track_p)
        cur.execute('insert into discogs_releases (id, country, released, genres, styles, title, label_name, catno,\
                    label_id, format_name, format_qty, data_quality, notes, track_p) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (stuff))
        cur.connection.commit()
        #print(stuff)

    elem.clear()
    for ancestor in elem.xpath('ancestor-or-self::*'):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]
del context
