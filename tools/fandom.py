import os
import re
from tqdm import tqdm
import sqlite3
from lxml import etree
import time

wiki_name = 'cryptidz'

sql_db = os.path.join(os.path.dirname( __file__ ), '{}.db' .format(wiki_name))
conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists {}
        (title text unique, content text, dated datetime DEFAULT CURRENT_TIMESTAMP)''' .format(wiki_name))

xmlfile = 'cryptidzwikiacom-20180621-history.xml'

context = etree.iterparse(xmlfile, tag='{http://www.mediawiki.org/xml/export-0.10/}page')
lst = []
for event, elem in tqdm(context):
    tree = etree.tostring(elem, encoding='utf-8').decode()
    if ('<ns>0</ns>' in tree or '<ns>14</ns>' in tree or '<ns>10</ns>' in tree) and '#redirect' not in tree.lower():
        try:
            title1 = re.search('<title>(.+)<\/title>', str(tree), flags=re.DOTALL)
            text = re.search('<text .*">(.+)<\/text>', str(tree), flags=re.DOTALL)
            title = title1.group(1)
            try:
                content = text.group(1)
            except:
                content = ''
            stuff = title, content
            lst.append(stuff)
            if len(lst) == 2000:
                cur.executemany('insert or ignore into {} (title, content) VALUES (?,?)' .format(wiki_name), (lst))
                cur.connection.commit()
                lst = []
        except Exception as e:
            print(e)

    elem.clear()
    for ancestor in elem.xpath('ancestor-or-self::*'):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]
del context

cur.executemany('insert or ignore into {} (title, content) VALUES (?,?)' .format(wiki_name), (lst))
cur.connection.commit()
