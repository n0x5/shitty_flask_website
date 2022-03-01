import re
from bs4 import BeautifulSoup
import sqlite3
import os
import time


conn = sqlite3.connect('gamesv2.db')
cur = conn.cursor()
cur.execute('CREATE TABLE if not exists gamesv2 (title text, genre text, developer text, publisher text, eu text, jp text, na text, year int, systems text, orig_system text, dated datetime DEFAULT CURRENT_TIMESTAMP)')

i2 = r'List of Xbox games - Wikipedia.html'
i = open(i2, 'r', encoding='utf8')
soup = BeautifulSoup(i, "html.parser")

table1 = soup.find('tbody')

list1 = table1.find_all('tr')

for item in list1:
    tds = item.find_all('td')
    title = tds[0].get_text().strip()
    genre = tds[1].get_text().strip()
    developer = tds[2].get_text().strip()
    publisher = tds[3].get_text().strip()
    conn2 = sqlite3.connect('games.db')
    sql = 'select title, systems from games where title = ?'
    results = [item for item in conn2.execute(sql, (title,))]
    try:
        db_title = results[0][0]
        db_systems = results[0][1]
    except:
        db_title = 'No title'
        db_systems = 'No systems'

    eu = tds[4].get_text().strip()
    jp = tds[5].get_text().strip()
    na = tds[6].get_text().strip()
    orig_system = 'xbox'
    yearscomb = eu, jp, na
    year2 = re.search(r'\d{4}', str(yearscomb))
    year = year2.group(0)

    stuff = title, genre, developer, publisher, eu, jp, na, year, db_systems.replace(' ', ', '), orig_system
    cur.execute('INSERT INTO gamesv2 (title, genre, developer, publisher, eu, jp, na, year, systems, orig_system) VALUES (?,?,?,?,?,?,?,?,?,?)', (stuff))
    cur.connection.commit()
    print(stuff)