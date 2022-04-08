try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
from flask import flash
import re
import requests

@app.route("/wp")
def wp_index(results=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'wp-posts.db'))
    sql = 'select * from wp_posts where (post_status = "publish" and post_type = "post") order by post_date desc'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('wp/wp_index.html', results=results, count=count)
