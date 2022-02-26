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


@app.route("/gamesv2")
def games2index():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select orig_system, count(distinct(title)) c from gamesv2 group by orig_system having c > 0 order by c desc"
    groups = [(item[0], item[1]) for item in conn.execute(sql)]

    sql2 = "select publisher, count(distinct(title)) c from gamesv2 group by publisher having c > 2 order by c desc"
    publishers = [(item[0], item[1]) for item in conn.execute(sql2)]

    sql4 = "select developer, count(distinct(title)) c from gamesv2 group by developer having c > 2 order by c desc"
    developers = [(item[0], item[1]) for item in conn.execute(sql4)]

    sql3 = "select year, count(distinct(title)) c from gamesv2 group by year having c > 2 order by c desc"
    years = [(item[0], item[1]) for item in conn.execute(sql3)]

    conn.close()
    gcounts = len(groups)
    return render_template('gamesv2index.html', groups=groups, publishers=publishers, years=years, developers=developers)

@app.route("/gamesv2/system/<search>")
def v2systemsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where orig_system like ? order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games2_search.html', results=results, search=search, gcounts=gcounts)


@app.route("/gamesv2/sysexclusive/<search>")
def v2systemexclsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(systems) = ? order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/conxclusive/<search>")
def v2systemconexclsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) like ? and systems not like '%PC%') group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/publisher/<search>")
def v2publishersearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(publisher) like ? group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/developer/<search>")
def v2developersearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(developer) like ? group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games2_search.html', results=results, search=search, gcounts=gcounts)