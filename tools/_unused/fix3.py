import os
import shutil

cwd = r'F:\dev\hidden2final\static\stargate_images'

for subdir, dirs, files in os.walk(cwd):
    for fn in files:
        fn2 = os.path.join(subdir, fn)
        fn3 = fn.replace(' ', '_')
        fn4 = os.path.join(subdir, fn3)
        try:
            shutil.copy2(fn2, fn4)
            print(fn2, fn4)
        except shutil.SameFileError:
            print('skipping'+fn4)
            pass