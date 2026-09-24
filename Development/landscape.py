"""0.7.15 landscape pass. Executed after shoreline generation by rebuild_maps.
Native tile artwork is composed into a reproducible atlas, not painted over maps.
All coordinates here are absolute. Original event IDs/positions remain intact.
"""
import math, random
from collections import deque

_native = Image.open(GAME/'Graphics/Tilesets/Outside.png').convert('RGBA').crop((0,0,256,456*32))
# Story maps use native rows through 451. Leave room below the GL 16K texture limit.
_tile_images=[]; _tile_cache={}
_base_count=384+(_native.height//32)*8

def baked(im, tag=0):
    key=(im.tobytes(),tag)
    if key not in _tile_cache:
        _tile_cache[key]=_base_count+len(_tile_images)
        _tile_images.append((im.copy(),tag))
    return _tile_cache[key]

def art(x,y,w=1,h=1):return _native.crop((x*32,y*32,(x+w)*32,(y+h)*32))
PINE=art(0,55,3,3)
ROUND=art(3,61,3,3)
AUTUMN=art(3,67,3,3)
ROCK=art(0,108,3,3)
BUSH=art(3,59)
SMALLROCKS=[art(0,140,2,2).crop((16,16,48,48)),art(2,140,2,2).crop((16,16,48,48))]
FLOWER=Image.open(GAME/'Graphics/Autotiles/Flowers1.png').convert('RGBA').crop((0,0,32,32))
WHITE=art(7,3)

class Landscape:
    def __init__(self,m):
        self.m=m;self.rng=random.Random(1400+m.id)
        self.overlay=Image.new('RGBA',(m.w*32,m.h*32))
        self.sprites=[];self.occupied=set();self.protected=set();self.ground_cells=set();self.clearings=set()
        self.native_layer=copy.deepcopy(m.layers[1])
        # Event centres and their interaction spaces remain open. Autoruns excluded.
        for name,x,y,trigger,blocks in m.targets:
            if trigger==3:continue
            for yy in range(y-1,y+2):
                for xx in range(x-1,x+2):self.protected.add((xx,yy))
        # Every existing road/path/plank remains available to scripted movement.
        for y in range(m.h):
            for x in range(m.w):
                v=m.layers[0][y][x]
                if m.walk[y][x] and v>=384 and v!=tile(1,0) and not (m.id==102 and v==tile(2,27)):self.protected.add((x,y))
    def reserve(self,x,y,w,h):self.protected.update((xx,yy) for yy in range(y,y+h) for xx in range(x,x+w))
    def valid(self,x,y,w,h,protected=True):
        m=self.m
        if x<0 or y<0 or x+w>m.w or y+h>m.h:return False
        return all((xx,yy) not in self.occupied and (not protected or (xx,yy) not in self.protected)
            and m.layers[1][yy][xx]==0 and m.layers[0][yy][xx]==tile(1,0)
            for yy in range(y,y+h) for xx in range(x,x+w))
    def plant(self,img,x,y,w=3,h=3,check=True,solid=True):
        if check and not self.valid(x,y,w,h):return False
        m=self.m
        if x<0 or y<0 or x+w>m.w or y+h>m.h:return False
        img=img.resize((w*32,h*32),Image.Resampling.NEAREST)
        self.sprites.append((y+h,img,x*32,y*32))
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                self.occupied.add((xx,yy))
                if solid:m.walk[yy][xx]=False
        return True
    def decal(self,img,x,y):
        if 0<=x<self.m.w and 0<=y<self.m.h and self.m.layers[1][y][x]==0:
            self.overlay.alpha_composite(img,(x*32,y*32))
    def ground(self,x,y,amount=.16):
        if self.m.layers[0][y][x]==tile(1,0):self.ground_cells.add((x,y))
    def finish(self):
        # Feather connected humus beds into grass. No square patchwork under trees.
        for x,y in sorted(self.ground_cells):
            im=art(1,0);px=im.load()
            for yy in range(32):
                for xx in range(32):
                    edge=1.0
                    for dx,dy,dist in [(-1,0,xx),(1,0,31-xx),(0,-1,yy),(0,1,31-yy)]:
                        if (x+dx,y+dy) not in self.ground_cells:edge=min(edge,min(1,dist/12))
                    factor=.16*edge;r,g,b,a=px[xx,yy]
                    px[xx,yy]=(round(r*(1-factor)+75*factor),round(g*(1-factor)+86*factor),round(b*(1-factor)+66*factor),a)
            self.m.layers[0][y][x]=baked(im)
        for _,im,x,y in sorted(self.sprites,key=lambda v:v[0]):self.overlay.alpha_composite(im,(x,y))
        for y in range(self.m.h):
            for x in range(self.m.w):
                im=self.overlay.crop((x*32,y*32,x*32+32,y*32+32))
                if im.getbbox():self.m.layers[2][y][x]=baked(im)

# Native tree sprites use these exact complete rectangles (no editor placeholders).
# The isolated round tree occupies columns 3..5, rows 63..65.

def clear_nature(m,all_forest=False):
    for y in range(m.h):
        for x in range(m.w):
            v=m.layers[1][y][x]
            row=(v-384)//8 if v>=384 else -1
            nature=(52<=row<=75 or 108<=row<=110 or (139<=row<=143 and (v-384)%8<4) or v in [240,tile(6,0),tile(7,3),tile(7,0)])
            if nature:
                m.layers[1][y][x]=0
                # Restore old nature footprints only on real land, not water or borders.
                if m.layers[0][y][x]>=384 and (m.id!=103 or 3<=x<=32 and 3<=y<=26):m.walk[y][x]=True
    for _,x,y,_,blocks in m.targets:
        if blocks:m.walk[y][x]=False

def grass_patch(p,cx,cy,rx,ry):
    m=p.m
    for y in range(max(0,cy-ry-1),min(m.h,cy+ry+2)):
        for x in range(max(0,cx-rx-1),min(m.w,cx+rx+2)):
            d=((x-cx)/rx)**2+((y-cy)/ry)**2
            if d<1.0+p.rng.uniform(-.13,.13) and m.walk[y][x] and (x,y) not in p.protected and m.layers[1][y][x]==0:
                m.layers[1][y][x]=tile(7,0)

def groves(p,centres,attempts):
    # Filled canopy blocks, with overlapping crowns as in early-generation maps.
    # Clearings and corridors are carved OUT of the forest, not dotted with trees.
    m=p.m
    def allowed(x,y,size):
        cells=[(xx,yy) for yy in range(y,y+size) for xx in range(x,x+size)]
        return all(0<=xx<m.w and 0<=yy<m.h and (xx,yy) not in p.protected
            and (xx,yy) not in p.clearings and m.layers[1][yy][xx]==0
            and m.layers[0][yy][xx]==tile(1,0) for xx,yy in cells)
    def in_grove(x,y):
        return min(((x-cx)/rx)**2+((y-cy)/ry)**2 for cx,cy,rx,ry in centres)<3.6
    for y in range(0,m.h-2,2):
        for x in range((y//2)%2,m.w-2,2):
            if allowed(x,y,3) and in_grove(x+1,y+1):
                im=ROUND if (x//7+y//6)%3 else PINE
                p.plant(im,x,y,3,3,check=False)
    # Younger trees thicken edges, while low shrubs soften the last single tiles.
    for size in [2,1]:
        for y in range(m.h-size):
            for x in range(m.w-size):
                if not allowed(x,y,size) or not in_grove(x,y):continue
                cells={(xx,yy) for yy in range(y,y+size) for xx in range(x,x+size)}
                if cells & p.occupied:continue
                nearby=sum((x+dx,y+dy) in p.occupied for dx,dy in [(-1,0),(size,0),(0,-1),(0,size)])
                if nearby and (size==2 or (x+y)%3==0):p.plant(PINE if size==2 else BUSH,x,y,size,size,check=False)
    for x,y in sorted(p.occupied):p.ground(x,y,.16)

def clearing(p,x,y,w,h):
    p.clearings.update((xx,yy) for yy in range(y,y+h) for xx in range(x,x+w))

def scree(p,regions):
    # Overlapping whole boulders follow the rocky land boundary, with smaller feet.
    m=p.m
    for x0,y0,x1,y1 in regions:
        for y in range(y0,y1,2):
            for x in range(x0+(y%4)//2,x1,2):
                size=2 if (x+y)%4 else 3
                cells=[(xx,yy) for yy in range(y,y+size) for xx in range(x,x+size)]
                if any(not(0<=xx<m.w and 0<=yy<m.h) or (xx,yy) in p.protected or m.layers[1][yy][xx] for xx,yy in cells):continue
                # Don't fill open ocean: these are contiguous land-edge formations.
                if not any(m.layers[0][yy][xx]>=192 for xx,yy in cells):continue
                p.plant(ROCK,x,y,size,size,check=False)
                for xx,yy in cells:p.ground(xx,yy)

def rock_group(p,x,y,scale=3,coastal=False):
    m=p.m
    if coastal:
        cells=[(xx,yy) for yy in range(y,y+scale) for xx in range(x,x+scale)]
        if any(not(0<=xx<m.w and 0<=yy<m.h) or (xx,yy) in p.protected or (xx,yy) in p.occupied or m.layers[1][yy][xx] for xx,yy in cells):return
        p.plant(ROCK,x,y,scale,scale,check=False)
    elif not p.plant(ROCK,x,y,scale,scale):return
    for dx,dy in [(-1,1),(scale,scale-1),(scale-1,scale),(0,scale),(-1,scale)]:
        xx,yy=x+dx,y+dy
        if not(0<=xx<m.w and 0<=yy<m.h) or (xx,yy) in p.protected or (xx,yy) in p.occupied:continue
        if m.layers[1][yy][xx] or m.layers[0][yy][xx]<192:continue
        p.plant(p.rng.choice(SMALLROCKS),xx,yy,1,1,check=False)
        if m.layers[0][yy][xx]==tile(1,0):p.ground(xx,yy,.3)

# LISTENING WOOD: the path threads three groves, a key clearing, pool and camp.
clear_nature(forest,True)
f=Landscape(forest)
f.reserve(12,7,5,6);f.reserve(7,19,8,5);f.reserve(25,8,5,5)
f.reserve(16,0,3,30)
for area in [(6,14,6,5),(11,17,6,2),(20,4,4,4),(19,7,5,3),(20,17,5,5),(19,19,3,3)]:clearing(f,*area)
# Irregular pool bank; retain the original encounter square and approach.
for x,y in [(27,7),(28,7),(29,7),(30,8),(30,9)]:
    forest.layers[0][y][x]=144;forest.walk[y][x]=False
shoreline(forest)
groves(f,[(4,3,4,3),(5,12,3,5),(7,26,5,3),(12,15,3,3),(23,2,4,3),(32,7,3,5),(30,19,4,5),(24,26,5,3)],240)
for x,y in [(24,7),(30,10),(31,12)]:rock_group(f,x,y,1)
# Keys sit among a colony of small white flowers, with a clear approach from path.
for x,y in [(13,8),(14,8),(15,8),(13,9),(14,10),(15,10),(13,11),(14,12)]:f.decal(WHITE,x,y)
for args in [(8,16,4,3),(22,5,3,3),(22,19,4,3)]:grass_patch(f,*args)
# A continuous canopy encloses the wood; overlapping crowns hide the map boundary.
for side in [0,33]:
    for y in range(0,28,2):f.plant(PINE if y%6 else ROUND,side,y,3,3,check=False)
for x in range(2,33,2):
    if not 14<=x<=18:f.plant(ROUND if x%6 else PINE,x,0,3,3,check=False)
    if not 14<=x<=20:f.plant(PINE if x%4 else ROUND,x,27,3,3,check=False)
f.finish()

# SHIOHAMA: a rock spine, sheltered garden and woodland thinning into village.
clear_nature(coast)
c=Landscape(coast)
# Preserve Pookie, robbery and seller walking routes explicitly, beyond event buffers.
c.reserve(31,34,7,7);c.reserve(44,31,7,10);c.reserve(47,23,3,13)
c.reserve(48,34,13,3);c.reserve(57,35,4,7);c.reserve(59,40,20,2)
c.reserve(52,42,5,11);c.reserve(34,38,14,4)
# Small garden and house approaches stay open; village margins become thickets.
c.reserve(28,30,10,4)
groves(c,[(47,7,4,5),(56,8,4,5),(60,19,3,4),(43,23,2,2),(52,29,3,3),(61,32,3,3)],160)
# Trees shelter the backs of houses; the exposed lighthouse has no tall trees.
for x,y in [(49,28),(59,24),(61,30),(50,38)]:c.plant(AUTUMN,x,y,2,2)
for x,y,s in [(25,29,3),(25,36,3),(35,25,3),(37,33,3),(30,41,3),(39,41,2),(44,43,2),(62,37,3),
              (27,26,2),(28,40,2),(38,29,2),(25,33,2),(38,38,2),(53,49,1),(57,48,2)]:rock_group(c,x,y,s,True)
# Tide-washed skerries continue the lighthouse's geology into the sea, not random clutter.
for x,y,s in [(22,31,2),(23,38,2),(27,44,2),(32,46,1),(38,44,1),(21,35,1)]:rock_group(c,x,y,s,True)
# Small planted beds sit on both sides of the tower, encircled by low stone edging.
for cells in [[(29,31),(29,32),(30,32),(30,33)],[(35,30),(35,31),(36,31),(35,32),(36,32),(36,33)]]:
    for x,y in cells:
        if coast.layers[1][y][x]==0:
            c.ground(x,y,.34);c.decal(WHITE if (x+y)%3==0 else FLOWER,x,y)
            # Low edging is visual only: garden interactions stay reachable.
            edging=Image.new('RGBA',(32,32));ed=ImageDraw.Draw(edging)
            for xx in [2,10,20]:
                ed.rectangle((xx,27,xx+7,30),fill=(103,112,103,255));ed.line((xx,27,xx+6,27),fill=(155,165,145,255),width=1)
            c.overlay.alpha_composite(edging,(x*32,y*32))
for x,y in [(29,34),(30,35),(36,34),(37,37)]:c.decal(art(6,0),x,y)
# Beach grass forms a narrow sheltered drift, away from the primary approach.
for x,y in [(49,39),(50,39),(51,39),(51,40),(55,38),(56,38),(61,41)]:c.decal(art(6,0),x,y)
scree(c,[(24,25,28,42),(28,24,38,28),(37,28,40,38),(27,41,38,44),(62,33,66,39)])
c.finish()
# Keep the original gate, avoiding accidental new entry through the tree line.
for y in range(23):
    for x in range(coast.w):coast.walk[y][x]=False
for x in (47,49):coast.walk[23][x]=False

# SOUTH ROAD: scrub woodland on the upper slopes, rocky tidal neck and lower bay.
clear_nature(road)
r=Landscape(road)
r.reserve(24,21,5,9);r.reserve(28,41,17,4);r.reserve(21,37,9,5)
for area in [(20,7,4,5),(19,10,4,3),(29,16,5,5),(27,18,3,2),(29,28,5,5),(27,30,3,2),(29,46,5,5),(27,48,3,2)]:clearing(r,*area)
groves(r,[(23,3,3,3),(32,9,4,3),(35,17,3,4),(19,32,3,3),(34,31,3,4),(19,47,3,4),(33,51,3,4),(26,60,5,3)],170)
for x,y,s in [(14,21,3),(20,22,2),(29,22,3),(35,22,3),(36,28,2),(14,40,2),(14,48,3),(18,56,2),(35,54,3),(29,64,2)]:rock_group(r,x,y,s,True)
for x,y,s in [(11,46,2),(12,51,1),(39,52,2),(40,28,1)]:rock_group(r,x,y,s,True)
for args in [(21,9,3,3),(31,18,3,3),(31,30,3,3),(31,48,3,3)]:grass_patch(r,*args)
for x,y in [(16,10),(16,11),(17,10),(22,38),(28,37)]:r.decal(WHITE,x,y)
scree(r,[(12,20,24,24),(29,21,39,24),(12,33,16,53),(35,53,39,60),(18,61,34,65)])
r.finish()

# DOCKS: a few tended courtyard plots, salt grass outside the working quays.
d=Landscape(docks)
dock_event_buffer={(xx,yy) for _,x,y,trigger,_ in docks.targets if trigger!=3 for yy in range(y-1,y+2) for xx in range(x-1,x+2)}
for x,y,w,h in [(26,10,10,5),(54,16,8,3),(12,22,7,2),(28,34,3,4),(58,33,4,6)]:
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            if docks.layers[1][yy][xx]==0 and (xx,yy) not in dock_event_buffer:
                docks.layers[0][yy][xx]=tile(1,0)
                d.protected.discard((xx,yy))
for x,y in [(27,10),(32,11),(59,16),(58,34)]:d.plant(AUTUMN,x,y,2,2)
for x,y in [(30,12),(33,13),(54,17),(56,17),(13,22),(14,22),(17,22),(28,35),(29,36),(60,37)]:d.decal(WHITE if x%2 else art(6,0),x,y)
for x,y,s in [(7,33,2),(11,38,2),(15,43,1),(61,40,2)]:rock_group(d,x,y,s,True)
d.finish()

# Water depth is legible without compromising the animated native sea or vast horizon.
# Only the story outdoor maps receive this cloned tileset; demo/astral remain untouched.
tilesets=loads((GAME/'Data/Tilesets.rxdata').read_bytes())
landscape_id=next((i for i,t in enumerate(tilesets) if t and t.attributes.get('@name')=='Tidebound Landscape'),len(tilesets))
ts=loads(writes(tilesets[1]));ts.attributes['@id']=landscape_id
ts.attributes['@name']='Tidebound Landscape';ts.attributes['@tileset_name']='TideboundLandscape'
for m in [coast,forest,road,docks]:m.tileset=landscape_id
# Keep the native wave animations, tint only blue water pixels (not shore rock).
for name,source,factors in [('Tidebound Shallows','Sea',(0.98,1.13,1.03)),('Tidebound Open Sea','Sea without shore',(.87,.98,1.0)),('Tidebound Deep Sea','Sea without shore',(.76,.87,.94))]:
    im=Image.open(GAME/'Graphics/Autotiles'/f'{source}.png').convert('RGBA')
    px=im.load()
    for y in range(im.height):
        for x in range(im.width):
            red,green,blue,a=px[x,y]
            if blue>red and blue>green: px[x,y]=(int(red*factors[0]),min(255,int(green*factors[1])),min(255,int(blue*factors[2])),a)
    im.save(GAME/'Graphics/Autotiles'/f'{name}.png')
ts.attributes['@autotile_names'][:3]=['Tidebound Shallows','Tidebound Open Sea','Tidebound Deep Sea']
for m in [coast,road,docks]:
    dist=[[999]*m.w for _ in range(m.h)];q=deque()
    for y in range(m.h):
        for x in range(m.w):
            v=m.layers[0][y][x]
            if v>=192 and v not in (tile(6,150),tile(6,151)):
                dist[y][x]=0;q.append((x,y))
    while q:
        x,y=q.popleft()
        for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=xx<m.w and 0<=yy<m.h and dist[yy][xx]>dist[y][x]+1:
                dist[yy][xx]=dist[y][x]+1;q.append((xx,yy))
    for y in range(m.h):
        for x in range(m.w):
            v=m.layers[0][y][x]
            if 48<=v<192:
                distance=dist[y][x]
                if distance<=2:m.layers[0][y][x]=48+(v%48 if v<96 else 0)
                elif distance<=7:m.layers[0][y][x]=96
                else:m.layers[0][y][x]=144
# Extend native tables and atlas deterministically. Base tile IDs and window pixels stay exact.
height=(_native.height//32+math.ceil(len(_tile_images)/8))*32
atlas=Image.new('RGBA',(256,height));atlas.alpha_composite(_native)
for i,(im,tag) in enumerate(_tile_images):atlas.alpha_composite(im,((i%8)*32,_native.height+(i//8)*32))
assert height<=16384, 'Keep landscape tileset within Mac 16K texture limit'
atlas.save(GAME/'Graphics/Tilesets/TideboundLandscape.png')
for key in ['@passages','@priorities','@terrain_tags']:
    data=ts.attributes[key]._dump();header=struct.unpack('<5i',data[:20]);values=list(struct.unpack('<'+'h'*header[4],data[20:]))
    values=values[:_base_count]+[0]*max(0,_base_count-len(values))
    values += [tag if key=='@terrain_tags' else 0 for im,tag in _tile_images]
    ts.attributes[key]=table(values,len(values))
if landscape_id==len(tilesets):tilesets.append(ts)
else:tilesets[landscape_id]=ts
(GAME/'Data/Tilesets.rxdata').write_bytes(writes(tilesets))
(DEV/'landscape_manifest.json').write_text(json.dumps({'revision':2,'maps':[102,103,108,112],'tileset_id':landscape_id,'baked_tiles':len(_tile_images),'trees_and_rocks':{str(p.m.id):len(p.sprites) for p in [c,f,r,d]}},indent=2))
