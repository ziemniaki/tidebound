"""Direct pixel edit of stock Lapras, explicitly requested by the user.

Preserves its poses and opaque silhouette. Adds jade irises, a short faded
gold forehead scar, and sparse translucent stepped mist behind the body.
No generator, blur, interpolation or runtime filtering is used.
"""
from pathlib import Path
from PIL import Image, ImageDraw

G = Path(__file__).resolve().parents[3]
BODY = {
    (65,164,230):(226,240,237), (57,123,164):(166,190,194),
    (115,197,246):(249,253,247), (57,148,197):(206,225,224),
    (24,65,82):(88,115,127), (0,0,0):(43,62,73),
    (246,222,172):(228,233,218), (222,197,131):(183,201,190),
    (213,205,197):(198,213,217), (164,148,148):(133,158,174),
    (90,74,65):(80,103,119), (82,74,74):(67,90,108),
    (246,238,230):(248,252,242)
}
ICON = {
    (112,112,200):(221,235,233), (160,168,240):(247,252,243),
    (192,168,40):(177,199,187), (240,240,40):(224,231,214),
    (184,184,176):(149,176,188), (96,96,88):(95,123,140),
    (64,64,64):(49,73,86), (248,248,248):(247,252,243)
}
GREEN=(63,160,114,255)
PALE_GREEN=(166,233,174,255)
GOLD=(214,199,120,255)
GOLD_SHADOW=(160,151,99,255)

def recolour(original, palette):
    im=original.copy()
    im.putdata([(*palette.get(p[:3],p[:3]),p[3]) if p[3] else (0,0,0,0)
                for p in original.getdata()])
    return im

def cell(im, x, y, colour):
    # Native sprites use a 2x logical pixel grid.
    for dy in range(2):
        for dx in range(2):
            assert im.getpixel((x+dx,y+dy))[3] == 255, (x,y)
            im.putpixel((x+dx,y+dy),colour)

def mist(im, paths):
    layer=Image.new('RGBA',im.size)
    draw=ImageDraw.Draw(layer)
    for i,points in enumerate(paths):
        draw.line(points,fill=(206,231,228,96 if i%2 else 136),width=2)
    # Paint behind, leaving the original opaque silhouette intact.
    return Image.alpha_composite(layer,im)

for folder in ['Front','Back']:
    src=G/'Graphics/Pokemon'/folder/'LAPRAS.png'
    original=Image.open(src).convert('RGBA')
    im=recolour(original,BODY)
    if folder=='Front':
        for x,y in [(96,44),(98,44),(98,48)]: cell(im,x,y,GREEN)
        cell(im,100,44,PALE_GREEN)
        for x,y in [(88,34),(90,36),(90,38),(92,40)]:cell(im,x,y,GOLD)
        cell(im,88,38,GOLD_SHADOW)
        paths=[[(4,128),(10,128),(10,126),(20,126)],
               [(18,144),(34,144),(34,146),(48,146)],
               [(56,140),(66,140),(66,142),(80,142)],
               [(98,146),(114,146),(114,144),(126,144)],
               [(138,130),(152,130),(152,128),(156,128)]]
    else:
        for x,y in [(88,62),(90,64)]:cell(im,x,y,GREEN)
        cell(im,86,58,PALE_GREEN)
        # Only the edge of the forehead mark is visible from behind.
        for x,y in [(88,48),(90,50)]:cell(im,x,y,GOLD)
        paths=[[(4,126),(10,126),(10,124),(18,124)],
               [(132,130),(146,130),(146,128),(154,128)],
               [(144,148),(154,148),(154,146),(158,146)]]
    im=mist(im,paths)
    assert im.size==original.size
    assert all(im.getpixel((x,y))[3]==255 for y in range(im.height) for x in range(im.width)
               if original.getpixel((x,y))[3]==255)
    im.save(src.with_name('LAPRAS_1.png'))
    im.save(G/'Graphics/Pokemon'/(folder+' shiny')/'LAPRAS_1.png')

src=G/'Graphics/Pokemon/Icons/LAPRAS.png'
original=Image.open(src).convert('RGBA')
im=recolour(original,ICON)
for frame,dy in [(0,0),(1,2)]:
    ox=64*frame
    cell(im,ox+20,36+dy,GREEN)
    cell(im,ox+22,34+dy,PALE_GREEN)
    cell(im,ox+16,32+dy,GOLD)
    cell(im,ox+18,34+dy,GOLD_SHADOW)
im=mist(im,[[(2,54),(8,54),(8,56),(14,56)],[(44,60),(56,60),(56,58),(62,58)],
            [(66,56),(72,56),(72,58),(78,58)],[(108,62),(120,62),(120,60),(126,60)]])
im.save(src.with_name('LAPRAS_1.png'))
print('Lapras: original poses, white/jade/gold palette, sparse pixel mist; front/back/shiny/icon exported.')
