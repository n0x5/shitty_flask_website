import os
import requests
import re
from bs4 import BeautifulSoup
import time
import sqlite3
from random import randint
import json
import traceback
from random import randint

def get_info(url):
    conn = sqlite3.connect('movies-flm.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE if not exists moviesflm
            (imdb text unique, title text, director text,
            mainactors text, infogenres text, inforest text, infosummary text, year text, country text, language text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('script', type=re.compile(r'ld\+json'))


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
        directors = ','.join(directors)

    except:
        directors = data['director']['name']
    summary = data['description']
    try:
        keywords = data['keywords']
    except:
        keywords = 'No keywords'
    score = data['aggregateRating']
    try:
        rating = data['contentRating']
    except:
        rating = 'Not rated'
    try:
        cast2 = soup.find('table', attrs={'class': 'cast_list'})
        names = cast2.find_all('a', href=re.compile(r'\/name'))
    except:
        cast2 = soup.find('section', attrs={'data-testid': 'title-cast'})
        names = cast2.find_all('a', href=re.compile(r'\/name'))

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

    langs = soup.find('div', attrs={'data-testid': 'title-details-section'})
    country_origin = langs.find('a', href=re.compile('country_of_origin')).text
    language_orig = langs.find('a', href=re.compile('primary_language')).text
    #stuff = year, typ3, title, cover, genres, actors, directors, summary, keywords, rating, score['ratingValue'], inforest

    stuff = url, title+' ('+year+')', directors, ', '.join(actors), ', '.join(genres), ', '.join(inforest), summary, year, country_origin, language_orig
    print(stuff)
    try:
        cur.execute('insert into moviesflm (imdb, title, director, mainactors, infogenres, inforest, infosummary, year, country, language) VALUES (?,?,?,?,?,?,?,?,?,?)', (stuff))
        cur.connection.commit()
    except Exception as e:
        print(e)




bmarks = r'FLM - IMDb.html'
i = open(bmarks, 'r', encoding='utf8')
soup = BeautifulSoup(i, "html.parser")

info2 = soup.find_all('div', attrs={'class': 'lister-item-title'})

for item in info2:
    r_int = randint(6, 15)
    time.sleep(r_int)
    try:
        url2 = item.find('a')
        url = url2['href'].strip()
        print('Fetching iMDB:')
        info = get_info(url)
        print(info)

    except Exception as e:
        print('Error', e)