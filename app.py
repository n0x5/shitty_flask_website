#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    import sys
    reload(sys)  
    sys.setdefaultencoding('utf8')
except:
    pass

from flask import Flask
import os
from flask import render_template

import configs

app = Flask(__name__)
#app.debug = True
app.config.update(configs.conf) # edit configs-sample.py and rename to configs.py


@app.route("/")
def hello(tpath=None):
    image = 'hey there guy'
    tpath = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
    return render_template('index.html', tpath=tpath)



# sections of site

import admin
import movies
import tv
import games
import flm
import blog2
import wiki


if __name__ == "__main__":
    app.run()
