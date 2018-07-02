#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
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

app = Flask(__name__)
api = Api(app)
app.debug = True
app.config.update(dict(
        DEBUG=True,
        SECRET_KEY=b'SECRET_KEY',
        USERNAME='ADMIN_USERNAME',
        PASSWORD='ADMIN_PASSWORD'
    ))

@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)

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

        connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
        cursor2 = connection2.cursor()
        sql2 = 'select * from (select * from movies order by dated desc limit 10) order by dated desc'
        cursor2.execute(sql2)
        results2 = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]) for item in cursor2.fetchall()]
        cursor2.close()

    return render_template('dashboard.html', results=results, results2=results2)


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
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
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

@app.route("/movies")
def movieindex(genres=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select release from movies')
    results = [item for item in cursor.fetchall()]
    count = len(results)
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    genres = [item.title() for item in genrelist]
    cursor.close()
    return render_template('movieindex.html', genres=genres, count=count)


@app.route("/movies/<search>")
def mmgames(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
        movies where (genre like ? or infogenres like ? or release like ? or director like ? \
        or mainactors like ? or inforest like ? or imdb like ?) order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in cursor.fetchall()]
    #names = cursor.keys()
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/cast/<search>")
def mmgames333(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor1 = connection.cursor()
    cursor1.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
        movies where mainactors like ? order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%',))
    results1 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor1.fetchall()]
    gcounts = len(results1)
    cursor1.close()
    cursor2 = connection.cursor()
    cursor2.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
        movies where (inforest like ? and mainactors not like ?) order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%', '%'+search+'%'))
    results2 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in cursor2.fetchall()]
    gcounts2 = len(results2)+len(results1)
    cursor2.close()
    return render_template('moviecast.html', results=results1, search=search, gcounts=gcounts2, results2=results2)


@app.route("/movies/genre/<search>")
def mmgames2(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from movies \
        where (genre like ? or infogenres like ?) order by substr(title, -1, -4) desc, dated desc", 
            ('%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genre/<search>/<search2>")
def mmgames112(search=None, search2=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from movies \
        where (genre like ? or infogenres like ?) and (genre like ? or infogenres like ?) order by substr(title, -1, -4) desc, dated desc", 
            ('%'+search+'%', '%'+search+'%', '%'+search2+'%', '%'+search2+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/groups")
def movielist(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    sql = 'select grp, count(*) c from movies group by grp having c > 0 order by c desc'
    cursor.execute(sql)
    groups = [(item[0], item[1]) for item in cursor.fetchall()]
    return render_template('moviegroups.html', groups=groups)

@app.route("/movies/group/<search>")
def mmgames3(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated \
        from movies where grp like ? order by substr(title, -1, -4) desc, dated desc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
        item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/director")
def moviedirect(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    sql = 'select director, count(distinct(imdb)) c from movies group by director having c > 0 order by c desc'
    cursor.execute(sql)
    groups = [(item[0].strip().replace('\\n', '').replace(',', ''), item[1]) for item in cursor.fetchall()]
    return render_template('moviedirector.html', groups=groups)

@app.route("/movies/years")
def movieyears(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    sql = 'select distinct(year), count(distinct(imdb)) c from movies group by year having c > 0 order by c desc'
    cursor.execute(sql)
    years = [(item[0], item[1]) for item in cursor.fetchall()]
    return render_template('movieyears.html', years=years)

@app.route("/movies/years/<search>")
def mmgames4114(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, year, title from movies where year like ? \
        order by year, release asc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
        item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/director/<search>")
def mmgames44(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), title, dated from movies \
        where director like ? order by substr(title, -1, -4) desc, dated desc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/company")
def companylist():
    connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imdb_scrape_database2.db'))
    cursor2 = connection2.cursor()
    sql = 'select company, title, count(distinct(imdbid)) c from companies group by company having c > 0 order by c desc'
    cursor2.execute(sql)
    companies = [(item[0], item[1], item[2]) for item in cursor2.fetchall()]
    cursor2.close()
    return render_template('company_list_all.html', companies=companies)

@app.route("/movies/company/all/<studio>")
def companylist2(studio=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imdb_scrape_database2.db'))
    cursor = connection.cursor()
    cursor.execute('select company, imdbid, title, year, role from companies where company like ? order by year desc, title desc', ('%'+studio+'%',))
    companies = [(item[0], item[1], item[2], item[3], item[4]) for item in cursor.fetchall()]
    count = len(companies)
    cursor.close()
    return render_template('company_list.html', companies=companies, count=count, studio=studio)

@app.route("/movies/company/<studio>")
def companylist3(studio=None):
    film_list = []
    connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imdb_scrape_database2.db'))
    cursor2 = connection2.cursor()
    cursor2.execute('select company, imdbid, title, year, role from companies where company like ? group by title order by year desc, title desc', ('%'+studio+'%',))
    companies = [(item2[0], item2[1], item2[2], item2[3], item2[4]) for item2 in cursor2.fetchall()]
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()

    for item3 in companies:

        cursor.execute('select distinct imdb from movies where imdb like ?', ('%'+item3[1]+'%',))
        [film_list.append(item3) for item in cursor.fetchall()]
    count = len(film_list)
    cursor2.close()
    cursor.close()
    return render_template('company_list2.html', companies=companies, results=film_list, count=count, studio=studio)


@app.route("/movies/seven2")
def sevent2wen(results=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select release, imdb, year from movies where imdb not in (select imdb from movies720) order by year desc')
    results = [(item) for item in cursor.fetchall()]
    cursor.close()
    return render_template('movies2.html', results=results)


@app.route("/movies/release/<release>")
def movierelease(release=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select release, grp, genre, format, imdb, title, director, mainactors, infogenres, inforest, \
        infosummary, substr(title, -1, -4), imdb from movies where release like ?', ('%'+release+'%',))

    results = [(item[0], item[1], item[2], item[3], os.path.basename(item[4]+'.jpg'), item[5], item[6].strip(' ').replace('\\n', '').replace(',', ''), 
            item[7].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[8].replace('[', '').replace(']', '').replace('\'', ''), item[9].replace('[', '').replace(']', '').replace('\'', ''), 
            item[10], item[11].replace(')', '').replace('(', ''), item[12]) for item in cursor.fetchall()]
    imdborig = re.search(r'\d{7}', str(results[0][4]))
    imdbidor = imdborig.group(0)
    connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imdb_scrape_database2.db'))
    cursor2 = connection2.cursor()
    try:
        cursor2.execute('select company, imdbid from companies where imdbid like ?', ('%'+imdbidor+'%',))
        results3 = [item2 for item2 in cursor2.fetchall()]
    except:
        results3 = ('None',)
    cursor.close()
    cursor2.close()

    return render_template('releasedetails.html', results=results, results3=results3, compane=imdbidor)

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


