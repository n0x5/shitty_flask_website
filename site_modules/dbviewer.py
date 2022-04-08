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


@app.route('/dbviewer')
def dbview_index():
    lst = []
    for root, dirs, files in os.walk(os.path.join(app.root_path, 'databases')):
        db_file_path = [os.path.join(root, db_file) for db_file in files]
        lst.append([db_file_path,])
        for fn in db_file_path:
            #lst.append([db_file_path, results2])
            conn = sqlite3.connect(fn)
            sql = "select name from sqlite_schema where type ='table' AND name NOT LIKE 'sqlite_%'"
            results2 = [item[0] for item in conn.execute(sql)]
            lst.append([results2])

    #return str(db_file_path)
    return render_template('blog2/blog2_index.html', results2=lst)
