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


@app.route("/newsgroups/<search>")
def ng_index(results=None, search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}.db' .format(search)))
    sql = "select distinct(thread), u_stamp, subject, sender from emails where subject not like 're:%' order by u_stamp asc"
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('newsgroups/ng_index.html', results=results, count=count, search=search.replace('_', '.'), search2=search)


@app.route("/newsgroups/<search>/<message>")
def ng_search(results=None, search=None, message=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}.db' .format(search)))
    sql = 'select subject, u_stamp, message, sender from emails where thread like ? order by u_stamp asc'
    results = [item for item in conn.execute(sql, (message,))]
    count = len(results)
    conn.close()
    return render_template('newsgroups/ng_search.html', results=results, count=count, search=search, message=message)


