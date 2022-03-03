try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
from flask import request
import re
import requests

@app.route("/tv")
def tvindex(results=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'tv.db'))
    sql = 'select imdb_id, show_title, count(imdb_id) c from tv group by show_title having c > 0 order by show_title'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('tv/tv_index.html', results=results, count=count)

@app.route("/tv/<search>")
def tvdetails(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'tv.db'))
    sql = "select show_title, episode_title, air_date, episode_summary, season_number, episode_number, imdb_id from tv where imdb_id like ? order by imdb_id, season_number"
    results = [item for item in conn.execute(sql, ('%'+search+'%',))]
    count = len(results)
    conn.close()
    return render_template('tv/tv_details.html', results=results, count=count)


