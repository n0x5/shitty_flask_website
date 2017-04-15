#!/usr/bin/env python

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
#app.debug = True

connection = pymysql.connect(host='127.0.0.1',
                             user='',
                             password='',
                             db='movies',
                             charset='utf8',
                             cursorclass=pymysql.cursors.SSCursor)

@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)
  
@app.route("/games")
def lgames(search=None):
    with connection.cursor() as cursor:
        sql = "select title, systems, rlsdate, url from games order by right(rlsdate, 4), systems, title" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
        return render_template('games.html', results=results, search=search)

@app.route("/games/<search>")
def sgames(search=None):
    with connection.cursor() as cursor:
        sql = "select title, systems, rlsdate, url from games where systems like '%{}%' order by right(rlsdate, 4), title" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
        return render_template('games.html', results=results, search=search)



@app.route("/movies")
def movieindex(genres=None):
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport", 
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    genres = [item.title() for item in genrelist]
    return render_template('movieindex.html', genres=genres)

@app.route("/movies/groups")
def movielist(groups=None):
    with connection.cursor() as cursor:
        sql = 'select distinct grp from movies'
        connection.escape_string(sql)
        cursor.execute(sql)
        groups = [''.join(item) for item in cursor]
        return render_template('moviegroups.html', groups=groups)

@app.route("/movies/genre/<search>")
def searchgenre(search=None):
    with connection.cursor() as cursor:
        sql = "select title, imdb, genre from movies where genre like '%{}%'" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
        return render_template('moviesearch.html', results=results, search=search)

@app.route("/movies/group/<search>")
def searchmovies(search=None):
    with connection.cursor() as cursor:
        sql = "select title, imdb, genre from movies where grp like '%{}%'" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
        return render_template('moviesearch.html', results=results, search=search)

@app.route("/movies/title/<search>")
def searchtitle(search=None):
    with connection.cursor() as cursor:
        sql = "select title, imdb, genre from movies where title like '%{}%'" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
        return render_template('moviesearch.html', results=results, search=search)

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
        results = [basename(image) for image in results2]
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


@app.route("/blog")
def get_blog():
    for subdir, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'blog')):
        outpt = [fn.replace(".txt", "") for fn in files]
        return render_template('blogindex.html', outpt=outpt)

@app.route('/blog/<blogid>')
def get_blogid(blogid):
    blogid2 = blogid + '.txt'
    with open(os.path.join(os.path.dirname(__file__), 'blog', blogid2), "r") as content:
        content2 = ''.join(content)
        return render_template('blog.html', content2=content2, blogid=blogid)
      
    
@app.route("/images")
def iisgames(search=None):
    return render_template('imagesindex.html')

@app.route("/images/<search>")
def iigames(search=None):
    connection = sqlite3.connect('images.db')
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder from images where file like ?", ('%'+search+'%',))
    results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)

if __name__ == "__main__":
    app.run()

