from flask import Flask
import os
from flask import render_template
from config import _configs
import time

app = Flask(__name__)

# edit configs/configs-sample.py and rename to config/configs.py
app.config.update(_configs.conf)


today_index = time.strftime('%Y/%m', time.gmtime(time.time()))

@app.context_processor
def inject_variables():
    return dict(today_index=today_index)


@app.template_filter()
def flm_image(results):
    imdb = results[0]
    image_dir = os.path.join(app.root_path, 'static', 'flm_images', imdb)
    list_img = []
    for subdir, dirs, files in os.walk(image_dir):
        for fn in files:
            list_img.append('<a href="/static/flm_images/{}/{}"><img width="150" src="/static/flm_images/{}/{}" /></a> '.format(imdb, fn, imdb, fn))
    return ''.join(list_img)


######## INDEX PAGE

@app.route("/")
def hello():
    return render_template('index.html')


# Main sections of site

from site_modules import admin
from site_modules import movies
from site_modules import tv
from site_modules import games
from site_modules import flm
from site_modules import blog2
from site_modules import wiki
from site_modules import tutorialspoint
from site_modules import dbviewer
from site_modules import discogs
from site_modules import wp
from site_modules import gallery
from site_modules import newsgroups
from site_modules import schedule

if __name__ == "__main__":
    app.run()
