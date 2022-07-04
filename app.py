from flask import Flask
import os
from flask import render_template
import json

app = Flask(__name__)

# edit config.json
app.config.from_file("config.json", load=json.load)


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
#from site_modules import tutorialspoint
#from site_modules import dbviewer
from site_modules import discogs
from site_modules import wp


if __name__ == "__main__":
    app.run()
