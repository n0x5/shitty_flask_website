try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
from flask import request
from flask import session
from flask import redirect
import markdown
import sqlite3
import re

# pip install Pygments for code highlighting, rest is automatic

@app.route('/blog2')
def blog2_index():
    for root, dirs, files in os.walk(os.path.join(app.root_path, 'posts')):
        results3 = [os.path.join(root, post1) for post1 in files]
        results3.sort(key=os.path.getctime, reverse=True)
        results2 = [os.path.basename(fn).replace('.md', '') for fn in results3]

    #conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'wp-posts.db'))
    #sql = 'select post_title, post_content, post_date from wp_posts where (post_status = "publish" and post_type = "post") order by post_date desc'
    #results = [item for item in conn.execute(sql)]

    return render_template('blog2/blog2_index.html', results2=results2)

@app.route('/blog2/<post>')
def blog2_post(post=None):
    filename = os.path.join(app.root_path, 'posts', '{}.md' .format(post))
    extension_list = ['codehilite', 'fenced_code', 'extra', 'meta', 'sane_lists', 'toc', 'wikilinks']
    with open(filename, 'r') as f:
        your_text_string = f.read()
        html = markdown.markdown(your_text_string, extensions=extension_list)

    return render_template('blog2/blog2_post.html', html=html)

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

