#!/usr/bin/env python

# Create a list of movies in a folder

import os
import requests
import re
from bs4 import BeautifulSoup
import time
import sqlite3
from random import randint
import urllib.request
from urllib.request import FancyURLopener

today = time.strftime("__%m_%Y_%H_%M_%S")

cwd = r'/folder/path'

sql_db = os.path.join(os.path.dirname( __file__ ), '..', 'databases', 'movies.db')

conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE movies720
            (release text unique, imdb text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')


def imdburl(fn):
    filn2 = open(fn, "r")
    for line in filn2:
        if "imdb.com/" in line.lower():
            urls = re.findall(r'\d{7}', line)
            urls23 = "[]".join(urls)
    return 'https://www.imdb.com/title/tt'+urls23


for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        if fn.endswith(".nfo"):
            try:
                file2 = os.path.join(subdir, fn)
                basenm2 = os.path.basename(os.path.join(subdir))
                file6 = "[]".join(basenm2.split('-')[-1:])
                file7 = "[]".join(basenm2.split('.')[-1:]).split('-')[0]
                banned = ['cd1', 'cd2', 'sample', 'vobsub', 'subs', 'proof', 'prooffix', 'syncfix']
                url = imdburl(file2)
                #print(url)
                try:
                    print(basenm2, url)
                    cur.execute('INSERT INTO movies720 (release, imdb) VALUES (?,?)', (basenm2, url))
                    cur.connection.commit()
                except:
                    print(basenm2, 'None')
            except Exception as e:
                print(e)