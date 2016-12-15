#!/usr/bin/env python

import os
import time
import re
import pymysql
from flask import Flask
from flask import render_template
from PIL import Image


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

@app.route("/movies/search/genre/<search>")
def searchgenre(results=None, search=None):
    with connection.cursor() as cursor:
        sql = "select title, imdb, genre from movies where genre like '%{}%'" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
        return render_template('moviesearch.html', results=results)

@app.route("/movies/search/title/<search>")
def searchmovies(results=None, search=None):
    with connection.cursor() as cursor:
        sql = "select title, imdb, genre from movies where title like '%-{}%'" .format(search)
        sql2 = "select imdb from movies where title like '%-{}%'" .format(search)
        connection.escape_string(sql)
        cursor.execute(sql)
        results = [(item[0], item[1], item[2]) for item in cursor.fetchall()]
        return render_template('moviesearch.html', results=results)

@app.route("/gallery")
def gallery():
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'static', 'gallery')):
        for name in dirs:
            return render_template('galleryindex.html', dirs=dirs)

@app.route('/gallery/<gal>')
def get_gallery(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '%s' % gal)
    for subdir, dirs, files in os.walk(dirgl):
        for image in files:
            return render_template('gallerylist.html', gal=gal, files=files)

@app.route('/gallery/<gal>/create')
def create_thumbs(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '%s' % gal)
    dirth = os.path.join(dirgl, 'thumbs')
    if not os.path.exists(dirth):
        os.makedirs(dirth)
    os.chmod(dirth, 0o777)
    for subdir, dirs, files in os.walk(dirgl):
        for image in files:
                thumbc(gal, image)

def thumbc(gal, image):
    sizes = [(250, 250)]
    dirsm = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '%s' % gal)
    dirth = os.path.join(dirsm, 'thumbs')

    for size in sizes:
        im = Image.open(os.path.join(dirsm, image)).convert('RGB')
        im.thumbnail(size, Image.ANTIALIAS)
        thmbs = os.path.join(dirsm, 'thumb_'+image)
        quality_val = 100
        thumbs2 = os.path.join(dirsm, 'thumbs', 'thumb_'+image)
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



if __name__ == "__main__":
    app.run()