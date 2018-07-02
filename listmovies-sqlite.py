#!/usr/bin/env python

# Create a list of movies in a folder
# It uses currently active directory so cd into the folder
# then run ./list-html-movies.py and it will make a html file
# in the same folder

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
number = 0

conn = sqlite3.connect('movies.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE movies 
            (release text unique, grp text, genre text, format text, imdb text, title text, director text, 
            mainactors text, infogenres text, inforest text, infosummary text, year text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

class GrabIt(urllib.request.FancyURLopener):
        version = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36')
        def download_file(self, url, path):
                try:
                    self.urlretrieve = GrabIt().retrieve
                    self.urlretrieve(url, path)
                except Exception as e:
                    print(str(e))

def imdburl(fn):
    filn2 = open(fn, "r")
    for line in filn2:
        if "imdb.com/" in line.lower():
            urls = re.findall(r'\d{7}', line)
            urls23 = "[]".join(urls)
    return 'https://www.imdb.com/title/tt'+urls23


def store(release, grp, genre, title, director, mainactors, infogenres, inforest, infosummary, year):
    print('{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}' .format(basenm2, file6, genrs(file2), file7, imdburl(file2), 
        str(imdb_info[0]).strip(), str(imdb_info[1]).strip(), str(imdb_info[2]).replace('\\n', ''), str(imdb_info[3]), 
        str(imdb_info[4]), str(imdb_info[5]).strip(), str(imdb_info[6])))
    cur.execute('INSERT INTO movies (release, grp, genre, format, imdb, title, director, mainactors, infogenres, inforest, infosummary, year) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', 
                (basenm2, file6, genrs(file2), file7, imdburl(file2), str(imdb_info[0]).strip(), str(imdb_info[1]).strip().replace(',', ''), str(imdb_info[2]).replace('\\n', '').strip(), 
                str(imdb_info[3]).strip(), str(imdb_info[4]).strip(), str(imdb_info[5]).strip(), str(imdb_info[6])))
    cur.connection.commit()

def genrs(fn):
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport", 
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    filn = open(fn, "r")
    for genres in filn:
        if "genre" in genres.lower():
            output = [item.title() for item in genrelist if item in genres.lower()]
            return(", ".join(repr(e).replace("'", "") for e in output))

def get_info(url):
    grab1 = GrabIt()
    info_genres = []
    info_main = []
    info_rest = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    cover = soup.find('div', attrs={'class': 'poster'})
    cover2 = cover.find('img', src=re.compile('.'))
    coverurl = cover2['src']
    id2 = os.path.basename(url)
    endpoint = os.path.join(os.path.dirname(__file__), 'covers', id2+'.jpg')
    if not os.path.exists('covers'):
        os.makedirs('covers')
    if os.path.isfile(endpoint):
        print('file exists - skipping')
    grab1.download_file(coverurl, endpoint)
    print(id2)

    title = soup.find('h1', attrs={'itemprop': 'name'})
    year2 = re.search(r'\((\d{4})\)', title.get_text())
    year = year2.group(1)
    genre = [genre1.get_text() for genre1 in soup.find_all('span', attrs={'itemprop': 'genre'})]
    director = soup.find('span', attrs={'itemprop': 'director'})
    main_actors2 = [main_actors.get_text() for main_actors in soup.find_all('span', attrs={'itemprop': 'actors'})]
    summary = soup.find('div', attrs={'class': 'summary_text'})
    actor_table = soup.find('table', attrs={'class': 'cast_list'})
    rest_actors = [rest_actors1.get_text() for rest_actors1 in actor_table.find_all('span', attrs={'itemprop': 'name'})]

    
    for line2 in genre:
        info_genres.append(line2)
    for line in main_actors2:
        info_main.append(line.replace(',', ''))
    for line3 in rest_actors:
        info_rest.append(line3)
    return title.get_text(), director.get_text(), info_main, info_genres, info_rest, summary.get_text().strip(), year



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
                print(url)
                if url is not None: 
                    imdb_info = get_info(url)
                if basenm2.lower().split('.')[0] not in banned:
                    store(basenm2, file6, genrs(file2), imdb_info[0], imdb_info[1], imdb_info[2], imdb_info[3], imdb_info[4], imdb_info[5], str(imdb_info[6]))
                    number += 1
                    r_int = randint(60, 130)
                    time.sleep(r_int)
            except Exception as e:
                print(e)
