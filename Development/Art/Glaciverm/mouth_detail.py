"""Direct-pixel Wurmple eye and omega-mouth detail on the exported logical sprite.

Run by export.sh before nearest-neighbour enlargement and icon generation.
Coordinates refer to the retained 56x47 front view. No resampling or changes
to horn, shell or body. Yellow eyes reference the included Wurmple sprite.
"""
from pathlib import Path
from PIL import Image

path = Path(__file__).resolve().parent / 'exported/front.png'
im = Image.open(path).convert('RGBA')
assert im.size == (56, 47)
cream = (241, 244, 223, 255)
colours = {'2':cream, '5':(218,207,173,255), '7':(58,66,81,255)}
# Remove only the previous grin's remaining dark pixels behind the new snout.
for x,y in [(12,22),(13,22),(14,22),(11,23),(9,24)]:
    im.putpixel((x,y), cream)
# Two rounded mouth lobes, with a deeper central cleft.
# Clear the old mouth's lower rim so its new indentation is transparent.
for y in range(26,29):
    for x in range(12): im.putpixel((x,y),(0,0,0,0))
rows = [
    '....775577....',
    '..7522222257..',
    '.752252222257.',
    '75222522222257',
    '72222522222227',
    '75222722222257',
    '.752277222257.',
    '..7557.75557..',
    '...77...77...',
    '.............',
]
for dy,row in enumerate(rows):
    for x,c in enumerate(row):
        if c != '.': im.putpixel((x,19+dy),colours[c])
# Rounded yellow eye surrounds and compact dark pupils, like Wurmple.
eye = {'D':(11,18,42,255), 'Y':(233,212,72,255),
       'L':(252,235,126,255), 'S':(183,161,62,255),
       'P':(58,66,81,255)}
for dy,row in enumerate(['..DDD..','.DLYYD.','DYLPPYD','DYPPPYD','DSPPSYD','.DSSSD.']):
    for dx,c in enumerate(row):
        if c != '.':im.putpixel((13+dx,14+dy),eye[c])
# A narrow sliver of the far eye remains visible beside the snout.
for x,y,c in [(2,16,'D'),(3,16,'Y'),(2,17,'Y'),(3,17,'P'),(2,18,'S')]:
    im.putpixel((x,y),eye[c])
im.save(path)
