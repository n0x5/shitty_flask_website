try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from werkzeug.utils import secure_filename
import markdown
import sqlite3
import re
from datetime import datetime
from uuid import uuid4

# pip install Pygments for code highlighting, rest is automatic

@app.route('/blog2')
def blog2_index():
    for root, dirs, files in os.walk(os.path.join(app.root_path, 'posts')):
        results3 = [os.path.join(root, post1) for post1 in files]
        results3.sort(key=os.path.getctime, reverse=True)
        results2 = [os.path.basename(fn).replace('.md', '') for fn in results3]
    return render_template('blog2/blog2_index.html', results2=results2)

@app.route('/blog2/<post>')
def blog2_post(post=None):
    filename = os.path.join(app.root_path, 'posts', '{}.md' .format(post))
    extension_list = ['codehilite', 'fenced_code', 'extra', 'meta', 'sane_lists', 'toc', 'wikilinks']
    with open(filename, 'r') as f:
        post_text = f.read()
        html = markdown.markdown(post_text, extensions=extension_list)
    return render_template('blog2/blog2_post.html', html=html.replace('<img', '<img width="300"'))

@app.route('/blog2/edit/<post>', methods=['GET', 'POST'])
def blog2_edit(post=None):
    if not session.get('logged_in'):
        return 'access denied'

    filename = os.path.join(app.root_path, 'posts', '{}.md' .format(post))
    with open(filename, 'r') as f:
        post_text = f.read()
    if request.method == 'POST':
        content = request.form['body']
        with open(filename, 'wb') as f:
            f.write(bytes(content, 'UTF-8'))

        return redirect('/blog2')

    return render_template('blog2/blog2_edit.html', post_text=post_text, filename=os.path.basename(filename).replace('.md', ''))

@app.route('/blog2/delete/<post>', methods=['GET', 'POST'])
def blog2_delete(post=None):
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'GET':
        filename = os.path.join(app.root_path, 'posts', '{}.md' .format(post))
        os.remove(filename)
        return redirect('/blog2')
    return redirect('/blog2')


@app.route('/blog2/new', methods=['GET', 'POST'])
def blog2_new():
    if not session.get('logged_in'):
        return 'access denied'
    if request.method == 'GET':
        date = datetime.today().strftime('%Y-%m-%d')
        upload = os.path.join(app.root_path, 'static', 'blog_images')
        list_img = []
        for subdir, dirs, files in os.walk(upload):
            for fn in files:
                subdir1 = subdir.split(os.path.sep)[-1]+'/'+fn
                list_img.append(subdir1)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['body']
        date = datetime.today().strftime('%Y-%m-%d')
        post = date+' '+title
        filename = os.path.join(app.root_path, 'posts', '{}.md' .format(post))
        with open(filename, 'wb') as f:
            f.write(bytes(content, 'UTF-8'))
        os.chmod(filename, 0o777)
        return redirect('/blog2')
    return render_template('blog2/blog2_new.html', list_img=list_img)

@app.route('/blog-upload', methods=['GET', 'POST'])
def upload_file_blog(date=None):
    date = datetime.today().strftime('%Y-%m-%d')
    upload = os.path.join(app.root_path, 'static', 'blog_images')
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        file = request.files['file']
        ident = uuid4().__str__()
        if file:
            filename = secure_filename(ident+'_'+file.filename)
            if not os.path.exists(os.path.join(upload, date)): 
                os.makedirs(os.path.join(upload, date))
            os.chmod(os.path.join(upload, date), 0o777)
            file.save(os.path.join(upload, date, filename))
            return redirect('/blog2/new')