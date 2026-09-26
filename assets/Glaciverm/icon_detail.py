"""Keep the yellow eye rim readable after nearest-neighbour icon reduction."""
from pathlib import Path
from PIL import Image, ImageDraw

p = Path(__file__).resolve().parent / 'exported/icon1.png'
im = Image.open(p).convert('RGBA')
ImageDraw.Draw(im).rectangle((22,26,23,27), fill=(233,212,72,255))
im.save(p)
