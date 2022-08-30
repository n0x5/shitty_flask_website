import os
import re
from tqdm import tqdm
import sqlite3
from lxml import etree
import time

sql_db = os.path.join(os.path.dirname( __file__ ), 'discogs_labels_subs.db')
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists labels \
        (label_id text unique, label_name text, profile text, sublabels text, sublabel_count int, dated datetime DEFAULT CURRENT_TIMESTAMP)''')


xmlfile = 'discogs_20220101_labels.xml'

context = etree.iterparse(xmlfile, tag='label')
lst3 = []

for event, elem in tqdm(context):
    tree = etree.tostring(elem.xpath('ancestor-or-self::*')[0]).decode()
    try:
        label2 = re.search(r'<label><images>(.+?)<\/sublabels><\/label>', tree, re.DOTALL)
        label = label2.group(0)
    except Exception:
        label = 'None'
    try:
        label_name = re.search(r'<name>(.+?)<\/name>', str(label), re.DOTALL)
        label_name = label_name.group(1)
    except Exception:
        label_name = 'None'
    try:
        label_id = re.search(r'<id>(.+?)<\/id>', str(label))
        label_id = label_id.group(1)
    except Exception:
        label_id = ''
    try:
        profile = re.search(r'<profile>(.+?)<\/profile>', str(label), re.DOTALL)
        profile = profile.group(1)
    except Exception:
        profile = 'None'
    try:
        sublabels1 = re.findall(r'<label id="(.+?)">(.+?)<\/label>', str(label), re.DOTALL)
        track_p = []
        try:
            for item in sublabels1:
                track_a = item[0]+' '+item[1]+'\n'
                track_p.append(track_a)
        except Exception:
            track_p = 'None'
        sublabel_count = len(track_p)
    except Exception:
        track_p = 'None'
        sublabel_count = '0'
    stuff = label_name, label_id, profile, ''.join(track_p), int(sublabel_count)
    lst3.append(stuff)
    if len(lst3) == 2000:
        cur.executemany('insert or ignore into labels (label_id, label_name, profile, sublabels, sublabel_count) VALUES (?,?,?,?,?)', (lst3))
        cur.connection.commit()
        lst3 = []

    elem.clear()
    for ancestor in elem.xpath('ancestor-or-self::*'):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]
del context