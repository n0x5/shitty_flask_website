import os
import shutil

cwd = r'F:\dev\hidden2final\static\stargate_images'

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fn2 = os.path.join(subdir, fn)
        fn3 = fn.replace("%27", "'")
        fn4 = os.path.join(subdir, fn3)
        shutil.move(fn2, fn4)
        print(fn2, fn4)
