try:
    from __main__ import app
except:
    from app import app
from flask import render_template
import sqlite3
import os
from flask import request
from flask import flash

###################### GAMES #########################


@app.route("/discogs")
def discogs_index():
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs3.db'))
    sql = "select label_name, count(distinct(release_id)) c from releases where genres like '%screen%' and label_name not like 'Not On Label' \
         and (label_name not like 'maverick' and label_name not like '%universal%' and label_name not like 'jive' \
        and label_name not like '%TVT Records%' and label_name not like '%roadrunner%' and label_name not like '%Hollywood Records%' \
        and label_name not like '%reprise%' and label_name not like '%Arista%' and label_name not like '%Immortal Records%' and label_name not like 'American Recordings' \
        and label_name not like '%Wind-Up%' and label_name not like 'RCA' and label_name not like '%Wind-Up%' and label_name not like 'Mercury' \
        and label_name not like 'Elektra' and label_name not like 'Virgin%' and label_name not like 'Capitol Records' and label_name not like 'Sony%' \
        and label_name not like 'Rise%' and label_name not like 'columbia' and label_name not like 'Century Media' and label_name not like 'BMG%' \
        and label_name not like 'EMI' and label_name not like 'island records' and label_name not like 'warner%' and label_name not like 'interscope%' \
        and label_name not like 'geffen%' and label_name not like 'Another Century' and label_name not like 'atlantic' and label_name not like 'Lakeshore' \
        and label_name not like 'disney' and label_name not like 'dreamworks%' \
        and label_name not like 'American Recordings' and \
        label_name not like 'Caroline Records' and label_name not like 'epic' and label_name not like 'london records' \
        and label_name not like 'MCA Records' and label_name not like 'Polydor' and label_name not like 'Republic Records' \
        and label_name not like 'Rhino Records (2)' and label_name not like 'sire' and label_name not like 'vagrant records' \
        and label_name not like 'Volcano (2)' and label_name not like 'Zoo Entertainment' and label_name not like 'Tool Dissectional' \
        and label_name not like 'A&amp;M Records' and label_name not like 'Astralwerks' and label_name not like 'Naxos' \
        and label_name not like 'Deutsche Grammophon' and label_name not like 'Decca' and label_name not like '%Sarabande' \
        and label_name not like 'ECM Records' and label_name not like 'Ariola' and label_name not like 'Walt Disney Records' \
        and label_name not like 'Milan' and label_name not like 'Def Jam Recordings' \
        and label_name not like 'Parlophone' and label_name not like 'Mute' and label_name not like 'WaterTower Music' \
        ) group by label_name having c > 10 order by c desc"
    groups = [item for item in conn.execute(sql)]

    return render_template('discogs/discogs_index.html', groups=groups)

@app.route("/discogs/search/<genre>/<country>/<label>")
def discogs_search_cogenre(genre=None, country=None, label=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs-releases-new4.db'))
    sql = "select released, label_name, title, track_p from releases where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and country like ? and label_name like ? order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country, label))]

    return render_template('discogs/discogs_search.html', results=results)

@app.route("/discogs/search/<genre>/<country>")
def discogs_search_cogenre_2(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs2.db'))
    sql = "select min(releases.released), releases.label_name, releases.title,  \
    releases.genres, releases.styles, format_name, track_p, artist_name from releases where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and released not like 'None' and track_p not like 'None' and country like ? and format_name like 'CD' group by master_id order by releases.label_name, released asc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)

@app.route("/discogs/search_subgenre_major/<genre>/<country>")
def discogs_search_cogenre_3(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs3.db'))
    sql = "select min(releases.released), releases.label_name, releases.title,  \
    releases.genres, releases.styles, format_name, track_p, artist_name, master_id from releases where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and released not like 'None' \
         and country like ? and format_name like 'CD' and (label_name like 'maverick' or label_name like 'Universal%' or label_name like 'jive' \
        or label_name like '%TVT Records%' or label_name like '%roadrunner%' or label_name like '%Hollywood Records%' \
        or label_name like '%reprise%' or label_name like '%Arista%' or label_name like '%Immortal Records%' or label_name like 'American Recordings' \
        or label_name like '%Wind-Up%' or label_name like 'RCA' or label_name like '%Wind-Up%' or label_name like 'Mercury' \
        or label_name like 'Elektra' or label_name like 'Virgin%' or label_name like 'Capitol Records' or label_name like 'Sony%' \
        or label_name like 'Rise Records (3)' or label_name like 'columbia' or label_name like 'Century Media' or label_name like 'BMG%' \
        or label_name like 'EMI' or label_name like 'island records' or label_name like 'warner%' or label_name like 'interscope%' \
        or label_name like 'geffen%' or label_name like 'Another Century' or label_name like 'atlantic' or label_name like 'Lakeshore' \
        or label_name like 'disney' or label_name like 'dreamworks%' or label_name like 'American Recordings' or \
        label_name like 'Caroline Records' or label_name like 'epic' or label_name like 'london records' \
        or label_name like 'MCA Records' or label_name like 'Polydor' or label_name like 'Republic Records' \
        or label_name like 'Rhino Records (2)' or label_name like 'sire' or label_name like 'vagrant records' \
        or label_name like 'Volcano (2)' or label_name like 'Zoo Entertainment' or label_name like 'Tool Dissectional' \
        or label_name like 'A&amp;M Records' or label_name like 'Astralwerks' or label_name like 'Naxos' \
        or label_name like 'Deutsche Grammophon' or label_name like 'Decca' or label_name like 'Var&#232;se Sarabande%' \
        or label_name like 'ECM Records' or label_name like 'Ariola' or label_name like 'Walt Disney Records' \
        or label_name like 'Milan' or label_name like 'Def Jam Recordings'  \
        or label_name like 'Parlophone' or label_name like 'Mute' or label_name like 'WaterTower Music' \
            ) group by master_id order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)

@app.route("/discogs/search_subgenre_indie/<genre>/<country>")
def discogs_search_cogenre_8(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs3.db'))
    sql = "select min(releases.released), releases.label_name, releases.title,  \
    releases.genres, releases.styles, format_name, track_p, artist_name, master_id from releases where styles like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and released not like 'None' \
         and country like ? and format_name like 'CD' and (label_name not like 'maverick' and label_name not like 'Universal%' and label_name not like 'jive' \
        and label_name not like '%TVT Records%' and label_name not like '%roadrunner%' and label_name not like '%Hollywood Records%' \
        and label_name not like '%reprise%' and label_name not like '%Arista%' and label_name not like '%Immortal Records%' and label_name not like 'American Recordings' \
        and label_name not like '%Wind-Up%' and label_name not like 'RCA' and label_name not like '%Wind-Up%' and label_name not like 'Mercury' \
        and label_name not like 'Elektra' and label_name not like 'Virgin%' and label_name not like 'Capitol Records' and label_name not like 'Sony%' \
        and label_name not like 'Rise%' and label_name not like 'columbia' and label_name not like 'Century Media' and label_name not like 'BMG%' \
        and label_name not like 'EMI' and label_name not like 'island records' and label_name not like 'warner%' and label_name not like 'interscope%' \
        and label_name not like 'geffen%' and label_name not like 'Another Century' and label_name not like 'atlantic' and label_name not like 'Lakeshore' \
        and label_name not like 'disney' and label_name not like 'dreamworks%' \
        and label_name not like 'American Recordings' and \
        label_name not like 'Caroline Records' and label_name not like 'epic' and label_name not like 'london records' \
        and label_name not like 'MCA Records' and label_name not like 'Polydor' and label_name not like 'Republic Records' \
        and label_name not like 'Rhino Records (2)' and label_name not like 'sire' and label_name not like 'vagrant records' \
        and label_name not like 'Volcano (2)' and label_name not like 'Zoo Entertainment' and label_name not like 'Tool Dissectional' \
        and label_name not like 'A&amp;M Records' and label_name not like 'Astralwerks' and label_name not like 'Naxos' \
        and label_name not like 'Deutsche Grammophon' and label_name not like 'Decca' and label_name not like '%Sarabande%' \
        and label_name not like 'ECM Records' and label_name not like 'Ariola' and label_name not like 'Walt Disney Records' \
        and label_name not like 'Milan' and label_name not like 'Def Jam Recordings' \
        and label_name not like 'Parlophone' and label_name not like 'Mute' and label_name not like 'WaterTower Music' \
        ) group by master_id order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)

@app.route("/discogs/search_genre_indie/<genre>/<country>")
def discogs_search_cogenre_4(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs3.db'))
    sql = "select min(releases.released), releases.label_name, releases.title,  \
    releases.genres, releases.styles, format_name, track_p, artist_name, master_id from releases where genres like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and released not like 'None' and track_p not like 'None' \
         and country like ? and format_name like 'CD' and (label_name not like 'maverick' and label_name not like '%universal%' and label_name not like 'jive' \
        and label_name not like '%TVT Records%' and label_name not like '%roadrunner%' and label_name not like '%Hollywood Records%' \
        and label_name not like '%reprise%' and label_name not like '%Arista%' and label_name not like '%Immortal Records%' and label_name not like 'American Recordings' \
        and label_name not like '%Wind-Up%' and label_name not like 'RCA' and label_name not like '%Wind-Up%' and label_name not like 'Mercury' \
        and label_name not like 'Elektra' and label_name not like 'Virgin%' and label_name not like 'Capitol Records' and label_name not like 'Sony%' \
        and label_name not like 'Rise%' and label_name not like 'columbia' and label_name not like 'Century Media' and label_name not like 'BMG%' \
        and label_name not like 'EMI' and label_name not like 'island records' and label_name not like 'warner%' and label_name not like 'interscope%' \
        and label_name not like 'geffen%' and label_name not like 'Another Century' and label_name not like 'atlantic' and label_name not like 'Lakeshore' \
        and label_name not like 'disney' and label_name not like 'dreamworks%' \
        and label_name not like 'American Recordings' and \
        label_name not like 'Caroline Records' and label_name not like 'epic' and label_name not like 'london records' \
        and label_name not like 'MCA Records' and label_name not like 'Polydor' and label_name not like 'Republic Records' \
        and label_name not like 'Rhino Records (2)' and label_name not like 'sire' and label_name not like 'vagrant records' \
        and label_name not like 'Volcano (2)' and label_name not like 'Zoo Entertainment' and label_name not like 'Tool Dissectional' \
        and label_name not like 'A&amp;M Records' and label_name not like 'Astralwerks' and label_name not like 'Naxos' \
        and label_name not like 'Deutsche Grammophon' and label_name not like 'Decca' and label_name not like '%Sarabande%' \
        and label_name not like 'ECM Records' and label_name not like 'Ariola' and label_name not like 'Walt Disney Records' \
        and label_name not like 'Milan' and label_name not like 'Def Jam Recordings' \
        and label_name not like 'Parlophone' and label_name not like 'Mute' and label_name not like 'WaterTower Music' \
        ) group by master_id order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)

@app.route("/discogs/search_genre_major/<genre>/<country>")
def discogs_search_cogenre_5(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs3.db'))
    sql = "select min(releases.released), releases.label_name, releases.title,  \
    releases.genres, releases.styles, format_name, track_p, artist_name, master_id from releases where genres like ? and label_name not like \
 'Not On Label' and label_name not like '%Self-released%' and released not like 'None' \
         and country like ? and format_name like 'CD' and (label_name like 'maverick' or label_name like '%universal%' or label_name like 'jive' \
        or label_name like '%TVT Records%' or label_name like '%roadrunner%' or label_name like '%Hollywood Records%' \
        or label_name like '%reprise%' or label_name like '%Arista%' or label_name like '%Immortal Records%' or label_name like 'American Recordings' \
        or label_name like '%Wind-Up%' or label_name like 'RCA' or label_name like '%Wind-Up%' or label_name like 'Mercury' \
        or label_name like 'Elektra' or label_name like 'Virgin%' or label_name like 'Capitol Records' or label_name like 'Sony%' \
        or label_name like 'Rise Records (3)' or label_name like 'columbia' or label_name like 'Century Media' or label_name like 'BMG%' \
        or label_name like 'EMI' or label_name like 'island records' or label_name like 'warner%' or label_name like 'interscope%' \
        or label_name like 'geffen%' or label_name like 'Another Century' or label_name like 'atlantic' or label_name like 'Lakeshore' \
        or label_name like 'disney' or label_name like 'dreamworks%' or label_name like 'American Recordings' or \
        label_name like 'Caroline Records' or label_name like 'epic' or label_name like 'london records' \
        or label_name like 'MCA Records' or label_name like 'Polydor' or label_name like 'Republic Records' \
        or label_name like 'Rhino Records (2)' or label_name like 'sire' or label_name like 'vagrant records' \
        or label_name like 'Volcano (2)' or label_name like 'Zoo Entertainment' or label_name like 'Tool Dissectional' \
        or label_name like 'A&amp;M Records' or label_name like 'Astralwerks' or label_name like 'Naxos' \
        or label_name like 'Deutsche Grammophon' or label_name like 'Decca' or label_name like '%Sarabande%' \
        or label_name like 'ECM Records' or label_name like 'Ariola' or label_name like 'Walt Disney Records' \
        or label_name like 'Milan' or label_name like 'Def Jam Recordings' \
        or label_name like 'Parlophone' or label_name like 'Mute' or label_name like 'WaterTower Music' \
        ) group by master_id order by released desc"
    results = [item for item in conn.execute(sql, ('%'+genre+'%', country))]
    count = len(results)
    return render_template('discogs/discogs_search_genre.html', results=results, count=count)


@app.route("/discogs/search_dvd")
def discogs_search_cogenre_dvd(genre=None, country=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'discogs_us_dvd.db'))
    sql = "select * from discogs_us order by artist_name asc"
    results = [item for item in conn.execute(sql,)]
    count = len(results)
    return render_template('discogs/discogs_search_dvd.html', results=results, count=count)