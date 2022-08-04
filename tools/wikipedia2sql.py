import xml.etree.ElementTree as ET
import time
import re
import sqlite3
import os
from tqdm import tqdm

xml_f = open('enwiki-20220801-pages-meta-current.xml', encoding='utf-8')

sql_db = os.path.join(os.path.dirname( __file__ ), 'wiki-en.db')
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists wiki
        (title text, content text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

for (event, elem) in tqdm(ET.iterparse(xml_f, events=['end'])):
    tree = ET.tostring(elem).decode()
    if ('<ns0:ns>0</ns0:ns>' in tree or '<ns0:ns>14</ns0:ns>' in tree) and '<ns0:redirect title' not in tree:
        try:
            title1 = re.search('<ns0:title>(.+)<\/ns0:title>', str(tree), flags=re.DOTALL)
            text = re.search('<ns0:text .+">(.+)<\/ns0:text>', str(tree), flags=re.DOTALL)
            title = title1.group(1)
            content = text.group(1)
            stuff = title, content
            cur.execute('insert into wiki (title, content) VALUES (?,?)', (stuff))
            cur.connection.commit()

        except Exception:
            print('skipping')

xml_f.close()
