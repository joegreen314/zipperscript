from __future__ import division
from PIL import Image
import os, sys, math

o_x = 3296
o_y = 2472
x = int(o_x/10)
y = int(o_y/10)
rows = 12
columns = 12

size = x, y

indir = sys.argv[1]
outfile = indir + "/output.jpg"


infiles = []
for dirpath, dirs, files in os.walk(indir, topdown = True):
    for f in files:
        if f[-4:] == ".jpg":
            infiles.append(os.path.join(dirpath, f))

if len(infiles) < columns:
    columns = len(infiles)
rows = int(math.ceil(len(infiles)/columns))

new_im = Image.new('RGB', (x*columns, y*rows))
print rows, columns, len(infiles)
k=0
for j in xrange(0, y*rows, y):
    for i in xrange(0, x*columns, x):
        if(len(infiles)>k):
            im = Image.open(infiles[k])
            im.thumbnail(size)
            new_im.paste(im, (i, j))
            k=k+1
        else:
            break

new_im.save(outfile, "JPEG", quality = 70)