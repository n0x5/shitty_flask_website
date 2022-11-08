try:
    from __main__ import app
except:
    from app import app
import calendar
from flask import render_template
import os
import time



@app.route('/calendar')
def calendar_index(results=None):
    text_cal = calendar.TextCalendar(firstweekday=0)
    results = text_cal.formatyear(2022)
    return render_template('schedule/schedule_index.html', results=results)

@app.route('/calendar/<year>/<month>')
def calendar_month(results=None, year=None, month=None):
    text_cal = calendar.TextCalendar(firstweekday=0)
    results = text_cal.formatmonth(int(year), int(month))
    today = time.strftime('%d', time.gmtime(time.time())).replace('0', '')
    return render_template('schedule/schedule_month.html', results=results.replace(' '+today+' ', '<div class="today">'+today+'</div>'))

@app.route('/calendar/<year>')
def calendar_year(results=None, year=None, month=None):
    text_cal = calendar.TextCalendar(firstweekday=0)
    results = text_cal.formatyear(int(year))
    today = time.strftime('%Y', time.gmtime(time.time())).replace('0', '')
    return render_template('schedule/schedule_index.html', results=results.replace(' '+today+' ', '<div class="today">'+today+'</div>'))

