import sqlite3
import os


connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies44.db'))
cursor = connection.cursor()

all_pages = []
posts_per_page = 15

def pages(search, lastvalue):
    cursor.execute('select release, director from movies where release like ? and release > ? order by release limit ?', ('%'+search+'%', lastvalue, posts_per_page))
    results = [(item[0], item[1]) for item in cursor.fetchall()]
    count = int(len(results))
    count = count - 1
    lastvalue = results[count][0]
    firstvalue = results[0][0]
    all_pages.append(results)

    if lastvalue:
        try:
            pages(search, lastvalue)
        except IndexError:
            cursor.execute('select release, director from movies where release like ? and release > ? order by release limit ?', ('%'+search+'%', firstvalue, posts_per_page))
            results = [(item[0], item[1]) for item in cursor.fetchall()]
            all_pages.append(results)


search = 'diamond'
lastvalue = ''
pages(search, lastvalue)

page = 0
all_dict = {}


for item in all_pages:
    if item:
        page += 1
        all_dict[page] = item


for item in all_dict:
    print(item, all_dict[item])

cursor.close()