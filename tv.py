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

@app.route("/tv")
def tvindex(results=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'tv.db'))
    sql = 'select imdb_id, show_title, count(imdb_id) c from tv group by show_title having c > 0 order by show_title'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('tvindex.html', results=results, count=count)

@app.route("/tv/<search>")
def tvdetails(search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'tv.db'))
    sql = "select show_title, episode_title, air_date, episode_summary, season_number, episode_number, imdb_id from tv where imdb_id like ? order by imdb_id, season_number"
    results = [item for item in conn.execute(sql, ('%'+search+'%',))]
    count = len(results)
    conn.close()
    return render_template('tvdetails.html', results=results, count=count)


@app.route("/wiki/<search>")
def wiki_index(results=None, search=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', '{}'+'.db').format(search))
    sql = 'select title from {} where title like "%Category%" order by title' .format(search)
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('wiki_index.html', results=results, count=count, search=search)


@app.route("/wiki/<search2>/category/<search>")
def wiki_details(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', '{}'+'.db').format(search2))
    sql = "select title, content from {} where content like ? order by title" .format(search2)
    results = [item for item in conn.execute(sql, ('%'+search+'%',))]
    count = len(results)
    conn.close()
    return render_template('wiki_details.html', results=results, count=count, search=search, search2=search2)

@app.route("/wiki/<search2>/article/<search>")
def wiki_article(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', '{}'+'.db').format(search2))
    sql = "select content from {} where title like ?" .format(search2)
    results = [item for item in conn.execute(sql, (search,))]
    count = len(results)
    conn.close()
    final_string1 = '<title>'+search+'</title>'+'<pre style="word-wrap: break-word; white-space: pre-wrap;">'+str(results[0][0])+'</pre>'
    final_string2 = re.sub(r'\[\[(.+?)\]\]', r'<a href="\1">\1</a>', final_string1)
    final_string3 = re.sub(r'\=\=\=\=(.+?)\=\=\=\=', r'<h4 style="display:inline;">\1</h4>', final_string2)
    final_string4 = re.sub(r'\=\=\=(.+?)\=\=\=', r'<h3 style="display:inline;">\1</h3>', final_string3)
    final_string5 = re.sub(r'\=\=(.+?)\=\=', r'<h2 style="display:inline;">\1</h2>', final_string4)
    final_string6 = re.sub(r"'''(.+?)'''", r'<b>\1</b>', final_string5)
    final_string7 = final_string6.replace('images/', '/static/{}_images/' .format(search2)).replace('{{cite}}', '').replace('{{Cite}}', '')
    final_string8 = re.sub(r"''(.+?)''", r'<b>\1</b>', final_string7)
    final_string9 = re.sub(r"\{\{dablink(.+?)\}\}", r'<b>\1</b><br>', final_string8)
    final_string10 = re.sub(r"\*(.+?)\n", r'<li>\1</li>', final_string9)
    final_string11 = re.sub(r'{{(.+?)}}', r'{{\1}}<hr>', final_string10)
    final_string = re.sub(r'<a href="(Category.+?)"', r'<a href="/wiki/{}/category/\1">\1</a>' .format(search2), final_string11)
    try:
        imgsearch = re.findall(r'src="\/static\/\w+\/(.+?)"', str(final_string))
        for item_img in imgsearch:
            endpoint_check = os.path.join(os.path.dirname(__file__), 'static', '{}_images', item_img) .format(search2)
            item_img = imgsearch.group(1)
            endpoint_check = os.path.join(os.path.dirname(__file__), 'static', '{}_images', item_img) .format(search2)
            conn2 = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', '{}_images.db').format(search2))
            sql2 = "select url, filename from {}_images where filename like ?" .format(search2)
            results2 = [item for item in conn2.execute(sql2, (item_img,))]
            file_url = results2[0][0]
            filename1 = results2[0][1]
            endpoint = os.path.join(os.path.dirname(__file__), 'static', '{}_images', filename1) .format(search2)
            endpoint2 = os.path.join(os.path.dirname(__file__), 'static', '{}_images') .format(search2)
            if not os.path.exists(endpoint2):
                os.makedirs(endpoint2)
            if not os.path.exists(endpoint):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
                r = requests.get(file_url, headers=headers)
                with open(endpoint, 'wb') as cover_jpg:
                    cover_jpg.write(r.content)
            if not os.path.exists(os.path.join(item_img, item_img)):
                item_img_img = str(item_img).replace('_', ' ')
                final_string_img_3 = re.sub(r'{}_images\/.+?"' .format(search2), r'{}_images\/{}"' .format(search2, item_img_img), final_string)
                return final_string_img_3.replace('.html', '').replace('{{up}}<hr>', '').replace('250px', '550px')

            else:
                return final_string.replace('.html', '').replace('{{up}}<hr>', '').replace('250px', '550px')

    except Exception:
        return final_string.replace('.html', '').replace('{{up}}<hr>', '').replace('250px', '550px')

