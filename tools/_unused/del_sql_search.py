import re
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import calendar
import sqlite3
from PIL import Image
import pyexiv2

#from gi.repository import GExiv2

cwd = r'/path/to/folder'

conn = sqlite3.connect('imagesnew3111.db')
cur = conn.cursor()
#cur.execute('''CREATE TABLE images
#             (file text, fullpath text unique, subfolder text, sizewidth int, sizeheight int, ftime int, exifd text, dated datetime DEFAULT CURRENT_TIMESTAMP)''')

cur.execute('delete from images where fullpath like "%2018_47_May%"')
cur.connection.commit()

