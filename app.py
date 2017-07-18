#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re
import pymysql
from os.path import basename
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
from flask import send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import sqlite3


app = Flask(__name__)
app.debug = True


@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)


@app.route("/images")
def gallery2():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort()

        return render_template('gallery2index.html', results2=results2)


@app.route("/images/<search>/<sizew>")
def i7games(search=None, sizew=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images where (fullpath like ? or exifd like ?) and sizewidth > ? order by ftime desc", ('%'+search+'%', '%'+search+'%', int(sizew)))
    results = [(item[0], item[1], item[2], str(item[3]).split(' ')[0].replace('.jpg', ''), str(item[4]).replace(', ', 'x'), item[5]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)

@app.route("/images/<search>")
def i62games(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images where fullpath like ? or exifd like ? order by ftime desc", ('%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], str(item[3]).split(' ')[0].replace('.jpg', ''), str(item[4]).replace(', ', 'x'), item[5]) for item in cursor.fetchall()]
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
    cursor.execute("select title, systems, rlsdate from games where systems like ? order by substr(rlsdate, -4), title", ('%'+search+'%',))
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
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies3.db'))
    cursor = connection.cursor()
    cursor.execute("select title, grp, imdb, genre from movies where title like ?", ('%'+search+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genre/<search>")
def mmgames2(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies3.db'))
    cursor = connection.cursor()
    cursor.execute("select title, grp, imdb, genre from movies where genre like ?", ('%'+search+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/groups")
def movielist(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies3.db'))
    cursor = connection.cursor()
    sql = 'select distinct grp from movies'
    cursor.execute(sql)
    groups = [item[0] for item in cursor.fetchall()]
    return render_template('moviegroups.html', groups=groups)

@app.route("/movies/group/<search>")
def mmgames3(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'movies3.db'))
    cursor = connection.cursor()
    cursor.execute("select title, grp, imdb, genre from movies where grp like ?", ('%'+search+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('movies2.html', results=results, search=search, gcounts=gcounts)

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
        results = [basename(image).replace('#', '%23') for image in results2]
        #results = [basename(image).decode('utf-8').replace('#', '%23') for image in results2]
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


if __name__ == "__main__":
    app.run()


