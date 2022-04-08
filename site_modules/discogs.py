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


@app.route("/discogs")
def discogs_index():
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs_releases_new.db'))
    sql = "select label_name, count(distinct(id)) c from discogs_releases where label_name not like 'Not On Label' group by label_name having c > 500 order by c desc"
    groups = [item for item in conn.execute(sql)]

    return render_template('discogs/discogs_index.html', groups=groups)


@app.route("/discogs/search/<genre>/<country>/<label>")
def discogs_search_cogenre(genre=None, country=None, label=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs_releases_new.db'))
    sql = "select released, label_name, title from discogs_releases where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and country like ? and label_name like ? order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country, label))]

    return render_template('discogs/discogs_search.html', results=results)

@app.route("/discogs/search/<genre>/<country>")
def discogs_search_cogenre_2(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs_releases_new.db'))
    sql = "select discogs_releases.released, discogs_releases.label_name, discogs_releases.title, discogs_rel_artists.artist_name from discogs_releases join discogs_rel_artists on discogs_releases.id = discogs_rel_artists.release_id where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and country like ? and format_name like 'CD' group by id order by label_name, released, artist_name desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)

