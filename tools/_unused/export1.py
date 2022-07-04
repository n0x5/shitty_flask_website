import sqlite3
import argparse
import os

#parser = argparse.ArgumentParser()
#parser.add_argument('year')
#args = parser.parse_args()

sql_db = os.path.join(os.path.dirname( __file__ ), '..', 'databases', 'movies.db')

conn = sqlite3.connect(sql_db)
sql = 'select boxoffice2.* from boxoffice2 where theaters like "Wide"'
results = [item for item in conn.execute(sql)]

with open('list_all_wide.html', 'a') as log_file:
    log_file.write('<style>table, th, td {border: 1px solid;border-collapse:collapse;padding:4px;}</style>')
    log_file.write('<h1>List of all horror US theatrical releases</h1>')
    log_file.write('<table>')
    log_file.write('<tr><td><h3>Title</h3></td><td><h3>Year</h3></td><td><h3>Theaters</h3></td><td><h3>Genres</h3></td><td><h3>Studio</h3></td><td><h3>Stars</td></h3><td><h3>IMDB</td></h3></tr>')
    for item2 in results:
        log_file.write('<tr>')
        log_file.write('<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td><a href="https://www.imdb.com/title/{}">{}</a></td>'.format(item2[0], item2[7], item2[5], item2[1], item2[4], item2[8], item2[3], item2[3]))
        log_file.write('</tr>')
        print(item2[0], item2[1], item2[4], item2[7], item2[8])
    log_file.write('</table>')