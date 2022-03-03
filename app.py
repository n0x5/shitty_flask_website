from flask import Flask
import os
from flask import render_template
from config import _configs

app = Flask(__name__)

# edit configs/configs-sample.py and rename to config/configs.py
app.config.update(_configs.conf)


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


if __name__ == "__main__":
    app.run()
