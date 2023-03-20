try:
    from __main__ import app
except:
    from app import app
import os
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from PIL import Image
import re

def sort_folder(fn):
    result = re.search(r'New folder \((.+?)\)', fn)
    if result is None:
        return 0
    return int(result.group(1))

@app.route('/gallery')
@app.route('/gallery/')
def gallery_index():
    root_gallery = request.args.get('dir')
    folder_gallery = request.args.get('folder')
    if root_gallery is None and folder_gallery is None:
        return render_template('gallery/gallery_index.html')

    folders = root_gallery.split('\\')
    path3 = os.path.join(app.root_path, 'static', root_gallery)
    if folder_gallery:
        root_gallery = os.path.join(root_gallery, folder_gallery)
        thumbs2 = os.path.join(path3, folder_gallery, 'thumbs')
        if not os.path.exists(thumbs2):
            os.makedirs(thumbs2)
    path = os.path.join(app.root_path, 'static', root_gallery)
    path2 = os.path.join('static', root_gallery)
    path_url = os.path.join('gallery', root_gallery)
    dir_list = []
    file_list = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                if 'thumbs' not in entry.name:
                    dir_list.append(entry.name)
            if entry.is_file():
                file_list.append(entry.name)
            

    if len(dir_list) != 0:
        dirfold = 'Folders'
    else:
        dirfold = ''
    if len(file_list) != 0:
        filefold = 'Files'
    else:
        filefold = ''

    for subdir, dirs, files in os.walk(path3):
        for fn in files:
            endp = os.path.join(subdir, fn)
            endpoint_thumb = os.path.join(subdir, 'thumbs', fn)

            if not os.path.exists(os.path.join(subdir, 'thumbs')):
                os.makedirs(os.path.join(subdir, 'thumbs'))
            if not os.path.exists(endpoint_thumb):
                width = 150
                try:
                    im = Image.open(endp)
                    widthper = (width/float(im.size[0]))
                    heightsize = int((float(im.size[1])*float(widthper)))
                    size = width, heightsize
                    print('saving {}' .format(endpoint_thumb))
                    im2 = im.resize(size, Image.LANCZOS)
                    im2.save(endpoint_thumb, "JPEG", quality=90)
                except:
                    pass
    
    return render_template('gallery/gallery.html', dir_list=sorted(sorted(dir_list), key=sort_folder), file_list=reversed(sorted(file_list)), root_gallery=root_gallery, \
                             path=path2, path_url=path_url, dirfold=dirfold, filefold=filefold, rooto=request.args.get('dir'))


