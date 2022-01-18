try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
import yaml

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
        results2 = [os.path.basename(post1).split('.')[0] for post1 in results3]
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