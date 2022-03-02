try:
    from __main__ import app
except:
    from app import app
from flask import session
from flask import request
from flask import render_template
from flask import current_app
from flask import flash
from flask import redirect
from flask import url_for
import sqlite3
import os

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

        connection2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
        cursor2 = connection2.cursor()
        sql2 = 'select * from (select * from movies order by dated desc limit 20) order by dated desc'
        cursor2.execute(sql2)
        results2 = [(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]) for item in cursor2.fetchall()]
        cursor2.close()

    return render_template('dashboard.html', results=results, results2=results2)