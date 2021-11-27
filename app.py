#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    import sys
    reload(sys)  
    sys.setdefaultencoding('utf8')
except:
    pass
import os
import time
import re
from os.path import basename
import markdown
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
from flask import send_from_directory
from flask import Markup
from flask import Flask
from flask import session
from flask import current_app
from flask import flash
import datetime
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from collections import OrderedDict
from flask_restful import fields, marshal_with
from PIL import Image
import sqlite3
import yaml
import zipfile
import configs

app = Flask(__name__)
api = Api(app)
app.debug = True
app.config.update(configs.conf) # edit configs-sample.py and rename to configs.py

@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)




####### FILE UPLOAD DRAG N DROP ######

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp3', 'mp4', 'mkv', 'avi'])
UPLOAD_FOLDER = r'/home/coax/websites/hidden2/virtualenv-3.3.5/FlaskApp/static/hosted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/uploadf/<gal>', methods=['GET', 'POST'])
def upload_form(gal=None):
    if not session.get('logged_in'):
        return 'access denied'

    return render_template('upload.html', gal=gal)

@app.route('/file-upload/<gal>', methods=['GET', 'POST'])
def upload_file(gal=None):
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/uploadf')
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], gal)): 
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], gal))
            os.chmod(os.path.join(app.config['UPLOAD_FOLDER'], gal), 0o777)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], gal, filename))
            flash('File successfully uploaded')
            return redirect('/uploadf')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect('/uploadf')



@app.route('/pics/<gal>')
def get_gallery_pics(gal=None, results3=None, gcount=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'hosted', '{}' .format(gal))
    for subdir, dirs, files in os.walk(str(dirgl)):
        if 'thumbs' not in subdir:
            results2 = [os.path.join(dirgl, image) for image in files]
            #results2.sort(key=os.path.getmtime, reverse=True)
            results2.sort()

        imh = [str(Image.open(image).size).replace('(', '').replace(')', '').replace(', ', 'x') for image in results2]
        results4 = [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(image))) for image in results2]
        results = [basename(image).replace('#', '%23') for image in results2]
        gcount = len(results)
        results3 = zip(results, imh, results4)

    return render_template('galleryhosted.html', gal=gal, results3=results3, gcount=gcount)


@app.route('/pics')
def get_gallery_folders():
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'hosted')
    empty1 = []
    empty2 = []
    for subdir, dirs, files in os.walk(dirgl):
        empty1.append(os.path.basename(subdir))

    return render_template('picsindex.html', empty1=empty1)


@app.route("/images/wallpaper/<search>/<sizew>/<sizeh>")
def i7gam111es(search=None, sizew=None, sizeh=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images \
        where (fullpath like ? or exifd like ?) and (sizewidth like ? and sizeheight like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', int(sizew), int(sizeh)))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''),
                 str(item[4]).replace(', ', 'x'), item[5], item[6]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)


###################### ADMIN / STUFF #########################

@app.route('/rinfo')
def inde22x():
    if session.get('logged_in'):
        username = current_app.config['USERNAME']
        return 'Logged in as ' + username + '<br>' + \
        "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + \
        "click here to log in</b></a>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('inde22x'))
    return render_template('login.html', error=error)    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('inde22x'))




@app.route('/dashboard', methods=['GET', 'POST'])
def dash1(results=None):
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'GET' or request.method == 'POST':
        sql = 'select file, subfolder, ftime from (select file, subfolder, ftime from images order by ftime DESC limit 10) order by ftime DESC'
        connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
        cursor = connection.cursor()
        cursor.execute(sql)
        results = [(item[0], item[1]) for item in cursor.fetchall()]
        cursor.close()

        connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
        cursor2 = connection2.cursor()
        sql2 = 'select * from (select * from movies order by dated desc limit 20) order by dated desc'
        cursor2.execute(sql2)
        results2 = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]) for item in cursor2.fetchall()]
        cursor2.close()

    return render_template('dashboard.html', results=results, results2=results2)



########################## MOVIES ############################


@app.route("/movies")
def movieindex(genres=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = 'select release from movies'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    genres = [item.title() for item in genrelist]
    conn.close()
    return render_template('movieindex.html', genres=genres, count=count)

@app.route("/movies/<search>")
def moviesearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
            movies where (genre like ? or infogenres like ? or release like ? or director like ? \
            or mainactors like ? or inforest like ? or imdb like ?) order by substr(title, -1, -4) desc, dated desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in \
    conn.execute(sql, ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/cast/<search>")
def castsearch(search=None):
    conn1 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql1 = "select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
            movies where mainactors like ? order by substr(title, -1, -4) desc, dated desc"

    results1 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
    conn1.execute(sql1, ('%'+search+'%',))]
    conn1.close()

    conn2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql2 = "select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
            movies where (inforest like ? and mainactors not like ?) order by substr(title, -1, -4) desc, dated desc"

    results2 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in \
    conn2.execute(sql2, ('%'+search+'%', '%'+search+'%'))]
    conn2.close()
    gcounts2 = len(results2)+len(results1)
    return render_template('moviecast.html', results=results1, search=search, gcounts=gcounts2, results2=results2)

@app.route("/movies/genrewide/<search>")
def genrewidesearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4), \
        boxoffice.rlid, boxoffice.wide_theatersopen from movies join boxoffice on movies.imdb = boxoffice.imdbid where (movies.genre like ? or movies.infogenres like ?) \
        and wide_theatersopen > 2000 and boxoffice.wide_theatersopen != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
    conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genreltd/<search>")
def genreltdsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4), \
        boxoffice.rlid, boxoffice.alt_theaters from movies join boxoffice on movies.imdb = boxoffice.imdbid where (movies.genre like ? or movies.infogenres like ?) \
        and boxoffice.alt_theaters < 2000 and boxoffice.alt_theaters != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genrevideo/<search>")
def genrevideosearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4) \
        from movies where imdb not in (select imdbid from boxoffice) and (genre like ? or infogenres like ?) group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/yearwide/<search>")
def yearwidesearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4), \
        boxoffice.rlid, boxoffice.wide_theatersopen from movies join boxoffice on movies.imdb = boxoffice.imdbid where movies.year like ? \
        and wide_theatersopen > 2000 and boxoffice.wide_theatersopen != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
    conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/yearltd/<search>")
def yearltdsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4), \
        boxoffice.rlid, boxoffice.alt_theaters from movies join boxoffice on movies.imdb = boxoffice.imdbid where movies.year like ? \
        and boxoffice.alt_theaters < 2000 and boxoffice.alt_theaters != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
             conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/yearvideo/<search>")
def yearvideosearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, substr(movies.title, -1, -4) \
        from movies where imdb not in (select imdbid from boxoffice) and movies.year like ? group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies7.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/genre/<search>")
def genresearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, substr(title, -1, -4), dated from movies \
            where (genre like ? or infogenres like ?) order by substr(title, -1, -4) desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/groups")
def grouplist(groups=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select grp, count(*) c from movies group by grp having c > 0 order by c desc"
    groups = [(item[0], item[1]) for item in conn.execute(sql)]
    conn.close()
    gcounts = len(groups)
    return render_template('moviegroups.html', groups=groups)


@app.route("/movies/group/<search>")
def groupsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, substr(title, -1, -4), dated \
            from movies where grp like ? order by substr(title, -1, -4) desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/director")
def director(groups=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select director, count(distinct(imdb)) c from movies group by director having c > 0 order by c desc"
    groups = [(item[0].strip().replace('\\n', '').replace(',', ''), item[1]) for item in \
                 conn.execute(sql)]
    conn.close()
    gcounts = len(groups)
    return render_template('moviedirector.html', groups=groups)


@app.route("/movies/director/<search>")
def directorsearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, substr(title, -1, -4), title, dated from movies \
            where director like ? order by substr(title, -1, -4) desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/years")
def movieyears(groups=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select distinct(year), count(distinct(imdb)) c from movies group by year having c > 0 order by c desc"
    years = [(item[0], item[1]) for item in conn.execute(sql)]
    conn.close()
    return render_template('movieyears.html', years=years)


@app.route("/movies/years/<search>")
def movieyearssearch(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, title from movies where year like ? \
            order by year, release asc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/boxgenres")
def moviesbox1():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    sql = 'select distinct(genre) from movie_genres'
    results = [(item[0],) for item in conn.execute(sql)]
    conn.close()

    return render_template('movies-boxgenres.html', results=results)

@app.route("/movies/company")
def companylist():
    connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'imdb_scrape_database2.db'))
    cursor2 = connection2.cursor()
    sql = 'select company, title, count(distinct(imdbid)) c from companies group by company having c > 0 order by c desc'
    cursor2.execute(sql)
    companies = [(item[0], item[1], item[2]) for item in cursor2.fetchall()]
    cursor2.close()

    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    cursor = connection.cursor()
    sql2 = 'select company, count(distinct(imdbid)) c from companyinfo join movies on movies.imdb = "tt" || companyinfo.imdbid group by company having c > 10 order by c desc'
    cursor.execute(sql2)
    companies2 = [(item[0], item[1]) for item in cursor.fetchall()]
    return render_template('company_list_all.html', companies=companies, companies2=companies2)

@app.route("/movies/company/all/<studio>")
def companylist2(studio=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'imdb_scrape_database2.db'))
    cursor = connection.cursor()
    cursor.execute('select company, imdbid, title, year, role from companies where company like ? order by year desc, title desc', ('%'+studio+'%',))
    companies = [(item[0], item[1], item[2], item[3], item[4]) for item in cursor.fetchall()]
    count = len(companies)
    cursor.close()
    return render_template('company_list.html', companies=companies, count=count, studio=studio)

@app.route("/movies/company/<studio>")
def companylist3(studio=None):
    film_list = []
    genres_list = []
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select movies.release, movies.year, movies.imdb, movies.infogenres from companyinfo join movies on movies.imdb = "tt" || companyinfo.imdbid where companyinfo.company like ? group by movies.release order by movies.year desc', ('%'+studio+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    count = len(results)
    cursor.close()
    return render_template('company_list2.html', results=results, count=count, studio=studio)

@app.route("/movies/release/<release>")
def movierelease(release=None):
    colist = []
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select release, grp, genre, format, imdb, title, director, mainactors, infogenres, inforest, \
        infosummary, substr(title, -1, -4), imdb from movies where release like ?', ('%'+release+'%',))

    results = [(item[0], item[1], item[2], item[3], os.path.basename(item[4]+'.jpg'), item[5], item[6].strip(' ').replace('\\n', '').replace(',', ''), 
            item[7].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[8].replace('[', '').replace(']', '').replace('\'', '').split(','), item[9].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[10], item[11].replace(')', '').replace('(', ''), item[12]) for item in cursor.fetchall()]
    remaining_cast = (item.strip() for item in results[0][9])
    main_cast = (item.strip() for item in results[0][7])
    genres_list = (item.strip() for item in results[0][8])
    imdborig = re.search(r'\d{7}', str(results[0][4]))
    imdbidor = imdborig.group(0)
    imdbor2 = 'tt'+imdbidor
    rls = str(results[0][0])

    connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'imdb_scrape_database2.db'))
    connection3 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movie-genres.db'))
    connection7 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'moviesdb-divx.db'))
    cursor3 = connection3.cursor()
    cursor2 = connection2.cursor()
    cursor7 = connection7.cursor()
    cursor7.execute('select rel_time_readable, release from db_movies where release like ?', ('%'+rls+'%',))
    cursor2.execute('select company, imdbid from companies where imdbid like ?', ('%'+imdbidor+'%',))
    cursor3.execute('select genre, theaters, distributor, imdb_id from movie_genres where imdb_id like ?', ('%'+imdbor2+'%',))
    cursor.execute('select company, imdbid from companyinfo where imdbid like ? group by company', ('%'+imdbidor+'%',))
    try:
        results3 = [item2 for item2 in cursor2.fetchall()]
        results6 = [item6 for item6 in cursor3.fetchall()]
        results4 = [item3 for item3 in cursor.fetchall()]
        results7 = [item7 for item7 in cursor7.fetchall()]

        try:
            pre_date = results7[0][0]
        except:
            pre_date = 'None'

        try:
            theaters = results6[0][1]
        except:
            theaters = 0
        try:
            distributor = results6[0][2]
        except:
            distributor = 'None'

    except:
        results3 = ('None',)
        results6 = [('None', 'None', 'None',)]

    return render_template('releasedetails.html', results=results, results3=results3, results4=results4, compane=imdbidor, \
                main_cast=main_cast, remaining_cast=remaining_cast, genres_list=genres_list, release=release, results6=results6, \
                theaters=theaters, distributor=distributor, pre_date=pre_date)


    cursor.close()
    cursor2.close()
    cursor3.close()



###################### BLOG #########################


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        filename = os.path.join(os.path.dirname(__file__), 'posts', request.form['title']+'.yaml')
        with open(filename, 'w+') as f:
            datafile = '''
postroot:
    title: {}
    body: {}
    date: {}
''' .format(request.form['title'], request.form['body'], time.strftime("%m/%d/%Y"))
            f.write(datafile)

        flash('New entry was successfully posted')
        
    return render_template('addyaml.html')


@app.route('/blog')
def blogit():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'posts'))):
        results3 = [os.path.join(root, post1) for post1 in files]
        results3.sort(key=os.path.getmtime, reverse=True)
        results2 = [basename(post1).split('.')[0] for post1 in results3]
    return render_template('blogindex.html', results2=results2)

@app.route('/blog/<post>')
def blogit2(post=None):
    filename = os.path.join(os.path.dirname(__file__), 'posts', post+'.yaml')
    with open(filename, 'r') as f:
        doc = yaml.load(f)
        title1 = doc['postroot']['title']
        body = Markup(markdown.markdown(doc['postroot']['body']))
        date = doc['postroot']['date']

    return render_template('blogit.html', doc=doc, title1=title1, body=body, date=date)


###################### IMAGES #########################

@app.route("/images")
def gallery2():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort(reverse=True)

        return render_template('gallery2index.html', results2=results2)


@app.route("/images3/celebs")
def celblist(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagename5.db'))
    cursor = connection.cursor()
    sql = 'select cname, count(fn) c, cname, subfolder from celebs group by cname having c > 0 order by c desc'
    cursor.execute(sql)
    years = [(item[0], item[1], item[2].replace(' ', '%25')) for item in cursor.fetchall()]
    return render_template('celeblist.html', years=years)


@app.route("/images/<search>/<sizew>")
def i7games(search=None, sizew=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images \
        where (fullpath like ? or exifd like ?) and sizewidth > ? order by ftime desc", ('%'+search+'%', '%'+search+'%', int(sizew)))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''),
                 str(item[4]).replace(', ', 'x'), item[5]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)


@app.route("/images/<search>")
def i613games(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd, celebname \
        from images where (fullpath like ? or exifd like ? or celebname like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''), 
                str(item[4]).replace(', ', 'x'), item[5], item[6], item[7], item[8].replace('[', '').replace("'", "").replace(']', '')) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('imagesname.html', results=results, search=search, gcounts=gcounts)


@app.route("/images/<search>/zip")
def i613games222(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd, celebname \
        from images where (fullpath like ? or exifd like ? or celebname like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''), 
                unicode(item[4]).replace(', ', 'x'), item[5], item[6], item[7], item[8].replace('[', '').replace("'", "").replace(']', '')) for item in cursor.fetchall()]
    zipr = os.path.join(os.path.dirname(__file__), 'static', '{}_{}.zip' .format(search.replace('%', '_'), time.strftime("%m_%d_%Y")))
    with zipfile.ZipFile(zipr, 'w' ) as myzip:
        for fi2 in results:
            path1 = os.path.join(os.path.dirname(__file__), 'static', 'gallery', fi2[2].encode('utf8'), fi2[0].encode('utf8'))
            myzip.write(path1.encode('utf8'), fi2[2].encode('utf8')+'_'+fi2[0].encode('utf8').replace('(', '_').replace(')', '').replace(' ', '_').replace('__', '_'))
    return 'zip complete <a href="/static/{}_{}.zip">{}</a>' .format(search.replace('%', '_'), time.strftime("%m_%d_%Y"), search.replace('%', '_'))


@app.route("/gallery")
def gallery():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort()

        return render_template('galleryindex.html', results2=results2)

@app.route('/gallery/<gal>')
def get_gallery(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    for subdir, dirs, files in os.walk(str(dirgl)):
        if 'thumbs' not in subdir:
            results2 = [os.path.join(dirgl, image) for image in files]
            results2.sort(key=os.path.getmtime, reverse=True)

        imh = [Image.open(image).size for image in results2]
        results = [basename(image).decode('utf-8', errors='replace').replace('#', '%23') for image in results2]
        gcount = len(results)
        results3 = zip(results, imh)

    return render_template('gallerylist.html', gal=gal, results3=results3, gcount=gcount)

@app.route('/gallery/<gal>/create')
def create_thumbs(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    dirth = os.path.join(dirgl, 'thumbs')
    if not os.path.exists(dirth):
        os.makedirs(dirth)
    os.chmod(dirth, 0o777)
    for subdir, dirs, files in os.walk(str(dirgl)):
        for image in files:
                if not image.startswith("thumb_"):
                    try:
                        thumbc(gal, image)
                    except IOError:
                        pass

    return redirect('/gallery/{}' .format(gal), code=302)

def thumbc(gal, image):
    sizes = [(250, 250)]
    dirsm = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    dirth = os.path.join(dirsm, 'thumbs')

    for size in sizes:
        im = Image.open(str(os.path.join(dirsm, image))).convert('RGB')
        im.thumbnail(size, Image.ANTIALIAS)
        thmbs = os.path.join(dirsm, 'thumb_'+image)
        quality_val = 100
        thumbs2 = os.path.join(dirsm, 'thumbs', 'thumb_'+image)
        if not os.path.exists(thumbs2): 
            im.save(thumbs2, "JPEG", quality=quality_val)
            os.chmod(thumbs2, 0o777)



###################### GAMES #########################

@app.route("/games")
def igames(search=None):
    return render_template('gamesindex.html')

@app.route("/games/<search>")
def sgames(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'games.db'))
    cursor = connection.cursor()
    cursor.execute("select title, systems, rlsdate from games where systems like ? \
        order by substr(rlsdate, -4), title", ('%'+search+'%',))
    results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('games.html', results=results, search=search, gcounts=gcounts)






######################## REST API ################

class movieindexa(Resource):
    def get(self):
        genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
        genres = [item.title() for item in genrelist]
        return {'genre': '{}' .format(genres)}

api.add_resource(movieindexa, '/api/moviegenres')

def apisearch(self, search):
    list1 = []
    list2 = []
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), mainactors, infosummary, dated from \
        movies where (genre like ? or infogenres like ? or release like ? or director like ? \
        or mainactors like ? or inforest like ?) order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], 
                item[5], item[6]) for item in cursor.fetchall()]
    for i in range(len(results)): 
        list1.append(results[i])
    for item3 in list1:
        results3 = {"data":{"release": '{}' .format(item3[0].encode('utf-8')), "director": '{}' .format(item3[1].encode('utf-8')), "imdb": '{}' .format(item3[2].encode('utf-8')), 
                    "genres": '{}' .format(item3[3].encode('utf-8')), "year": '{}' .format(item3[4].encode('utf-8')), "main_actors": '{}' .format(item3[5].encode('utf-8')),
                    "plot_summary": '{}' .format(item3[6].encode('utf-8'))}}
        list2.append(results3)

    cursor.close()
    return list2

class moviesearchtitle(Resource):
    def get(self, search):
        rls = apisearch(self, search)
        return {"data":{"children": rls}}

api.add_resource(moviesearchtitle, '/api/moviesearch/<string:search>')



if __name__ == "__main__":
    app.run()


