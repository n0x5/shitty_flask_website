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

@app.route("/tutorials")
def tp_index(results=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'tutorialspoint.db'))
    sql = 'select distinct(section) from tutorialspoint order by section'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('tp/tp_index.html', results=results, count=count)


@app.route("/tutorials/category/<search>")
def tp_category(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'tutorialspoint.db'))
    sql = "select title, section from tutorialspoint where section like ? order by title"
    results = [item for item in conn.execute(sql, (search,))]
    count = len(results)
    conn.close()
    return render_template('tp/tp_section.html', results=results, count=count, search=search)


@app.route("/tutorials/<section>/<title>")
def tp_article(title=None, section=None, content=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'tutorialspoint.db'))
    sql = "select title, section, content_html from tutorialspoint where (title like ? and section like ?) order by title"
    results = [item for item in conn.execute(sql, (title, section))]
    count = len(results)
    conn.close()
    return render_template('tp/tp_article.html', results=results, count=count)