try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
import re
import requests

@app.route("/flm")
def flm_index(results=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies-flm.db'))
    sql = 'select * from flmlist order by year desc'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('flm/flm_index.html', results=results, count=count)
