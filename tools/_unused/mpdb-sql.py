import os
import pymysql
import time
import sqlite3
from tqdm import tqdm

connection3 = sqlite3.connect('moviesdb-divx.db')
cursor3 = connection3.cursor()
cursor3.execute('''CREATE TABLE if not exists db_movies
            (release text unique, rel_time int, rel_time_readable text, rel_group text, rel_section text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

conn = pymysql.connect(host ='localhost', user ='root', passwd = '', db= 'predb', charset ='utf8')
cur = conn.cursor()

sql = "select rel_name, rel_time, rel_group, rel_section from predb2.allpres where rel_section = 'DIVX' order by rel_time asc"


cur.execute (sql)
cur.connection.commit()

results = [item for item in cur.fetchall()]

for item in tqdm(results):
    human_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(item[1])))
    stuff = item[0], item[1], human_time, item[2], item[3]
    try:
        cursor3.execute('INSERT INTO db_movies (release, rel_time, rel_time_readable, rel_group, rel_section) VALUES (?,?,?,?,?)', (stuff))
        cursor3.connection.commit()
        #print(stuff)
    except Exception as e:
        print(e)
        pass
