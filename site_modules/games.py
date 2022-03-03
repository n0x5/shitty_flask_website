try:
    from __main__ import app
except:
    from app import app
from flask import render_template
import sqlite3
import os
from flask import request
from flask import flash

###################### GAMES #########################


@app.route("/gamesv2")
def games2index():
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select orig_system, count(distinct(title)) c from gamesv2 group by orig_system having c > 0 order by c desc"
    groups = [(item[0], item[1]) for item in conn.execute(sql)]

    sql2 = "select publisher, count(distinct(title)) c from gamesv2 group by publisher having c > 40 order by c desc"
    publishers = [(item[0], item[1]) for item in conn.execute(sql2)]

    sql4 = "select developer, count(distinct(title)) c from gamesv2 group by developer having c > 40 order by c desc"
    developers = [(item[0], item[1]) for item in conn.execute(sql4)]

    sql3 = "select year, count(distinct(title)) c from gamesv2 group by year having c > 2 order by c desc"
    years = [(item[0], item[1]) for item in conn.execute(sql3)]

    sql5 = "select genre, count(distinct(title)) c from gamesv2 group by genre having c > 10 order by c desc"
    genres = [(item[0], item[1]) for item in conn.execute(sql5)]

    conn.close()
    gcounts = len(groups)
    return render_template('games/games2_index.html', groups=groups, publishers=publishers, years=years, developers=developers, genres=genres)

@app.route("/gamesv2/system/<search>")
def v2systemsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where orig_system like ? order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)


@app.route("/gamesv2/exclusives/<search>")
def v2systemexclsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) = ? and orig_system = ?) order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search, search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/notonpc/<search>")
def v2systemconexclsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) like ? and systems not like '%PC%' and orig_system = ?) group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%', search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/publisher/<search>")
def v2publishersearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(publisher) like ? group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/developer/<search>")
def v2developersearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(developer) like ? group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/genre/<search>")
def v2genresearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where lower(genre) like ? group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/system/na/<search>")
def v2systemsearchregionna(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (orig_system like ? and na is not null and na not like 'Unreleased' and na not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/system/eu/<search>")
def v2systemsearregioneu(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (orig_system like ? and eu is not null and eu not like 'Unreleased' and eu not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/system/jp/<search>")
def v2systemsearregionjp(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (orig_system like ? and jp is not null and jp not like 'Unreleased' and jp not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/exclusives/na/<search>")
def v2systemexclsearchregionna(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) = ? and orig_system = ? and na is not null and na not like 'Unreleased' and na not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search, search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/notonpc/na/<search>")
def v2systemconexclsearchregionna(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) like ? and systems not like '%PC%' and orig_system = ? and na is not null and na not like 'Unreleased' and na not like '') group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%', search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/system/eu/<search>")
def v2systemsearchregioneu(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (orig_system like ? and eu is not null and eu not like 'Unreleased' and eu not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)


@app.route("/gamesv2/exclusives/eu/<search>")
def v2systemexclsearchregioneu(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) = ? and orig_system = ? and eu is not null and eu not like 'Unreleased' and eu not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search, search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/notonpc/eu/<search>")
def v2systemconexclsearchregioneu(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) like ? and systems not like '%PC%' and orig_system = ? and eu is not null and eu not like 'Unreleased' and eu not like '') group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%', search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/system/jp/<search>")
def v2systemsearchregionjp(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (orig_system like ? and jp is not null and jp not like 'Unreleased' and jp not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search,))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)


@app.route("/gamesv2/exclusives/jp/<search>")
def v2systemexclsearchregionjp(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) = ? and orig_system = ? and jp is not null and jp not like 'Unreleased' and jp not like '') order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, (search, search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)

@app.route("/gamesv2/notonpc/jp/<search>")
def v2systemconexclsearchregionjp(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'gamesv2.db'))
    sql = "select title, genre, developer, publisher, year, systems, orig_system from gamesv2 \
            where (lower(systems) like ? and systems not like '%PC%' and orig_system = ? and jp is not null and jp not like 'Unreleased' and jp not like '') group by title order by year asc"
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in conn.execute(sql, ('%'+search+'%', search))]
    conn.close()
    gcounts = len(results)
    return render_template('games/games2_search.html', results=results, search=search, gcounts=gcounts)



###################### old games

@app.route("/games")
def igames(search=None):
    return render_template('games/games_index.html')

@app.route("/games/<search>")
def sgames(search=None):
    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'games.db'))
    cursor = connection.cursor()
    cursor.execute("select title, systems, rlsdate from games where systems like ? \
        order by substr(rlsdate, -4), title", ('%'+search+'%',))
    results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('games/games.html', results=results, search=search, gcounts=gcounts)
