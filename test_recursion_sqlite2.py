import sqlite3
import os


connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies44.db'))
cursor = connection.cursor()

all_pages = []

def pages(search, lastvalue):
    cursor.execute('select release, director from movies where release like ? and release > ? order by release limit 8', ('%'+search+'%', lastvalue))
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
            cursor.execute('select release, director from movies where release like ? and release > ? order by release limit 8', ('%'+search+'%', firstvalue))
            results = [(item[0], item[1]) for item in cursor.fetchall()]
            all_pages.append(results)


search = 'men.in.black'
lastvalue = ''
pages(search, lastvalue)

page = 0
for item in all_pages:
    page += 1
    print(page, item)

cursor.close()