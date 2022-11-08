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

@app.route("/flm")
def flm_index(results=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies-flm.db'))
    sql = 'select * from flmlist order by year desc'
    results = [item for item in conn.execute(sql)]
    sql2 = 'select country, count(distinct(imdb)) c from flmlist group by country order by c desc'
    countries = [item2 for item2 in conn.execute(sql2)]
    count = len(results)
    conn.close()
    return render_template('flm/flm_index.html', results=results, count=count, countries=countries)


@app.route("/flm/<search>")
def flm_search(results=None, search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies-flm.db'))
    sql = 'select * from flmlist where imdb like ?'
    results = [item for item in conn.execute(sql, (search,))]
    dir1 = os.path.join(app.root_path, 'static', 'flm_images', search)
    list_img = []
    for subdir, dirs, files in os.walk(dir1):
        for fn in files:
            list_img.append(fn)
    count = len(results)
    conn.close()
    return render_template('flm/flm_search.html', results=results, count=count, list_img=list_img, search=search)


@app.route('/file-upload/<search>', methods=['GET', 'POST'])
def upload_file_flm(search=None):
    upload = os.path.join(app.root_path, 'static', 'flm_images')
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if not os.path.exists(os.path.join(upload, search)): 
                os.makedirs(os.path.join(upload, search))
            try:
                os.chmod(os.path.join(upload, search), 0o777)
            except Exception:
                pass
            file.save(os.path.join(upload, search, filename))
            return redirect('/flm/{}'.format(search))
