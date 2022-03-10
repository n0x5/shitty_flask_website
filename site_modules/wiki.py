try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
from flask import request
import re
import requests

@app.route("/wiki/<search>")
def wiki_index(results=None, search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}'+'.db').format(search))
    sql = 'select title from {} where title like "%Category%" order by title' .format(search)
    results = [item for item in conn.execute(sql)]
    count = len(results)
    conn.close()
    return render_template('wiki/wiki_index.html', results=results, count=count, search=search)


@app.route("/wiki/<search2>/category/<search>")
def wiki_details(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}'+'.db').format(search2))
    sql = "select title, content from {} where content like ? order by title" .format(search2)
    results = [item for item in conn.execute(sql, ('%'+search+'%',))]
    count = len(results)
    conn.close()
    return render_template('wiki/wiki_details.html', results=results, count=count, search=search, search2=search2)


@app.route("/wiki/<search2>/article/<search>")
def wiki_article(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}'+'.db').format(search2))
    sql = "select content from {} where title like ?" .format(search2)
    results = [item for item in conn.execute(sql, (search,))]
    count = len(results)
    conn.close()
    final_string1 = '<title>'+search+'</title>'+'<h1>'+search+'</h1>'+'<pre style="word-wrap: break-word; white-space: pre-wrap;font-family:time;width:700px;">'+str(results[0][0])+'</pre>'
    final_string2 = re.sub(r'\[\[(.+?)\]\]', r'<a href="\1">\1</a>', final_string1)
    final_string3 = re.sub(r'\=\=\=\=(.+?)\=\=\=\=', r'<h4 style="display:inline;">\1</h4>', final_string2)
    final_string4 = re.sub(r'\=\=\=(.+?)\=\=\=', r'<h3 style="display:inline;">\1</h3>', final_string3)
    final_string5 = re.sub(r'\=\=(.+?)\=\=', r'<h2 style="display:inline;">\1</h2>', final_string4)
    final_string6 = re.sub(r"'''(.+?)'''", r'<b>\1</b>', final_string5)
    final_string7 = final_string6.replace('images/', 'https://temple.machinecode.org/{}_images/' .format(search2)).replace('{{cite}}', '').replace('{{Cite}}', '')
    final_string8 = re.sub(r"''(.+?)''", r'<b>\1</b>', final_string7)
    final_string9 = re.sub(r"\{\{dablink(.+?)\}\}", r'<b>\1</b><br>', final_string8)
    final_string10 = re.sub(r"\*(.+?)\n", r'<li>\1</li>', final_string9)
    final_string11 = re.sub(r'{{(.+?)}}', r'{{\1}}<hr>', final_string10)
    final_string = re.sub(r'<a href="(Category.+?)"', r'<a href="/wiki/{}/category/\1">\1</a>' .format(search2), final_string11)
    return final_string.replace('.html', '').replace('{{up}}<hr>', '')



@app.route("/wiki/<search2>/article2/<search>")
def wiki_article2(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}'+'.db').format(search2))
    sql = "select content from {} where title like ?" .format(search2)
    results = [item for item in conn.execute(sql, (search,))]
    count = len(results)
    conn.close()
    final_string1 = '<title>'+search+'</title>'+'<h1>'+search+'</h1>'+'<pre style="word-wrap: break-word; white-space: pre-wrap;font-family:time;">'+str(results[0][0])+'</pre>'
    final_string2 = re.sub(r'\[\[(.+?)\]\]', r'<a href="\1">\1</a>', final_string1)
    final_string3 = re.sub(r'\=\=\=\=(.+?)\=\=\=\=', r'<h4 style="display:inline;">\1</h4>', final_string2)
    final_string4 = re.sub(r'\=\=\=(.+?)\=\=\=', r'<h3 style="display:inline;">\1</h3>', final_string3)
    final_string5 = re.sub(r'\=\=(.+?)\=\=', r'<h2 style="display:inline;">\1</h2>', final_string4)
    final_string6 = re.sub(r"'''(.+?)'''", r'<b>\1</b>', final_string5)
    #final_string7 = final_string6.replace('images/', '/static/{}_images/' .format(search2)).replace('{{cite}}', '').replace('{{Cite}}', '')
    final_string7 = final_string6.replace('images/', 'https://temple.machinecode.org/{}_images/' .format(search2)).replace('{{cite}}', '').replace('{{Cite}}', '')
    final_string8 = re.sub(r"''(.+?)''", r'<b>\1</b>', final_string7)
    final_string9 = re.sub(r"\{\{dablink(.+?)\}\}", r'<b>\1</b><br>', final_string8)
    final_string10 = re.sub(r"\*(.+?)\n", r'<li>\1</li>', final_string9)
    final_string11 = re.sub(r'{{(.+?)}}', r'{{\1}}<hr>', final_string10)
    final_string = re.sub(r'<a href="(Category.+?)"', r'<a href="/wiki/{}/category/\1">\1</a>' .format(search2), final_string11)
    try:
        imgsearch = re.findall(r'src="\/static\/\w+\/(.+?)"', str(final_string))
        lst = []
        for item_img in imgsearch:
            conn2 = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}_images.db').format(search2))
            sql2 = "select url, filename from {}_images where filename like ?" .format(search2)
            results2 = [item for item in conn2.execute(sql2, (item_img,))]
            file_url = results2[0][0]
            filename1 = results2[0][1]
            lst.append([item_img, filename1, file_url])
            endpoint = os.path.join(app.root_path, 'static', '{}_images', filename1) .format(search2)
            endpoint2 = os.path.join(app.root_path, 'static', '{}_images') .format(search2)
            if not os.path.exists(endpoint2):
                os.makedirs(endpoint2)
            if not os.path.exists(endpoint):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
                r = requests.get(file_url, headers=headers)
                with open(endpoint, 'wb') as cover_jpg:
                    cover_jpg.write(r.content)


        return final_string.replace('.html', '').replace('{{up}}<hr>', '')

    except Exception:
        return final_string.replace('.html', '').replace('{{up}}<hr>', '')


@app.route("/wiki/<search2>/search", methods=['GET', 'POST'])
def wiki_search(search=None, search2=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', '{}'+'.db').format(search2))
    search = request.form['search']
    sql = "select title, substr(content, instr(lower(content), '{}')-20, 75) from {} where content like ? order by title" .format(search.lower(), search2)
    results = [item for item in conn.execute(sql, ('%'+search+'%',))]
    count = len(results)
    conn.close()
    return render_template('wiki/wiki_search.html', results=results, count=count, search=search, search2=search2)