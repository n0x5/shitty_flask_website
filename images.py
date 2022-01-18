try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
from PIL import Image
import time

@app.route("/images")
def gallery2():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort(reverse=True)

        return render_template('gallery2index.html', results2=results2)


@app.route("/images3/celebs")
def celblist(groups=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagename5.db'))
    cursor = connection.cursor()
    sql = 'select cname, count(fn) c, cname, subfolder from celebs group by cname having c > 0 order by c desc'
    cursor.execute(sql)
    years = [(item[0], item[1], item[2].replace(' ', '%25')) for item in cursor.fetchall()]
    return render_template('celeblist.html', years=years)


@app.route("/images/<search>/<sizew>")
def i7games(search=None, sizew=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images \
        where (fullpath like ? or exifd like ?) and sizewidth > ? order by ftime desc", ('%'+search+'%', '%'+search+'%', int(sizew)))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''),
                 str(item[4]).replace(', ', 'x'), item[5]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)


@app.route("/images/<search>")
def i613games(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd, celebname \
        from images where (fullpath like ? or exifd like ? or celebname like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''), 
                str(item[4]).replace(', ', 'x'), item[5], item[6], item[7], item[8].replace('[', '').replace("'", "").replace(']', '')) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('imagesname.html', results=results, search=search, gcounts=gcounts)


@app.route("/images/<search>/zip")
def i613games222(search=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3111.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd, celebname \
        from images where (fullpath like ? or exifd like ? or celebname like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''), 
                unicode(item[4]).replace(', ', 'x'), item[5], item[6], item[7], item[8].replace('[', '').replace("'", "").replace(']', '')) for item in cursor.fetchall()]
    zipr = os.path.join(os.path.dirname(__file__), 'static', '{}_{}.zip' .format(search.replace('%', '_'), time.strftime("%m_%d_%Y")))
    with zipfile.ZipFile(zipr, 'w' ) as myzip:
        for fi2 in results:
            path1 = os.path.join(os.path.dirname(__file__), 'static', 'gallery', fi2[2].encode('utf8'), fi2[0].encode('utf8'))
            myzip.write(path1.encode('utf8'), fi2[2].encode('utf8')+'_'+fi2[0].encode('utf8').replace('(', '_').replace(')', '').replace(' ', '_').replace('__', '_'))
    return 'zip complete <a href="/static/{}_{}.zip">{}</a>' .format(search.replace('%', '_'), time.strftime("%m_%d_%Y"), search.replace('%', '_'))


@app.route("/gallery")
def gallery():
    for root, dirs, files in os.walk(str(os.path.join(os.path.dirname(__file__), 'static', 'gallery'))):
        results2 = [image for image in dirs]
        results2.sort()

        return render_template('galleryindex.html', results2=results2)

@app.route('/gallery/<gal>')
def get_gallery(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    for subdir, dirs, files in os.walk(str(dirgl)):
        if 'thumbs' not in subdir:
            results2 = [os.path.join(dirgl, image) for image in files]
            results2.sort(key=os.path.getmtime, reverse=True)

        imh = [Image.open(image).size for image in results2]
        results = [os.path.basename(image).decode('utf-8', errors='replace').replace('#', '%23') for image in results2]
        gcount = len(results)
        results3 = zip(results, imh)

    return render_template('gallerylist.html', gal=gal, results3=results3, gcount=gcount)

@app.route('/gallery/<gal>/create')
def create_thumbs(gal=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    dirth = os.path.join(dirgl, 'thumbs')
    if not os.path.exists(dirth):
        os.makedirs(dirth)
    os.chmod(dirth, 0o777)
    for subdir, dirs, files in os.walk(str(dirgl)):
        for image in files:
                if not image.startswith("thumb_"):
                    try:
                        thumbc(gal, image)
                    except IOError:
                        pass

    return redirect('/gallery/{}' .format(gal), code=302)

def thumbc(gal, image):
    sizes = [(250, 250)]
    dirsm = os.path.join(os.path.dirname(__file__), 'static', 'gallery', '{}' .format(gal))
    dirth = os.path.join(dirsm, 'thumbs')

    for size in sizes:
        im = Image.open(str(os.path.join(dirsm, image))).convert('RGB')
        im.thumbnail(size, Image.ANTIALIAS)
        thmbs = os.path.join(dirsm, 'thumb_'+image)
        quality_val = 100
        thumbs2 = os.path.join(dirsm, 'thumbs', 'thumb_'+image)
        if not os.path.exists(thumbs2): 
            im.save(thumbs2, "JPEG", quality=quality_val)
            os.chmod(thumbs2, 0o777)



####### FILE UPLOAD DRAG N DROP ######

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp3', 'mp4', 'mkv', 'avi'])
UPLOAD_FOLDER = r'/home/coax/websites/hidden2/virtualenv-3.3.5/FlaskApp/static/hosted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/uploadf/<gal>', methods=['GET', 'POST'])
def upload_form(gal=None):
    if not session.get('logged_in'):
        return 'access denied'

    return render_template('upload.html', gal=gal)

@app.route('/file-upload/<gal>', methods=['GET', 'POST'])
def upload_file(gal=None):
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/uploadf')
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], gal)): 
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], gal))
            os.chmod(os.path.join(app.config['UPLOAD_FOLDER'], gal), 0o777)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], gal, filename))
            flash('File successfully uploaded')
            return redirect('/uploadf')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect('/uploadf')



@app.route('/pics/<gal>')
def get_gallery_pics(gal=None, results3=None, gcount=None):
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'hosted', '{}' .format(gal))
    for subdir, dirs, files in os.walk(str(dirgl)):
        if 'thumbs' not in subdir:
            results2 = [os.path.join(dirgl, image) for image in files]
            #results2.sort(key=os.path.getmtime, reverse=True)
            results2.sort()

        imh = [str(Image.open(image).size).replace('(', '').replace(')', '').replace(', ', 'x') for image in results2]
        results4 = [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(image))) for image in results2]
        results = [os.path.basename(image).replace('#', '%23') for image in results2]
        gcount = len(results)
        results3 = zip(results, imh, results4)

    return render_template('galleryhosted.html', gal=gal, results3=results3, gcount=gcount)


@app.route('/pics')
def get_gallery_folders():
    dirgl = os.path.join(os.path.dirname(__file__), 'static', 'hosted')
    empty1 = []
    empty2 = []
    for subdir, dirs, files in os.walk(dirgl):
        empty1.append(os.path.basename(subdir))

    return render_template('picsindex.html', empty1=empty1)


@app.route("/images/wallpaper/<search>/<sizew>/<sizeh>")
def i7gam111es(search=None, sizew=None, sizeh=None):
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'imagesnew3.db'))
    cursor = connection.cursor()
    cursor.execute("select file, fullpath, subfolder, file, sizewidth, sizeheight, ftime, exifd from images \
        where (fullpath like ? or exifd like ?) and (sizewidth like ? and sizeheight like ?) order by ftime desc", ('%'+search+'%', '%'+search+'%', int(sizew), int(sizeh)))
    results = [(item[0], item[1], item[2], unicode(item[3]).split(' ')[0].replace('.jpg', ''),
                 str(item[4]).replace(', ', 'x'), item[5], item[6]) for item in cursor.fetchall()]
    gcounts = len(results)
    cursor.close()
    return render_template('images.html', results=results, search=search, gcounts=gcounts)