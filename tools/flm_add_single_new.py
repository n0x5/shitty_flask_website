import os
import requests
import re
from bs4 import BeautifulSoup
import time
import sqlite3
from random import randint
import json
import argparse
from tqdm import tqdm


def get_info(url):
    sql_db = os.path.join(os.path.dirname( __file__ ), '..', 'databases', 'movies_flm_new.db')
    conn = sqlite3.connect(sql_db)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE if not exists moviesflm
            (imdb text unique, orig_title text, eng_title text, director text,
            mainactors text, infogenres text, inforest text, infosummary text, year text, country text, language text, flm_actress text, json_data text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

    headers = {
    'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('script', type=re.compile(r'ld\+json'))

    try:
        data = json.loads(table.string)
    except:
        data = json.loads(table.get_text())

    json_data = json.dumps(data)

    try:
        year2 = soup.find('title').get_text()
        year3 = re.search(r'(\d{4})', year2)
        year = year3.group(1)


    except:
        year = soup.find('div', attrs={'class': 'title_wrapper'}).get_text().replace('(', '').replace(')', '')


    typ3 = data['@type']
    url5 = data['url']
    
    title = data['name']
    try:
        title_alt = data['alternateName']
    except:
        title_alt = 'None'
    try:
        cover = data['image']
    except:
        cover = 'None'
    try:
        genres = data['genre']
    except:
        genres = 'None'
    actor = data['actor']
    actors = [item4['name'] for item4 in actor]
    try:
        director = data['director']
    except:
        director = 'None'
    try:
        directors = [item5['name'] for item5 in director]
        directors = ','.join(directors)

    except:
        try:
            directors = data['director']['name']
        except:
            directors = 'None'
    try:
        summary = data['description']
    except:
        summary = 'No summary'
    try:
        keywords = data['keywords']
    except:
        keywords = 'No keywords'
    try:
        score = data['aggregateRating']
    except:
        score = 'No aggregate rating'
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
    endpoint_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers_flm')
    endpoint = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers_flm', id2.group(1)+'.jpg')
    if not os.path.exists(endpoint_folder):
        os.makedirs('covers_flm')
    if os.path.isfile(endpoint):
        print('file exists - skipping')

    try:
        r = requests.get(cover, headers=headers)
        fn = os.path.basename(cover)

        with open(endpoint, 'wb') as cover_jpg:
            cover_jpg.write(r.content)
    except:
        print('No cover')

    for item in names:
        inforest1.append(item.get_text().strip())

    for item in inforest1:
        if item:
            inforest.append(item)

    flm_actress = ''
    langs = soup.find('div', attrs={'data-testid': 'title-details-section'})
    country_origin = langs.find('a', href=re.compile('country_of_origin')).text
    try:
        language_orig = langs.find('a', href=re.compile('primary_language')).text
    except:
        language_orig = 'None'


    stuff = id2.group(1), title, title_alt, directors, ', '.join(actors), ', '.join(genres), ', '.join(inforest), summary, year, country_origin, language_orig, flm_actress, json_data
    print(stuff)
    try:
        cur.execute('insert into moviesflm (imdb, orig_title, eng_title, director, mainactors, infogenres, inforest, infosummary, year, country, language, flm_actress, json_data) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (stuff))
        cur.connection.commit()
    except Exception as e:
        print(e)



def get_gallery(url):
    headers = {
    'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title = re.search(r'<meta property="pageId" content="(tt\d{4,12})"', str(response.text))
    title2 = title.group(1)
    table = soup.find('script', type=re.compile(r'ld\+json'))
    if not os.path.exists(title2):
        os.makedirs(title2)

    try:
        data = json.loads(table.string)
    except:
        data = json.loads(table.get_text())

    json_data = json.dumps(data)
    for item in tqdm(data['image']):
        try:
            file_url = item['url']
            filename = os.path.join(title2, os.path.basename(file_url))
            if not os.path.exists(filename):
                r = requests.get(file_url, headers=headers)
                with open(filename, 'wb') as cover_jpg:
                    cover_jpg.write(r.content)

            file_url = item['contentUrl']
            filename = os.path.join(title2, os.path.basename(file_url))
            if not os.path.exists(filename):
                print('contenturl not exist')
                r = requests.get(file_url, headers=headers)
                with open(filename, 'wb') as cover_jpg:
                    cover_jpg.write(r.content)
        except:
            pass



parser = argparse.ArgumentParser()
parser.add_argument('url')
args = parser.parse_args()

info_url = 'https://www.imdb.com/title/'+args.url
gallery_url = 'https://www.imdb.com/title/{}/mediaindex' .format(args.url)

get_info(info_url)
get_gallery(gallery_url)

