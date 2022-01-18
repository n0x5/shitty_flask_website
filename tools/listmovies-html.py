import re
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import calendar
import sqlite3


conn = sqlite3.connect('movies3.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE movies (title text unique, grp text, imdb text, genre text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

wsite = open('list.html', 'r')
soup = BeautifulSoup(wsite, "html.parser")
gameslist = soup.find('table', attrs={'class': 'sortable'})

def title(row):
    for title2 in row.find_all('td', class_="release") or row:
        return title2.get_text(' ', strip=True)

def grp(row):
    for dat2 in row.find_all('td', class_="group") or row:
        return dat2.get_text(' ', strip=True)

def imdb(row):
    for dat2 in row.find_all('a', href=re.compile('.')) or row:
        return dat2['href']

def genre(row):
    for systems in row.find_all('td', class_="genre") or row:
        return systems.get_text(' ', strip=True)

for row in gameslist.find_all('tr') or row:
    try:
        title1 = title(row)
        grp1 = grp(row)
        imdb1 = imdb(row)
        genre1 = genre(row)
        print('INSERT INTO movies (title, grp, imdb, genre) VALUES (?,?,?,?)', (title1, grp1, imdb1, genre1))
        cur.execute('INSERT INTO movies (title, grp, imdb, genre) VALUES (?,?,?,?)', (title1, grp1, imdb1, genre1))
        cur.connection.commit()
    except Exception as e:
        print(str(e))
