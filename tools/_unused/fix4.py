import os
import shutil

cwd = r'/home/coax/websites/hidden2/virtualenv-3.3.5/FlaskApp/static/enshadowrun_images'

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fn2 = os.path.join(subdir, fn)
        fn3 = fn.replace('%28', '(').replace('%29', ')')
        fn4 = os.path.join(subdir, fn3)
        try:
            shutil.copy2(fn2, fn4)
            print(fn2, fn4)
        except shutil.SameFileError:
            print('skipping'+fn4)
            pass
