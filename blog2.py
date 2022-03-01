try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
import markdown

# pip install Pygments for code highlighting, rest is automatic

@app.route('/blog2')
def blog2_index():
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'posts')):
        results3 = [os.path.join(root, post1) for post1 in files]
        results3.sort(key=os.path.getmtime, reverse=True)
        results2 = [os.path.basename(fn).replace('.md', '') for fn in results3]

    return render_template('blog2index.html', results2=results2)

@app.route('/blog2/<post>')
def blog2_post(post=None):
    filename = os.path.join(os.path.dirname(__file__), 'posts', '{}.md' .format(post))
    with open(filename, 'r', encoding='utf8') as f:
        your_text_string = f.read()
        html = markdown.markdown(your_text_string, extensions=['codehilite', 'fenced_code'])

    return render_template('blog2post.html', html=html)