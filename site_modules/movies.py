try:
    from __main__ import app
except:
    from app import app
import sqlite3
import os
from flask import render_template
from flask import flash
import re

@app.route("/movies")
def movieindex(genres=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = 'select release from movies'
    results = [item for item in conn.execute(sql)]
    count = len(results)
    genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
    genres = [item.title() for item in genrelist]
    conn.close()
    return render_template('movies/movieindex.html', genres=genres, count=count)

@app.route("/movies/<search>")
def moviesearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, dated from \
            movies where (genre like ? or infogenres like ? or release like ? or director like ? \
            or mainactors like ? or inforest like ? or imdb like ?) order by year desc, dated desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in \
    conn.execute(sql, ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/cast/<search>")
def castsearch(search=None):
    conn1 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql1 = "select release, director, imdb, infogenres, year, dated from \
            movies where mainactors like ? order by year desc, dated desc"

    results1 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
    conn1.execute(sql1, ('%'+search+'%',))]
    conn1.close()

    conn2 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql2 = "select release, director, imdb, infogenres, year, dated from \
            movies where (inforest like ? and mainactors not like ?) order by year desc, dated desc"

    results2 = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                    item[3].replace('[', '').replace(']', '').replace("\'", ""), item[4]) for item in \
    conn2.execute(sql2, ('%'+search+'%', '%'+search+'%'))]
    conn2.close()
    gcounts2 = len(results2)+len(results1)
    return render_template('movies/moviecast.html', results=results1, search=search, gcounts=gcounts2, results2=results2)

@app.route("/movies/genrewide/<search>")
def genrewidesearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year, \
        boxoffice.rlid, boxoffice.wide_theatersopen from movies join boxoffice on movies.imdb = boxoffice.imdbid where (movies.genre like ? or movies.infogenres like ?) \
        and wide_theatersopen > 2000 and boxoffice.wide_theatersopen != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
    conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genreltd/<search>")
def genreltdsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year, \
        boxoffice.rlid, boxoffice.alt_theaters from movies join boxoffice on movies.imdb = boxoffice.imdbid where (movies.genre like ? or movies.infogenres like ?) \
        and boxoffice.alt_theaters < 2000 and boxoffice.alt_theaters != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/genrevideo/<search>")
def genrevideosearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year \
        from movies where imdb not in (select imdbid from boxoffice) and (genre like ? or infogenres like ?) group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/yearwide/<search>")
def yearwidesearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year, \
        boxoffice.rlid, boxoffice.wide_theatersopen from movies join boxoffice on movies.imdb = boxoffice.imdbid where movies.year like ? \
        and wide_theatersopen > 2000 and boxoffice.wide_theatersopen != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
    conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/yearltd/<search>")
def yearltdsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year, \
        boxoffice.rlid, boxoffice.alt_theaters from movies join boxoffice on movies.imdb = boxoffice.imdbid where movies.year like ? \
        and boxoffice.alt_theaters < 2000 and boxoffice.alt_theaters != 'None' group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], item[5], item[6]) for item in \
             conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/yearvideo/<search>")
def yearvideosearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select movies.release, movies.director, movies.imdb, movies.infogenres, movies.year \
        from movies where imdb not in (select imdbid from boxoffice) and movies.year like ? group by movies.release order by year desc"

    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies7.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/genre/<search>")
def genresearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, dated from movies \
            where (genre like ? or infogenres like ?) order by year desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
             conn.execute(sql, ('%'+search+'%', '%'+search+'%'))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies2.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/groups")
def grouplist(groups=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select grp, count(*) c from movies group by grp having c > 0 order by c desc"
    groups = [(item[0], item[1]) for item in conn.execute(sql)]
    conn.close()
    gcounts = len(groups)
    return render_template('movies/moviegroups.html', groups=groups)


@app.route("/movies/group/<search>")
def groupsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, dated \
            from movies where grp like ? order by year desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies2.html', results=results, search=search, gcounts=gcounts)


@app.route("/movies/director")
def director(groups=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select director, count(distinct(imdb)) c from movies group by director having c > 0 order by c desc"
    groups = [(item[0].strip().replace('\\n', '').replace(',', ''), item[1]) for item in \
                 conn.execute(sql)]
    conn.close()
    gcounts = len(groups)
    return render_template('movies/moviedirector.html', groups=groups)


@app.route("/movies/director/<search>")
def directorsearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, title, dated from movies \
            where director like ? order by year desc, dated desc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/years")
def movieyears(groups=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select distinct(year), count(distinct(imdb)) c from movies group by year having c > 0 order by c desc"
    years = [(item[0], item[1]) for item in conn.execute(sql)]
    conn.close()
    return render_template('movies/movieyears.html', years=years)


@app.route("/movies/years/<search>")
def movieyearssearch(search=None):
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = "select release, director, imdb, infogenres, year, title from movies where year like ? \
            order by year, release asc"
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), os.path.basename(item[2]+'.jpg'), 
            item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4]) for item in \
                 conn.execute(sql, ('%'+search+'%',))]
    conn.close()
    gcounts = len(results)
    return render_template('movies/movies2.html', results=results, search=search, gcounts=gcounts)

@app.route("/movies/boxgenres")
def moviesbox1():
    conn = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    sql = 'select distinct(genre) from movie_genres'
    results = [(item[0],) for item in conn.execute(sql)]
    conn.close()

    return render_template('movies/movies-boxgenres.html', results=results)

@app.route("/movies/company")
def companylist():
    connection2 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'imdb_scrape_database2.db'))
    cursor2 = connection2.cursor()
    sql = 'select company, title, count(distinct(imdbid)) c from companies group by company having c > 0 order by c desc'
    cursor2.execute(sql)
    companies = [(item[0], item[1], item[2]) for item in cursor2.fetchall()]
    cursor2.close()

    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    cursor = connection.cursor()
    sql2 = 'select company, count(distinct(imdbid)) c from companyinfo join movies on movies.imdb = "tt" || companyinfo.imdbid group by company having c > 10 order by c desc'
    cursor.execute(sql2)
    companies2 = [(item[0], item[1]) for item in cursor.fetchall()]

    sql3 = 'select alt_distributor, count(distinct(imdbid)) c from boxoffice join movies on movies.imdb = boxoffice.imdbid group by alt_distributor having c > 0 order by c desc;'
    cursor.execute(sql3)
    companies3 = [(item[0], item[1]) for item in cursor.fetchall()]

    cursor.close()
    return render_template('movies/company_list_all.html', companies=companies, companies2=companies2, companies3=companies3)


@app.route("/movies/company/all/<studio>")
def companylist2(studio=None):
    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'imdb_scrape_database2.db'))
    cursor = connection.cursor()
    cursor.execute('select company, imdbid, title, year, role from companies where company like ? order by year desc, title desc', ('%'+studio+'%',))
    companies = [(item[0], item[1], item[2], item[3], item[4]) for item in cursor.fetchall()]
    count = len(companies)
    cursor.close()
    return render_template('movies/company_list.html', companies=companies, count=count, studio=studio)

@app.route("/movies/company/<studio>")
def companylist3(studio=None):
    film_list = []
    genres_list = []
    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select movies.release, movies.year, movies.imdb, movies.infogenres from companyinfo join movies on movies.imdb = "tt" || companyinfo.imdbid where companyinfo.company like ? group by movies.release order by movies.year desc', ('%'+studio+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    count = len(results)
    cursor.close()
    return render_template('movies/company_list2.html', results=results, count=count, studio=studio)

@app.route("/movies/company/theatrical/<studio>")
def companylist3theatrical(studio=None):
    film_list = []
    genres_list = []
    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select movies.release, movies.year, movies.imdb, movies.infogenres from boxoffice join movies on movies.imdb = boxoffice.imdbid where boxoffice.alt_distributor like ? group by movies.release order by movies.year desc', ('%'+studio+'%',))
    results = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
    count = len(results)
    cursor.close()
    return render_template('movies/company_list2.html', results=results, count=count, studio=studio)

@app.route("/movies/release/<release>")
def movierelease(release=None):
    colist = []
    connection = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute('select release, grp, genre, format, imdb, title, director, mainactors, infogenres, inforest, \
        infosummary, year, imdb from movies where release like ?', ('%'+release+'%',))

    results = [(item[0], item[1], item[2], item[3], os.path.basename(item[4]+'.jpg'), item[5], item[6].strip(' ').replace('\\n', '').replace(',', ''), 
            item[7].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[8].replace('[', '').replace(']', '').replace('\'', '').split(','), item[9].replace('[', '').replace(']', '').replace('\'', '').split(','), 
            item[10], item[11], item[12]) for item in cursor.fetchall()]
    remaining_cast = (item.strip() for item in results[0][9])
    main_cast = (item.strip() for item in results[0][7])
    genres_list = (item.strip() for item in results[0][8])
    imdborig = re.search(r'\d{7}', str(results[0][4]))
    imdbidor = imdborig.group(0)
    imdbor2 = 'tt'+imdbidor
    rls = str(results[0][0])

    connection2 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'imdb_scrape_database2.db'))
    connection3 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'movie-genres.db'))
    connection7 = sqlite3.connect(os.path.join(app.root_path, 'databases', 'moviesdb-divx.db'))
    cursor3 = connection3.cursor()
    cursor2 = connection2.cursor()
    cursor7 = connection7.cursor()
    cursor7.execute('select rel_time_readable, release from db_movies where release like ?', ('%'+rls+'%',))
    cursor2.execute('select company, imdbid from companies where imdbid like ?', ('%'+imdbidor+'%',))
    cursor3.execute('select genre, theaters, distributor, imdb_id from movie_genres where imdb_id like ?', ('%'+imdbor2+'%',))
    cursor.execute('select company, imdbid from companyinfo where imdbid like ? group by company', ('%'+imdbidor+'%',))
    try:
        results3 = [item2 for item2 in cursor2.fetchall()]
        results6 = [item6 for item6 in cursor3.fetchall()]
        results4 = [item3 for item3 in cursor.fetchall()]
        results7 = [item7 for item7 in cursor7.fetchall()]

        try:
            pre_date = results7[0][0]
        except:
            pre_date = 'None'

        try:
            theaters = results6[0][1]
        except:
            theaters = 0
        try:
            distributor = results6[0][2]
        except:
            distributor = 'None'

    except:
        results3 = ('None',)
        results6 = [('None', 'None', 'None',)]

    return render_template('movies/releasedetails.html', results=results, results3=results3, results4=results4, compane=imdbidor, \
                main_cast=main_cast, remaining_cast=remaining_cast, genres_list=genres_list, release=release, results6=results6, \
                theaters=theaters, distributor=distributor, pre_date=pre_date)


    cursor.close()
    cursor2.close()
    cursor3.close()



