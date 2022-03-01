import re
from bs4 import BeautifulSoup
import sqlite3
import os
import time


conn = sqlite3.connect('games.db')
cur = conn.cursor()

i2 = r'console_exclusives_PS4.html'
i = open(i2, 'r', encoding='utf8')
soup = BeautifulSoup(i, "html.parser")


list1 = soup.find_all('tr')
for item in list1:
    try:
        tds = item.find_all('td')
        title = tds[0].get_text().strip()
        systems = tds[1].get_text().strip()
        date = tds[2].get_text().strip()
        stuff = title, systems, date
        print(stuff)
        cur.execute('INSERT INTO games (title, systems, rlsdate) VALUES (?,?,?)', (stuff))
        cur.connection.commit()
    except Exception:
        pass