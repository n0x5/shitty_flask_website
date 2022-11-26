try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
import re
import requests
from flask import session
from flask import request
from flask import redirect
from werkzeug.utils import secure_filename


@app.route("/paranormal")
def para_index(results=None, search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'paranormal.db'))
    sql = "select distinct(section), count(section) from paranormal group by section order by section asc"
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('paranormal/para_index.html', results=results, count=count)



@app.route("/paranormal/<section>")
def para_section(results=None, section=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'paranormal.db'))
    sql = 'select subsection, section from paranormal where section like ? order by section asc'
    results = [item for item in conn.execute(sql, (section,))]
    count = len(results)
    conn.close()
    return render_template('paranormal/para_index_subsection.html', results=results, count=count)


@app.route("/paranormal/<section>/<article>")
def para_article(results=None, section=None, article=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'paranormal.db'))
    sql = 'select subsection, body, section from paranormal where section like ? and subsection like ? order by section asc'
    results = [item for item in conn.execute(sql, (section, article))]
    count = len(results)
    conn.close()
    return render_template('paranormal/para_index_article.html', results=results, count=count)


