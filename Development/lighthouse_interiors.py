"""0.7.16: complete native furniture, legible stairs, distinct lighthouse rooms.
Executed after landscape.py. Preserve all events, coordinates and story paths.
"""
import random
I=Image.open(GAME/'Graphics/Tilesets/Interior general.png').convert('RGBA')
interior_tiles=[];interior_cache={};interior_base=384+(I.height//32)*8

def itile(im):
    key=im.tobytes()
    if key not in interior_cache:
        interior_cache[key]=interior_base+len(interior_tiles);interior_tiles.append(im.copy())
    return interior_cache[key]
def crop(box):return I.crop(box)
def native(x,y,w=1,h=1):return crop((x*32,y*32,(x+w)*32,(y+h)*32))
def muted(im,amount=.30):
    grey=im.convert('L').convert('RGBA');grey.putalpha(im.getchannel('A'))
    return Image.blend(im,grey,amount)
def fit_asset(im,w,h):
    if im.width>w*32 or im.height>h*32:im.thumbnail((w*32,h*32),Image.Resampling.NEAREST)
    out=Image.new('RGBA',(w*32,h*32));out.alpha_composite(im,((w*32-im.width)//2,h*32-im.height));return out
def surface(m,im,x,y,solid=False,layer=1):
    for yy in range(im.height//32):
        for xx in range(im.width//32):
            cell=im.crop((xx*32,yy*32,xx*32+32,yy*32+32))
            if cell.getbbox():
                previous=m.layers[layer][y+yy][x+xx]
                if previous>=interior_base:
                    base=interior_tiles[previous-interior_base].copy();base.alpha_composite(cell);cell=base
                m.layers[layer][y+yy][x+xx]=itile(cell)
            if solid:m.walk[y+yy][x+xx]=False
def prop(m,im,x,y,w,h,solid=True):surface(m,fit_asset(im.copy(),w,h),x,y,solid)

# Pixel-exact object bounds avoid neighbouring objects and half-sprite fragments.
BED=muted(crop((24,4828,74,4896)))
SHELF=muted(crop((96,4480,160,4544)))
CUPBOARD=muted(crop((66,4600,112,4656)))
CABINET=muted(crop((192,4598,256,4656)),.65)
SINK=muted(crop((32,4728,96,4784)))
ImageDraw.Draw(SINK).rectangle((32,0,63,7),fill=(0,0,0,0))
COOKER=muted(crop((160,4740,192,4786)))
SOFA=muted(crop((64,5026,160,5088)))
STOOL=muted(crop((230,5098,252,5120)))
PLANT=muted(crop((128,5538,160,5600)))
BOOK=Image.new('RGBA',(32,32));bd=ImageDraw.Draw(BOOK)
bd.rectangle((5,18,8,30),fill=(76,61,49,255));bd.rectangle((23,18,26,30),fill=(76,61,49,255))
bd.rectangle((2,8,29,24),fill=(101,80,57,255),outline=(60,56,49,255),width=2)
bd.line((4,9,27,9),fill=(166,137,96,255),width=2)
bd.rectangle((8,10,23,20),fill=(202,196,165,255),outline=(96,104,100,255))
bd.line((15,11,15,19),fill=(133,127,109,255));bd.line((10,14,13,14),fill=(141,138,120,255));bd.line((18,14,21,14),fill=(141,138,120,255))
BASIN=muted(crop((2,4770,30,4800)))
STAIR_DOWN=muted(crop((28,4140,96,4216)),.55)
STAIR_UP=muted(crop((100,4140,166,4216)),.55)
TABLE=muted(native(6,212,2,2))
# Archive cupboards retain native silhouettes, with weathered timber colours.
ARCHIVE=CUPBOARD.copy()
for yy in range(ARCHIVE.height):
    for xx in range(ARCHIVE.width):
        r,g,b,a=ARCHIVE.getpixel((xx,yy))
        if a:
            l=int(r*.3+g*.5+b*.2)
            ARCHIVE.putpixel((xx,yy),(int(l*.70),int(l*.65),int(l*.54),a))

def floor_tile(stone=False,variant=0):
    if not stone:
        im=muted(native(4,78));return Image.blend(im,Image.new('RGBA',(32,32),(101,83,65,255)),.22)
    v=[0,3,-2][variant%3];im=Image.new('RGBA',(32,32),(94+v,102+v,105+v,255));d=ImageDraw.Draw(im)
    d.line((0,31,31,31),fill=(69,79,84,255),width=2);d.line((31,0,31,31),fill=(69,79,84,255),width=2)
    d.line((2,1,28,1),fill=(112,119,120,255),width=1)
    r=random.Random(716+variant)
    for _ in range(5):
        x=r.randrange(2,14)*2;y=r.randrange(2,14)*2;d.rectangle((x,y,x+1,y+1),fill=(86+v,95+v,99+v,255))
    return im

def wall(stone=False):
    im=Image.new('RGBA',(32,64),(127,123,103,255));d=ImageDraw.Draw(im)
    if stone:
        d.rectangle((0,0,31,63),fill=(74,85,92,255))
        for y in [0,16,32,48]:
            d.line((0,y,31,y),fill=(42,53,62,255),width=2)
            x=8 if y%32 else 24;d.line((x,y,x,y+14),fill=(51,63,71,255),width=2)
        d.rectangle((0,56,31,63),fill=(47,57,64,255));d.line((0,56,31,56),fill=(112,116,109,255),width=2)
    else:
        d.rectangle((0,0,31,7),fill=(78,64,53,255));d.line((0,8,31,8),fill=(166,147,115,255),width=2)
        d.rectangle((0,36,31,63),fill=(91,78,60,255))
        for x in [0,16,30]:d.line((x,38,x,62),fill=(67,62,52,255),width=2)
        d.rectangle((0,34,31,38),fill=(159,135,96,255));d.rectangle((0,60,31,63),fill=(48,48,45,255))
    return im

def room(m,x,y,w,h,stone=False):
    m.layers=[[[0]*m.w for _ in range(m.h)] for _ in range(3)];m.walk=[[False]*m.w for _ in range(m.h)]
    for yy in range(y,y+h):
        for xx in range(x,x+w):m.layers[0][yy][xx]=itile(floor_tile(stone,(xx+yy)%3));m.walk[yy][xx]=True
    for xx in range(x,x+w):surface(m,wall(stone),xx,y-2)
    for xx in [x,x+w-1]:
        for yy in range(y,y+h):
            edge=Image.new('RGBA',(32,32));d=ImageDraw.Draw(edge);a=0 if xx==x else 26
            d.rectangle((a,0,a+5,31),fill=(48,54,56,255));d.line((a+3,0,a+3,31),fill=(124,125,114,255),width=2);surface(m,edge,xx,yy,False,2)

def rug(m,x,y,w,h,color):
    im=Image.new('RGBA',(w*32,h*32));d=ImageDraw.Draw(im)
    d.rectangle((2,2,w*32-3,h*32-3),fill=color,outline=(64,61,59,255),width=2)
    d.rectangle((8,8,w*32-9,h*32-9),outline=(172,155,120,255),width=2)
    for xx in range(10,w*32-10,12):
        d.rectangle((xx,12,xx+3,13),fill=(140,135,116,255));d.rectangle((xx,h*32-14,xx+3,h*32-13),fill=(140,135,116,255))
    # Composite over wood so the transparent rug margins never become void.
    base=Image.new('RGBA',im.size)
    for yy in range(h):
        for xx in range(w):base.alpha_composite(floor_tile(),(xx*32,yy*32))
    base.alpha_composite(im);surface(m,base,x,y,False,0)

def window(m,x,y,w=2):
    im=Image.new('RGBA',(w*32,64));d=ImageDraw.Draw(im)
    d.rectangle((2,4,w*32-3,53),fill=(52,60,63,255),outline=(166,162,141,255),width=2)
    d.rectangle((8,10,w*32-9,45),fill=(22,39,57,255))
    for xx in range(14,w*32-10,18):d.line((xx,12,xx,43),fill=(59,78,87,255),width=2)
    d.line((8,31,w*32-9,31),fill=(84,99,107,255),width=2)
    d.rectangle((0,52,w*32-1,59),fill=(101,103,97,255));d.line((0,52,w*32-1,52),fill=(191,184,153,255),width=2)
    # Keep the wall behind the glass and sill, including transparent margins.
    base=Image.new('RGBA',im.size)
    for xx in range(w):base.alpha_composite(wall(m in [lantern,basement,vault]),(xx*32,0))
    base.alpha_composite(im);surface(m,base,x,y)

def stairs(m,x,y,up=True):
    surface(m,fit_asset((STAIR_UP if up else STAIR_DOWN).copy(),2,3),x,y)
    for yy in range(y,y+3):
        for xx in range(x,x+2):m.walk[yy][xx]=True

def lamp(m,x,y):
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    d.rectangle((9,26,23,29),fill=(68,59,48,255));d.rectangle((14,11,17,27),fill=(130,112,73,255))
    d.rectangle((9,6,22,18),fill=(89,82,64,255));d.rectangle((12,8,19,15),fill=(234,191,111,255));d.rectangle((8,4,23,7),fill=(65,68,64,255));surface(m,im,x,y)

room(bedroom,2,4,12,8)
window(bedroom,4,2);window(bedroom,10,2)
prop(bedroom,BED,3,4,2,3);prop(bedroom,SHELF,11,4,2,2);prop(bedroom,CUPBOARD,8,4,2,2)
rug(bedroom,5,7,5,3,(74,92,100,255));prop(bedroom,BOOK,3,8,1,1);lamp(bedroom,3,9)
prop(bedroom,STOOL,4,9,1,1);prop(bedroom,PLANT,12,9,1,2)
stairs(bedroom,7,10,False);bedroom.rect(8,12,1,1,itile(floor_tile()),walk=True)

room(home,2,3,16,11)
window(home,8,1);window(home,12,1)
stairs(home,5,1);stairs(home,16,1);stairs(home,2,10,False)
prop(home,SHELF,3,3,2,2);prop(home,CUPBOARD,10,3,2,2)
prop(home,SINK,12,4,2,2);prop(home,COOKER,14,4,1,2);prop(home,BASIN,15,5,1,1)
rug(home,7,6,4,4,(100,76,64,255));prop(home,TABLE,8,7,2,2)
prop(home,SOFA,4,8,3,2);prop(home,BOOK,4,10,1,1,False);lamp(home,5,10)
prop(home,PLANT,15,7,1,2);rug(home,14,10,2,2,(87,99,84,255));prop(home,CUPBOARD,16,10,2,2)
home.rect(10,14,1,1,itile(floor_tile()),walk=True)
for xx in range(3,13):home.walk[7][xx]=True
for yy in range(7,12):home.walk[yy][3]=True

room(lantern,3,3,8,8,True)
window(lantern,3,1);window(lantern,5,1,4);window(lantern,9,1)
beacon=Image.new('RGBA',(96,128));b=ImageDraw.Draw(beacon)
b.ellipse((4,101,91,125),fill=(41,51,57,255),outline=(146,148,128,255),width=2)
b.rectangle((34,75,61,111),fill=(94,100,96,255));b.rectangle((40,75,55,109),fill=(135,139,122,255))
b.ellipse((12,70,83,91),fill=(67,77,80,255),outline=(158,143,103,255),width=2)
b.rectangle((20,22,75,75),fill=(99,94,70,255));b.ellipse((20,8,75,36),fill=(157,139,88,255),outline=(51,61,66,255),width=2)
b.rectangle((28,25,67,75),fill=(120,128,112,255))
for yy in range(26,75,6):b.line((30,yy,65,yy),fill=(180,175,128,255),width=2)
for xx in [20,24,68,72]:b.rectangle((xx,24,xx+3,79),fill=(68,74,68,255))
b.ellipse((18,73,77,87),fill=(123,114,82,255),outline=(57,66,67,255),width=2);b.rectangle((44,0,51,13),fill=(76,85,81,255))
surface(lantern,beacon,5,2,True)
prop(lantern,ARCHIVE,3,6,2,2);prop(lantern,BOOK,4,8,1,1,False)
stairs(lantern,5,9,False);lantern.rect(6,11,1,1,itile(floor_tile(True)),walk=True)
prop(lantern,STOOL,9,8,1,1,False)
glow=Image.new('RGBA',(96,128));g=ImageDraw.Draw(glow)
for yy in range(26,75,6):g.rectangle((30,yy,65,yy+2),fill=(255,221,144,180))
g.rectangle((43,29,51,70),fill=(255,232,174,130));glow.save(GAME/'Graphics/Pictures/Tidebound_Beacon_Glow.png')

room(basement,3,4,20,13,True);stairs(basement,5,12)
for x in [10,13,20]:prop(basement,ARCHIVE,x,4,2,2)
prop(basement,SHELF,4,8,2,2);prop(basement,ARCHIVE,20,8,2,2)
prop(basement,BASIN,9,13,1,1);prop(basement,ARCHIVE,14,13,2,2)
for x in [15,18]:
    for y in [2,3,4]:surface(basement,wall(True).crop((0,0,32,32)),x,y,True)

room(vault,3,3,22,16,True)
for x in [4,7,19,22]:prop(vault,ARCHIVE,x,3,2,2)
for x in [4,22]:
    for y in [7,12]:prop(vault,ARCHIVE,x,y,2,2)
for y in range(7,18):
    for x in [11,12,13]:
        im=floor_tile(True);dr=ImageDraw.Draw(im)
        if x in [11,13]:dr.line((3 if x==11 else 28,0,3 if x==11 else 28,31),fill=(143,142,121,255),width=2)
        vault.layers[0][y][x]=itile(im)
for x in [8,17]:prop(vault,CABINET,x,14,2,2)
vault.rect(12,18,1,1,itile(floor_tile(True)),walk=True)
for m in [bedroom,home,lantern,basement,vault]:
    for name,x,y,trigger,blocks in m.targets:
        if blocks:m.walk[y][x]=False
exec((DEV/'psychic_maze.py').read_text())
exec((DEV/'dream_room.py').read_text())
exec((DEV/'folded_room.py').read_text())
exec((DEV/'hideout_room.py').read_text())

sets=loads((GAME/'Data/Tilesets.rxdata').read_bytes())
id=next((i for i,t in enumerate(sets) if t and t.attributes.get('@name')=='Tidebound Lighthouse'),len(sets))
ts=loads(writes(sets[3]));ts.attributes.update({'@id':id,'@name':'Tidebound Lighthouse','@tileset_name':'TideboundLighthouse'})
h=I.height+((len(interior_tiles)+7)//8)*32;assert h<=16384
atlas=Image.new('RGBA',(256,h));atlas.alpha_composite(I)
for i,im in enumerate(interior_tiles):atlas.alpha_composite(im,((i%8)*32,I.height+(i//8)*32))
atlas.save(GAME/'Graphics/Tilesets/TideboundLighthouse.png')
for key in ['@passages','@priorities','@terrain_tags']:
    raw=ts.attributes[key]._dump();size=struct.unpack('<5i',raw[:20])[4]
    vals=list(struct.unpack('<'+'h'*size,raw[20:]));vals=vals[:interior_base]+[0]*max(0,interior_base-len(vals));vals += [0]*len(interior_tiles);ts.attributes[key]=table(vals,len(vals))
if id==len(sets):sets.append(ts)
else:sets[id]=ts
(GAME/'Data/Tilesets.rxdata').write_bytes(writes(sets))
for m in [bedroom,home,lantern,basement,vault,maze,dream,folded,hideout]:m.tileset=id
(DEV/'lighthouse_manifest.json').write_text(json.dumps({'maps':[101,104,107,110,111],'tileset':id,'tiles':len(interior_tiles),'revision':1},indent=2))
