from flask import Flask
import os
from flask import render_template
import json
import time

app = Flask(__name__)

# edit config.json
app.config.from_file("config.json", load=json.load)

today_index = time.strftime('%Y/%m', time.gmtime(time.time()))

@app.context_processor
def inject_variables():
    return dict(today_index=today_index)

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
from site_modules import discogs
from site_modules import wp
from site_modules import newsgroups
from site_modules import gallery
from site_modules import schedule
from site_modules import paranormal

if __name__ == "__main__":
    app.run()
