import re
import time
import urllib.request
import requests
from bs4 import BeautifulSoup
import sqlite3
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('year')
args = parser.parse_args()

sql_db = os.path.join(os.path.dirname( __file__ ), '..', 'databases', 'movies.db')

conn = sqlite3.connect(sql_db)
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists boxoffice2
            (title text, genres text, rl_id text unique, imdb_id text,
             studio text, theaters text, studio_id text, year int, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

for month in months:

    url = r'https://www.boxofficemojo.com/calendar/{}-{}-01/' .format(args.year, month)


    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table2 = soup.find('div', attrs={'id': 'table'})

    table3 = table2.find_all('tr')

    for item in table3:
        title2 = item.find('div', attrs={'class': 'a-section a-spacing-none mojo-schedule-release-details'})
        if title2 is not None:
            rl_id2 = title2.find('a', href=re.compile('(rl\d+)'))
            rl_id = re.search(r'\/release\/(rl\d+)\/', str(rl_id2))
            title = title2.find('h3').text
            genres2 = title2.find('div', attrs={'class': 'a-section a-spacing-none mojo-schedule-genres'}).text
            genres = re.sub('\\n', '', genres2)
            imdb = item.find('a', href=re.compile('/(tt\d+)'))
            imdb_id = re.search(r'\/(tt\d+)', str(imdb))
            studio1 = item.find('td', attrs={'class': 'a-text-left mojo-field-type-release_studios'}).text
            studio = re.sub('\\n', '', studio1)
            studio_id1 = item.find('td', attrs={'class': 'a-text-left mojo-field-type-release_studios'})
            try:
                studio_id = re.search(r'\/(co\d+)', str(studio_id1)).group(1)
            except:
                studio_id = 'None'
            theaters = item.find('td', attrs={'class': 'a-text-left mojo-field-type-release_scale'}).text
            stuff = title, ', '.join(genres.split()), rl_id.group(1), imdb_id.group(1), studio, theaters, studio_id, args.year
            cur.execute('INSERT OR IGNORE INTO boxoffice2 (title, genres, rl_id, imdb_id, studio, theaters, studio_id, year) VALUES (?,?,?,?,?,?,?,?)', (stuff))
            cur.connection.commit()
            print(stuff)

    time.sleep(2)
