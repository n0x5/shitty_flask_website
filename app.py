#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from collections import OrderedDict
from flask_restful import fields, marshal_with
from PIL import Image
import sqlite3
import yaml


app = Flask(__name__)
api = Api(app)
app.debug = True


@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)

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
        image = doc['postroot']['images']

    return render_template('blogit.html', doc=doc, title1=title1, body=body, date=date, image=image)

@app.route("/images")
def gallery2():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort(reverse=True)

        return render_template('gallery2index.html', results2=results2)

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
def i62games(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd \
        from images where fullpath like ? or exifd like ? order by ftime desc", ('%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''), 
                str(item[4]).replace(', ', 'x'), item[5]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)

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
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    genres = [item.title() for item in genrelist]
    return render_template('movieindex.html', genres=genres)

@app.route("/movies/<search>")
def mmgames(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from \
        movies where (genre like ? or infogenres like ? or release like ? or director like ? \
        or mainactors like ? or inforest like ?) order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genre/<search>")
def mmgames2(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated from movies \
        where (genre like ? or infogenres like ?) order by substr(title, -1, -4) desc, dated desc", 
            ('%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/groups")
def movielist(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    sql = 'select grp, count(*) c from movies group by grp having c > 0 order by c desc'
    cursor.execute(sql)
    groups = [(item[0], item[1]) for item in cursor.fetchall()]
    return render_template('moviegroups.html', groups=groups)

@app.route("/movies/group/<search>")
def mmgames3(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), dated \
        from movies where grp like ? order by substr(title, -1, -4) desc, dated desc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
        item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/director")
def moviedirect(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    sql = 'select director, count(distinct(imdb)) c from movies group by director having c > 0 order by c desc'
    cursor.execute(sql)
    groups = [(item[0].strip().replace('\\n', '').replace(',', ''), item[1]) for item in cursor.fetchall()]
    return render_template('moviedirector.html', groups=groups)

@app.route("/movies/years")
def movieyears(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2new2.db'))
    cursor = connection.cursor()
    sql = 'select distinct(year), count(distinct(imdb)) c from movies group by year having c > 0 order by c desc'
    cursor.execute(sql)
    years = [(item[0], item[1]) for item in cursor.fetchall()]
    return render_template('movieyears.html', years=years)

@app.route("/movies/years/<search>")
def mmgames4114(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2new2.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, year, title from movies where year like ? \
        order by year, release asc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
        item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/director/<search>")
def mmgames44(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), title, dated from movies \
        where director like ? order by substr(title, -1, -4) desc, dated desc", ('%'+search+'%',))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/release/<release>")
def movierelease(release=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
    cursor = connection.cursor()
    cursor.execute('select release, grp, genre, format, imdb, title, director, mainactors, infogenres, inforest, \
        infosummary, substr(title, -1, -4) from movies where release like ?', ('%'+release+'%',))
    results = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6].strip(' ').replace('\\n', '').replace(',', ''), 
            item[7].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[8].replace('[', '').replace(']', '').replace('\'', ''), item[9].replace('[', '').replace(']', '').replace('\'', ''), 
            item[10], item[11].replace(')', '').replace('(', '')) for item in cursor.fetchall()]
    return render_template('releasedetails.html', results=results)

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
        results = [basename(image).decode('utf-8').replace('#', '%23') for image in results2]
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
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'moviesim2.db'))
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
        results3 = {"data":{"release": '{}' .format(item3[0]), "director": '{}' .format(item3[1]), "imdb": '{}' .format(item3[2]), 
                    "genres": '{}' .format(item3[3]), "year": '{}' .format(item3[4]), "main_actors": '{}' .format(item3[5]),
                    "plot_summary": '{}' .format(item3[6])}}
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


