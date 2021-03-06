#!/usr/bin/env python

# Create an sqlite db of movies in a folder
# Recursive scan of folders
# Uses imdb for data from .nfo imdb url

import os
import requests
import re
from bs4 import BeautifulSoup
import time
import sqlite3
from random import randint
import urllib.request
from urllib.request import FancyURLopener
import json
import traceback

today = time.strftime("__%m_%Y_%H_%M_%S")

cwd = r'F:\archive\xvid-scan'
number = 0

conn = sqlite3.connect('movies44.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists movies 
            (release text unique, grp text, genre text, format text, imdb text, title text, director text, 
            mainactors text, infogenres text, inforest text, infosummary text, year text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')


def imdburl(fn):
    filn2 = open(fn, "r")
    for line in filn2:
        if "imdb.com/" in line.lower():
            urls = re.findall(r'\d{6,10}', line)
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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('script', type=re.compile('ld\+json'))


    try:
        data = json.loads(table.string)
    except:
        data = json.loads(table.get_text())

    try:
        year2 = soup.find('title').get_text()
        year3 = re.search(r'(\d{4})', year2)
        year = year3.group(1)


    except:
        year = soup.find('div', attrs={'class': 'title_wrapper'}).get_text().replace('(', '').replace(')', '')

    typ3 = data['@type']
    url5 = data['url']
    title = data['name']
    cover = data['image']
    genres = data['genre']
    actor = data['actor']
    actors = [item4['name'] for item4 in actor]
    director = data['director']
    try:
        directors = [item5['name'] for item5 in director]
        directors = directors[0]
    except:
        directors = data['director']['name']
    summary = data['description']
    keywords = data['keywords']
    score = data['aggregateRating']
    rating = data['contentRating']
    try:
        cast2 = soup.find('table', attrs={'class': 'cast_list'})
        names = cast2.find_all('a', href=re.compile('\/name'))
    except:
        cast2 = soup.find('section', attrs={'data-testid': 'title-cast'})
        names = cast2.find_all('a', href=re.compile('\/name'))

    inforest = []
    inforest1 = []

    id2 = re.search(r'(tt\d+)', str(url5))
    endpoint = os.path.join(os.path.dirname(__file__), 'covers', id2.group(1)+'.jpg')
    if not os.path.exists('covers'):
        os.makedirs('covers')
    if os.path.isfile(endpoint):
        print('file exists - skipping')

    r = requests.get(cover, headers=headers)
    fn = os.path.basename(cover)

    with open(endpoint, 'wb') as cover_jpg:
        cover_jpg.write(r.content)

    for item in names:
        inforest1.append(item.get_text().strip())

    for item in inforest1:
        if item:
            inforest.append(item)

    #stuff = year, typ3, title, cover, genres, actors, directors, summary, keywords, rating, score['ratingValue'], inforest

    return title+' ('+year+')', directors, actors, genres, inforest, summary, year



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
                print(url, file2)
                if url is not None: 
                    imdb_info = get_info(url)
                if basenm2.lower().split('.')[0] not in banned:
                    store(basenm2, file6, genrs(file2), imdb_info[0], imdb_info[1], imdb_info[2], imdb_info[3], imdb_info[4], imdb_info[5], str(imdb_info[6]))
                    number += 1
                    r_int = randint(5, 15)
                    time.sleep(r_int)
            except Exception as e:
                print(e)
                traceback.print_exc()

