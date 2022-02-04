#!/usr/bin/env python

# Scan imdb for episode info

import os
import requests
import re
from bs4 import BeautifulSoup
import sqlite3
import urllib.request
from urllib.request import FancyURLopener
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('imdb_id')
parser.add_argument('season')
args = parser.parse_args()

class GrabIt(urllib.request.FancyURLopener):
        version = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36')
        def download_file(self, url, path):
                try:
                    self.urlretrieve = GrabIt().retrieve
                    self.urlretrieve(url, path)
                except Exception as e:
                    print(str(e))

conn = sqlite3.connect('tv.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists tv
            (imdb_id, show_title text, episode_title text, air_date text, episode_summary text, 
                season_number int, episode_number int, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

url = r'https://www.imdb.com/title/{}/episodes?season={}' .format(args.imdb_id, args.season)
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
}

grab1 = GrabIt()
url2 = r'https://www.imdb.com/title/{}' .format(args.imdb_id)
response2 = requests.get(url2, headers=headers)
soup3 = BeautifulSoup(response2.text, "html.parser")
table = soup3.find('script', type=re.compile(r'ld\+json'))
try:
    data = json.loads(table.string)
except:
    data = json.loads(table.get_text())
show_title = data['name']

endpoint4 = os.path.join(os.path.dirname(__file__), 'cover_tv', args.imdb_id+'.jpg')
if not os.path.isfile(endpoint4):
   
    cover = data['image']
    id2 = re.search(r'(tt\d+)', str(url2))
    endpoint = os.path.join(os.path.dirname(__file__), 'cover_tv', id2.group(1)+'.jpg')
    if not os.path.exists('cover_tv'):
        os.makedirs('cover_tv')
    if os.path.isfile(endpoint):
        print('file exists - skipping')
    r = requests.get(cover, headers=headers)
    fn = os.path.basename(cover)

    with open(endpoint, 'wb') as cover_jpg:
        cover_jpg.write(r.content)


response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")


table = soup.find('div', attrs={'class': 'list detail eplist'})

for item in soup.find_all('div', attrs={'class': 'list_item'}):
    episode_number = item.find('meta', content=re.compile('\d{1,5}'))
    airdate = item.find('div', attrs={'class': 'airdate'})
    episode_title = item.find('strong')
    episode_summary = item.find('div', attrs={'class': 'item_description'})
    sql = args.imdb_id, show_title.strip(), episode_title.get_text().strip(), airdate.get_text().strip(), \
          episode_summary.get_text().strip(), args.season, episode_number['content']
    print(sql)
    cur.execute('INSERT INTO tv (imdb_id, show_title, episode_title, air_date, episode_summary, season_number, episode_number) VALUES (?,?,?,?,?,?,?)', (sql))
    cur.connection.commit()
