from flask import Flask
from flask import render_template
from PIL import Image
import os
import html
app = Flask(__name__)

@app.route("/")
def hello():
    return( "Hello World!")

@app.route("/gallery")
def gallery():
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'static', 'gallery')):
        for name in dirs:
            return render_template('galleryindex.html', dirs=dirs)

@app.route('/gallery/<galid>')
def get_gallery(galid=None):
    
    for subdir, dirs, files in os.walk(os.path.join(os.getcwd(), 'static', 'gallery', '%s' % galid)):
        for image in files:
            return render_template('gallerylist.html', galid=galid, files=files)

@app.route('/gallery/<galid>/create')
def create_thumbs(galid=None):
    sizes = [(250,250)]
    for subdir, dirs, files in os.walk(os.path.join(os.getcwd(), 'static', 'gallery', '%s' % galid)):
        for image in files:
            if image.endswith(".py"):
                pass
            if image.endswith(".thumbnail"):
                pass
            else:
                for size in sizes:
                    if not os.path.exists(os.path.join(os.getcwd(), 'static', 'gallery', galid, 'thumbs')): 
                        os.makedirs(os.path.join(os.getcwd(), 'static', 'gallery', galid, 'thumbs'))
                    im = Image.open(os.path.join(os.getcwd(), 'static', 'gallery', galid, image)).convert('RGB')
                    im.thumbnail(size, Image.ANTIALIAS)
                    if not os.path.exists(os.path.join(os.getcwd(), 'static', 'gallery', galid, 'thumbs', image) + ".thumbnail"):
                        im.save(os.path.join(os.getcwd(), 'static', 'gallery', galid, 'thumbs', image) + ".thumbnail", "JPEG")
                    else:
                        pass
    print('thumbnail creation for', galid,' complete!')           

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
