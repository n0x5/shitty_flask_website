try:
    from __main__ import app
except:
    from app import app
from flask import render_template
import sqlite3
import os

###################### GAMES #########################

@app.route("/games")
def igames(search=None):
    return render_template('gamesindex.html')

@app.route("/games/<search>")
def sgames(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'games.db'))
    cursor = connection.cursor()
    cursor.execute("select title, systems, rlsdate from games where systems like ? \
        order by substr(rlsdate, -4), title", ('%'+search+'%',))
    results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('games.html', results=results, search=search, gcounts=gcounts)