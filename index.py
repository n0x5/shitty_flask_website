import os
import time
import html
from flask import Flask
from flask import render_template
from PIL import Image

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/gallery")
def gallery():
    for root, dirs, files in os.walk(dirgl):
        for name in dirs:
            return render_template('galleryindex.html', dirs=dirs)

@app.route('/gallery/<gal>')
def get_gallery(gal=None):
    dirgl = os.path.join(os.getcwd(), 'static', 'gallery', '%s' % gal)
    for subdir, dirs, files in os.walk(dirgl):
        for image in files:
            return render_template('gallerylist.html', gal=gal, files=files)

@app.route('/gallery/<gal>/create')
def create_thumbs(gal=None):
    dirgl = os.path.join(os.getcwd(), 'static', 'gallery', '%s' % gal)
    for subdir, dirs, files in os.walk(dirgl):
        for image in files:
            if image.endswith(".py"):
                pass
            if image.endswith(".thumbnail"):
                pass
            else:
                thumbc(gal, image)
    print('thumbnail creation for', gal, 'complete!')

def thumbc(gal, image):
    sizes = [(250, 250)]
    dirsm = os.path.join(os.getcwd(), 'static', 'gallery', gal)
    for size in sizes:
        os.makedirs(os.path.join(dirsm, 'thumbs'), exist_ok=True)
        im = Image.open(os.path.join(dirsm, image)).convert('RGB')
        im.thumbnail(size, Image.ANTIALIAS)
        thmbs = os.path.join(dirsm, 'thumbs', image)
        if not os.path.exists(thmbs):
            im.save(thmbs + '.thumbnail', "JPEG")
        else:
            pass

@app.route("/blog")
def get_blog():
    for subdir, dirs, files in os.walk(os.path.join(os.getcwd(), 'blog')):
        for fn in files:
            outpt = [fn.replace(".txt", "") for fn in files]
            return render_template('blogindex.html', outpt=outpt)

@app.route('/blog/<blogid>')
def get_blogid(blogid):
    blogid2 = blogid + '.txt'
    with open(os.path.join(os.getcwd(), 'blog', blogid2), "r") as content:
        content2 = ''.join(content)
        return render_template('blog.html', content2=content2, blogid=blogid)


if __name__ == "__main__":
    app.run()

