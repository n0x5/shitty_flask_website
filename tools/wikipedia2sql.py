import os
import re
from tqdm import tqdm
import sqlite3
from lxml import etree
import time

sql_db = os.path.join(os.path.dirname( __file__ ), 'wiki-en3.db')
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists wiki
        (title text unique, content text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

xmlfile = 'enwiki-20220801-pages-meta-current.xml'

context = etree.iterparse(xmlfile, tag='{http://www.mediawiki.org/xml/export-0.10/}page')
lst = []
for event, elem in tqdm(context):
    tree = etree.tostring(elem).decode()
    if ('<ns>0</ns>' in tree or '<ns>14</ns>' in tree) and '#REDIRECT' not in tree:
        try:
            title1 = re.search('<title>(.+)<\/title>', str(tree), flags=re.DOTALL)
            text = re.search('<text .*">(.+)<\/text>', str(tree), flags=re.DOTALL)
            title = title1.group(1)
            content = text.group(1)
            stuff = title, content
            lst.append(stuff)
            if len(lst) == 2000:
                cur.executemany('insert or ignore into wiki (title, content) VALUES (?,?)', (lst))
                cur.connection.commit()
                lst = []
        except Exception:
            print('skipping')

    elem.clear()
    for ancestor in elem.xpath('ancestor-or-self::*'):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]
del context
