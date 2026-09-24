from pathlib import Path
import ast, copy, json, re, struct, zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import RubyObject, UserDef, Symbol
from PIL import Image, ImageDraw, ImageEnhance

DEV = Path(__file__).resolve().parent
GAME = DEV.parent
ROOT = GAME
DEV.mkdir(exist_ok=True)
PATTERNS=[[27, 28, 33, 34], [5, 28, 33, 34], [27, 6, 33, 34], [5, 6, 33, 34], [27, 28, 33, 12], [5, 28, 33, 12], [27, 6, 33, 12], [5, 6, 33, 12], [27, 28, 11, 34], [5, 28, 11, 34], [27, 6, 11, 34], [5, 6, 11, 34], [27, 28, 11, 12], [5, 28, 11, 12], [27, 6, 11, 12], [5, 6, 11, 12], [25, 26, 31, 32], [25, 6, 31, 32], [25, 26, 31, 12], [25, 6, 31, 12], [15, 16, 21, 22], [15, 16, 21, 12], [15, 16, 11, 22], [15, 16, 11, 12], [29, 30, 35, 36], [29, 30, 11, 36], [5, 30, 35, 36], [5, 30, 11, 36], [39, 40, 45, 46], [5, 40, 45, 46], [39, 6, 45, 46], [5, 6, 45, 46], [25, 30, 31, 36], [15, 16, 45, 46], [13, 14, 19, 20], [13, 14, 19, 12], [17, 18, 23, 24], [17, 18, 11, 24], [41, 42, 47, 48], [5, 42, 47, 48], [37, 38, 43, 44], [37, 6, 43, 44], [13, 18, 19, 24], [13, 14, 43, 44], [37, 42, 43, 48], [17, 18, 47, 48], [13, 18, 43, 48], [1, 2, 7, 8]]
NEIGHBORS=[46, 44, 46, 44, 43, 41, 43, 40, 46, 44, 46, 44, 43, 41, 43, 40, 42, 32, 42, 32, 35, 19, 35, 18, 42, 32, 42, 32, 34, 17, 34, 16, 46, 44, 46, 44, 43, 41, 43, 40, 46, 44, 46, 44, 43, 41, 43, 40, 42, 32, 42, 32, 35, 19, 35, 18, 42, 32, 42, 32, 34, 17, 34, 16, 45, 39, 45, 39, 33, 31, 33, 29, 45, 39, 45, 39, 33, 31, 33, 29, 37, 27, 37, 27, 23, 15, 23, 13, 37, 27, 37, 27, 22, 11, 22, 9, 45, 39, 45, 39, 33, 31, 33, 29, 45, 39, 45, 39, 33, 31, 33, 29, 36, 26, 36, 26, 21, 7, 21, 5, 36, 26, 36, 26, 20, 3, 20, 1, 46, 44, 46, 44, 43, 41, 43, 40, 46, 44, 46, 44, 43, 41, 43, 40, 42, 32, 42, 32, 35, 19, 35, 18, 42, 32, 42, 32, 34, 17, 34, 16, 46, 44, 46, 44, 43, 41, 43, 40, 46, 44, 46, 44, 43, 41, 43, 40, 42, 32, 42, 32, 35, 19, 35, 18, 42, 32, 42, 32, 34, 17, 34, 16, 45, 38, 45, 38, 33, 30, 33, 28, 45, 38, 45, 38, 33, 30, 33, 28, 37, 25, 37, 25, 23, 14, 23, 12, 37, 25, 37, 25, 22, 10, 22, 8, 45, 38, 45, 38, 33, 30, 33, 28, 45, 38, 45, 38, 33, 30, 33, 28, 36, 24, 36, 24, 21, 6, 21, 4, 36, 24, 36, 24, 20, 2, 20, 0]

def obj(class_name, **values):
    return RubyObject(class_name, {'@'+k:v for k,v in values.items()})

def table(values, x, y=1, z=1):
    t=UserDef('Table')
    t._load(struct.pack('<5i',3 if z>1 else 2 if y>1 else 1,x,y,z,len(values))+struct.pack('<'+'h'*len(values),*values))
    return t

def command(code, *parameters, indent=0):
    return obj('RPG::EventCommand',code=code,indent=indent,parameters=list(parameters))

def script(code):
    lines=code.splitlines()
    return [command(355 if i==0 else 655,line) for i,line in enumerate(lines)]

def page(code, charset='', trigger=0, opacity=255, move=0):
    condition=obj('RPG::Event::Page::Condition',switch1_valid=False,switch2_valid=False,variable_valid=False,self_switch_valid=False,switch1_id=1,switch2_id=1,variable_id=1,variable_value=0,self_switch_ch='A')
    graphic=obj('RPG::Event::Page::Graphic',tile_id=0,character_name=charset,character_hue=0,direction=2,pattern=0,opacity=opacity,blend_type=0)
    route=obj('RPG::MoveRoute',repeat=True,skippable=True,list=[obj('RPG::MoveCommand',code=0,parameters=[])])
    return obj('RPG::Event::Page',condition=condition,graphic=graphic,move_type=move,move_speed=2,move_frequency=2,move_route=route,walk_anime=True,step_anime=False,direction_fix=False,through=(charset==''),always_on_top=False,trigger=trigger,list=script(code)+[command(0)])

def tile(x,y): return 384+x+y*8

class Map:
    def __init__(self,id,name,w,h,tileset,floor=0):
        self.id,self.name,self.w,self.h,self.tileset=id,name,w,h,tileset
        self.layers=[[[0]*w for _ in range(h)] for _ in range(3)]
        self.layers[0]=[[floor]*w for _ in range(h)]
        self.walk=[[False]*w for _ in range(h)]
        self.events={};self.targets=[]
    def rect(self,x,y,w,h,t,z=0,walk=None):
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                self.layers[z][yy][xx]=t
                if walk is not None:self.walk[yy][xx]=walk
    def stamp(self,sx,sy,w,h,x,y,walk=False,z=1):
        for yy in range(h):
            for xx in range(w):
                self.layers[z][y+yy][x+xx]=tile(sx+xx,sy+yy)
                if walk is not None:self.walk[y+yy][x+xx]=walk
    def event(self,name,x,y,code,charset='',trigger=0,opacity=255,move=0,blocks=False):
        eid=len(self.events)+1
        self.events[eid]=obj('RPG::Event',id=eid,name=name,x=x,y=y,pages=[page(code,charset,trigger,opacity,move)])
        if blocks:self.walk[y][x]=False
        self.targets.append((name,x,y,trigger,blocks))
        return eid
    def door(self,x,y,destination,dx,dy,d=2):
        self.walk[y][x]=True
        code=f'Tidebound::Opening.travel_coast({dx}, {dy}, {d})' if destination==102 else f'Tidebound::Opening.travel({destination}, {dx}, {dy}, {d})'
        self.event('Door',x,y,code,trigger=1)
    def save(self):
        flat=[v for layer in self.layers for row in layer for v in row]
        m=obj('RPG::Map',tileset_id=self.tileset,width=self.w,height=self.h,autoplay_bgm=True,bgm=obj('RPG::AudioFile',name='Tidebound Shore' if self.id==102 else 'Tidebound Stillness',volume=80,pitch=100),autoplay_bgs=False,bgs=obj('RPG::AudioFile',name='',volume=100,pitch=100),encounter_list=[],encounter_step=30,data=table(flat,self.w,self.h,3),events=self.events)
        (GAME/f'Data/Map{self.id:03}.rxdata').write_bytes(writes(m))
    def render(self):
        ts=loads((GAME/'Data/Tilesets.rxdata').read_bytes())[self.tileset].attributes
        atlas=Image.open(GAME/'Graphics/Tilesets'/f"{ts['@tileset_name']}.png").convert('RGBA')
        canvas=Image.new('RGBA',(self.w*32,self.h*32),(5,9,20,255))
        autos={}
        for layer in self.layers:
            for y,row in enumerate(layer):
                for x,t in enumerate(row):
                    if t>=384:
                        c=(t-384)%8;r=(t-384)//8
                        image=atlas.crop((c*32,r*32,c*32+32,r*32+32))
                    elif t>=48:
                        key=t//48-1
                        if key not in autos:autos[key]=Image.open(GAME/'Graphics/Autotiles'/f"{ts['@autotile_names'][key]}.png").convert('RGBA')
                        auto=autos[key]
                        # Variant zero is the seamless centre, four 16px chunks.
                        image=Image.new('RGBA',(32,32))
                        for i,chunk in enumerate(PATTERNS[t%48]):
                            cx=((chunk-1)%6)*16;cy=((chunk-1)//6)*16
                            image.paste(auto.crop((cx,cy,cx+16,cy+16)),((i%2)*16,(i//2)*16))
                    else:continue
                    if 48<=t<384 and auto.height==32:image=auto.crop((0,0,32,32))
                    canvas.alpha_composite(image,(x*32,y*32))
        for e in self.events.values():
            p=e.attributes;g=p['@pages'][0].attributes['@graphic'].attributes
            if g['@character_name'] and g['@opacity']:
                im=Image.open(GAME/'Graphics/Characters'/f"{g['@character_name']}.png").convert('RGBA')
                w,h=im.width//4,im.height//4
                im=im.crop((w,0,w*2,h));canvas.alpha_composite(im,(p['@x']*32+(32-w)//2,p['@y']*32+32-h))
        if self.id in (102,103,108,112):
            # Approximate the runtime Tone in the offline preview, without editing assets.
            rgb=canvas.convert('RGB');grey=rgb.convert('L').convert('RGB')
            rgb=Image.blend(rgb,grey,150/255)
            rgb=Image.merge('RGB',[band.point(lambda v,shift=shift:max(0,v+shift)) for band,shift in zip(rgb.split(),[-80,-74,-48])])
            canvas=rgb.convert('RGBA')
        elif self.id==105:
            canvas=Image.alpha_composite(canvas,Image.new('RGBA',canvas.size,(10,19,49,155)))
        canvas.convert('RGB').save(DEV/f'map_{self.id}_preview.png')


class CoastMap(Map):
    OX, OY = 24, 20
    def rect(self,x,y,*args,**kw):super().rect(x+self.OX,y+self.OY,*args,**kw)
    def stamp(self,sx,sy,w,h,x,y,**kw):super().stamp(sx,sy,w,h,x+self.OX,y+self.OY,**kw)
    def event(self,name,x,y,*args,**kw):return super().event(name,x+self.OX,y+self.OY,*args,**kw)
    def door(self,x,y,destination,dx,dy,d=2):
        self.walk[y+self.OY][x+self.OX]=True
        self.event('Door',x,y,f'Tidebound::Opening.travel({destination}, {dx}, {dy}, {d})',trigger=1)
    def polygon(self,points,t,walk=True):
        im=Image.new('1',(self.w,self.h));ImageDraw.Draw(im).polygon([(x+self.OX,y+self.OY) for x,y in points],fill=1)
        for yy in range(self.h):
            for xx in range(self.w):
                if im.getpixel((xx,yy)):self.layers[0][yy][xx]=t;self.walk[yy][xx]=walk
    def path(self,x,y,w,h,stone=False):
        base=26 if stone else 12
        for yy in range(h):
            for xx in range(w):
                self.rect(x+xx,y+yy,1,1,tile(1 if xx==0 else 3 if xx==w-1 else 2,base+(0 if yy==0 else 2 if yy==h-1 else 1)),walk=True)

# New maps have distinct IDs so the original demo remains untouched but inaccessible.
home=Map(101,'The Keeper\'s House',20,16,3)
home.rect(2,3,16,11,tile(4,78),walk=True)
home.rect(2,2,16,2,tile(1,13),walk=False)
home.stamp(0,0,4,2,2,1);home.stamp(0,0,4,2,6,1);home.stamp(0,0,4,2,10,1);home.stamp(0,0,4,2,14,1)
home.stamp(0,151,2,2,3,4)
home.stamp(0,140,3,2,12,4) # domestic furnishings
home.stamp(6,212,2,2,8,7)
home.event('Mother',12,7,'Tidebound::Opening.mother','NPC 11',blocks=True)
home.event('Book',4,10,'Tidebound::Opening.journal')
home.stamp(0,140,3,2,3,8)
home.event('Opening',2,13,'Tidebound::Opening.home_arrival',trigger=3)
home.event('House:NATU',6,5,'Tidebound::Opening.house_pet(:NATU)','Pokemon 01',opacity=0)
home.event('House:MAKUHITA',10,9,'Tidebound::Opening.house_pet(:MAKUHITA)','Pokemon 01',opacity=0)
home.event('House:POOCHYENA',13,11,'Tidebound::Opening.house_pet(:POOCHYENA)','Pokemon 01',opacity=0)
home.event('Crate',10,10,'pbMessage("Bottles wrapped in straw. Maku carries them as carefully as he can.")','Pokemon 01',opacity=0)
home.event('Crate spare',12,10,'pbMessage("One of the boxes Maku is helping Mother put away.")','Pokemon 01',opacity=0)
home.stamp(1,237,2,2,6,3,walk=True)
home.door(6,3,107,8,10,8)
# This autorun erases itself; persistent story flag prevents repetition on revisit.
home.rect(10,14,1,1,tile(4,78),walk=True)
home.door(10,14,102,8,16)
home.stamp(1,237,2,2,16,3,walk=True)
home.door(17,3,104,6,9)

coast=CoastMap(102,'Shiohama',108,88,1,96)
# The ocean continues far past every reachable camera position.
coast.polygon([(3,7),(7,5),(12,5),(14,8),(16,12),(14,16),(14,19),(11,22),(6,22),(2,19),(1,13)],tile(2,27))
coast.polygon([(4,8),(11,7),(13,10),(13,16),(11,20),(5,20),(3,16)],tile(1,0))
coast.polygon([(20,-18),(38,-18),(39,7),(41,12),(39,17),(37,22),(33,25),(25,25),(21,22),(19,16)],tile(1,0))
coast.polygon([(22,18),(29,17),(36,19),(37,22),(33,25),(25,25),(21,22)],192)
coast.polygon([(11,18),(15,18),(17,19),(21,18),(23,20),(20,22),(16,21),(13,22),(11,20)],tile(2,27))
coast.path(7,14,4,7,True);coast.path(10,18,7,3,True);coast.path(16,19,8,3,True)
coast.path(23,3,3,19);coast.path(24,14,13,3);coast.path(33,15,4,7)
# Weathered timber projects above water; it is not a dirt peninsula.
coast.rect(35,20,20,1,tile(6,150),walk=True)
coast.rect(35,21,20,1,tile(6,151),walk=True)
coast.rect(35,22,20,1,tile(6,152),z=1,walk=False)
coast.rect(52,19,3,1,tile(6,150),walk=True)
coast.rect(55,20,1,2,tile(7,151),z=1,walk=False)
coast.stamp(5,444,3,8,7,7)
coast.stamp(0,227,4,4,20,8);coast.stamp(0,227,4,4,28,7);coast.stamp(4,228,4,4,34,7)
coast.door(8,15,101,10,12,8)
coast.walk[31][45]=True
coast.event('Shop door',21,11,'Tidebound::Opening.shop_door',trigger=1)
coast.event('Seller outside',22,12,'Tidebound::Opening.outside_seller','NPC 10')
coast.event('Pookie outside',11,16,'Tidebound::Opening.pookie','Pokemon 01',opacity=0)
coast.event('Oil shop sign',23,12,'pbMessage("LAMP OIL. Please ask the seller for assistance.\nA small bottle hangs beside the lettering.")')
coast.event('Empty house',29,11,'pbMessage("The door has swollen in its frame. Nobody answers.")')
coast.event('Seated neighbour',31,18,'pbMessage("Young as ever, aren\'t you? I wish I knew your secret.")\npbMessage("Your mother still lights the tower every night. I used to complain that it shone through my curtains.")','NPC 14',blocks=True)
coast.event('Pier',54,20,'Tidebound::Opening.pier',trigger=1)
coast.event('Lapras',56,23,'')
coast.event('Tide bell',18,20,'pbMessage("A bell with no clapper. Salt has filled the inscription.")')
coast.event('Forest path',24,3,'Tidebound::Opening.forest_gate',trigger=1)

for x in range(20,39,3):
    for y in range(-18,3,3):coast.stamp(0,55,3,3,x,y)
for x,y in [(3,7),(12,10),(18,6),(25,7),(32,3),(36,12)]:coast.stamp(3,67,3,3,x,y)
for x,y in [(1,10),(1,17),(11,5),(13,13),(6,21),(16,22),(20,24),(37,16)]:coast.stamp(0,108,3,3,x,y)
for i,(x,y) in enumerate([(4,16),(5,19),(12,17),(14,20),(19,22),(22,23),(26,24),(32,24),(35,23),(38,20),(3,20),(11,21)]):
    sx,sy=[(0,140),(2,140),(0,142),(3,142),(2,143)][i%5];coast.stamp(sx,sy,1,1,x,y)
for x,y in [(5,11),(5,12),(6,12),(10,16),(11,17),(11,12),(12,12),(26,18),(27,18),(30,16),(31,16),(23,17)]:coast.rect(x,y,1,1,240,z=1)
for x,y in [(4,12),(6,17),(12,19),(20,17),(27,16),(32,18),(34,23)]:coast.rect(x,y,1,1,tile(6,0),z=1)
# Only the authored entrance crosses into the northern forest.
for x in range(20,40):coast.walk[22][x+24]=False
for x in (23,25):coast.walk[23][x+24]=False
coast.event('Headland flowers',11,12,'pbMessage("Late flowers, sheltered by a ring of flat stones.\nSomeone has tied the weakest stems to little sticks.")')
coast.event('Sea glass',29,24,'pbMessage("Green glass, worn smooth by the water.\nFor a moment, it catches the light.")')
coast.event('Coast lamp:home',5,16,'pbMessage("Mother lights this little lamp before dusk.\nSo you can always find the path home.")')
coast.event('Coast lamp:pier',52,19,'pbMessage("A little oil lamp. Someone still tends it, even with the boats gone.")')
coast.event('Mooring rope',54,21,'pbMessage("An old mooring rope disappears beneath the boards.")')

# Preserve all existing coast event IDs. Extend a small southern rocky path.
coast.polygon([(28,23),(32,23),(33,28),(32,32),(28,32),(27,28)],tile(2,27))
coast.path(29,24,3,8,True)
coast.event('South path',30,31,'Tidebound::NeighborQuest.south_gate',trigger=1)
coast.event('Robbery youth one',21,11,'','trainer_YOUNGSTER',opacity=0)
coast.event('Robbery youth two',21,12,'','trainer_CAMPER',opacity=0)
coast.event('Coast road sign',31,29,'pbMessage("COAST ROAD - SOUTH. The lettering has been repainted around the rusted nails.")')

forest=Map(103,'The Listening Wood',36,30,1,tile(1,0))
forest.rect(3,3,30,24,tile(1,0),walk=True)
forest.rect(16,3,3,24,tile(2,13),walk=True)
forest.rect(7,20,12,3,tile(2,13),walk=True)
forest.rect(17,10,12,3,tile(2,13),walk=True)
for x in range(1,34,3):
    for y in [0,26]:
        if x in [16,19] and y==26:continue
        forest.stamp(0,55,3,3,x,y)
for x,y in [(2,5),(2,11),(2,17),(6,5),(7,10),(10,5),(24,3),(28,6),(30,13),(25,17),(25,23),(7,24),(11,13)]:
    forest.stamp(0,55,3,3,x,y)
forest.event('Ninja',9,20,'Tidebound::Opening.fire','NPC 01',blocks=True)
forest.event('Fire',10,21,'Tidebound::Opening.fire',blocks=True)
forest.event('Wild:NATU',21,13,'Tidebound::Opening.bird','Pokemon 01',opacity=0,move=1)
forest.event('Dark pool',27,10,'Tidebound::Opening.pool',trigger=1)
forest.rect(26,8,4,2,144,walk=False)
forest.event('Shop keys',14,11,'Tidebound::Opening.forest_keys','Pokemon 01',opacity=0)
forest.event('White flowers',14,9,'pbMessage("Small white flowers. They have survived the cold.")')
forest.event('Northern way',17,3,'Tidebound::Opening.northern_way',trigger=1)
forest.door(17,27,102,24,5)
for x,y in [(12,21),(14,7),(14,8),(14,10),(22,15),(23,15),(24,15)]:forest.rect(x,y,1,1,tile(7,3),z=1)

lantern=Map(104,'The Lantern Room',14,14,3)
lantern.rect(3,3,8,8,tile(1,81),walk=True)
lantern.rect(3,2,8,1,tile(1,13),walk=False)
lantern.event('Main lamp',6,5,'Tidebound::Opening.main_lamp',blocks=True)
lantern.event('Downward lamp',9,8,'pbMessage("A smaller lamp points straight down into the water.\nThe glass is warm.")',blocks=True)
lantern.rect(6,11,1,1,tile(1,81),walk=True)
lantern.door(6,11,101,16,4)

astral=Map(105,'Beyond the Shore',32,26,1,tile(1,0))
astral.rect(3,3,26,20,tile(1,0),walk=True)
astral.rect(14,4,3,19,tile(2,13),walk=True)
for x,y in [(1,1),(6,1),(22,1),(27,1),(1,8),(1,16),(27,8),(27,17),(5,20),(22,20)]:astral.stamp(0,55,3,3,x,y)
for i,(x,y) in enumerate([(9,7),(21,8),(7,15),(23,16),(13,5),(18,19)]):
    astral.event(f'Spirit:{i}',x,y,f'Tidebound::Opening.spirit({i})','Pokemon 01',opacity=0,move=1)
astral.event('Guide',15,20,'Tidebound::Opening.guide','NPC 01',opacity=120)
astral.event('Return',15,22,'Tidebound::Opening.return_from_astral',trigger=1)
astral.event('Ashes',5,12,'Tidebound::Opening.memorial')
astral.event('Arrival',3,22,'Tidebound::Opening.astral_arrival',trigger=3)

shop=Map(106,'The Oil Shop',16,14,3)
shop.rect(2,3,12,9,tile(4,78),walk=True)
shop.rect(2,2,12,2,tile(1,13),walk=False)
for x in (2,6,10):shop.stamp(0,0,4,2,x,1)
shop.stamp(3,140,3,3,3,4)
shop.stamp(0,140,2,3,10,4)
shop.stamp(6,212,2,2,10,8)
shop.event('Oil seller',7,5,'Tidebound::Opening.oil_seller','NPC 10',blocks=True)
shop.event('Bottles',4,7,'pbMessage("Old glass, washed and washed again. Each bottle has a different name scratched underneath.")')
shop.event('Old ledger',11,10,'pbMessage("The ledger lies open to a page with very few names.\nYour mother\'s is underlined.")')
shop.rect(8,12,1,1,tile(4,78),walk=True)
shop.door(8,12,102,21,12,2)

bedroom=Map(107,"Your Room",16,14,3)
bedroom.rect(2,4,12,8,tile(4,78),walk=True)
bedroom.rect(2,2,12,2,tile(1,13),walk=False)
for x in (2,6,10):bedroom.stamp(0,0,4,2,x,1)
bedroom.stamp(0,151,2,2,3,4)
bedroom.stamp(0,140,3,2,10,4)
bedroom.event('Room:NATU',7,8,'Tidebound::Opening.bedroom_pet','Pokemon 01',opacity=0)
bedroom.event('Mother visiting',8,11,'pbMessage("Mother: Downstairs, love.")','NPC 11',opacity=0)
bedroom.event('Book',4,9,'Tidebound::Opening.journal')
bedroom.event('Opening',2,11,'Tidebound::Opening.begin_story',trigger=3)
bedroom.rect(8,12,1,1,tile(4,78),walk=True)
bedroom.event('Bedroom exit',8,12,'Tidebound::Opening.bedroom_exit',trigger=1)
# The short pursuit route is separate from the future dock city.
class RoadMap(CoastMap):
    OX, OY = 0, 0
    door = Map.door
road=RoadMap(108,'The South Coast Road',56,68,1,96)
road.polygon([(17,1),(25,1),(25,6),(34,6),(38,11),(40,19),(38,23),(36,27),(40,33),(41,45),(38,55),(33,64),(20,64),(16,59),(13,50),(15,40),(14,32),(17,27),(16,20),(13,16),(14,8)],tile(1,0))
road.polygon([(14,8),(16,8),(17,16),(19,19),(18,23),(16,20),(13,16)],192)
road.polygon([(15,31),(17,32),(17,40),(16,49),(19,58),(17,59),(13,50)],192)
road.rect(17,4,3,15,tile(2,27),walk=True)
road.rect(18,17,10,3,tile(2,13),walk=True)
road.rect(25,17,3,35,tile(2,13),walk=True)
road.rect(25,42,12,3,tile(2,13),walk=True)
road.rect(25,50,3,9,tile(2,27),walk=True)
# A narrow timber crossing visibly explains the first thief's chokepoint.
road.rect(13,24,29,2,96,walk=False)
road.rect(25,24,3,2,tile(6,150),walk=True)
for x,y in [(14,22),(20,22),(28,22),(34,22),(37,14),(32,13),(36,31),(17,33),(18,48),(36,51)]:road.stamp(0,108,3,3,x,y)
for x,y in [(20,1),(23,4),(28,5),(32,7),(35,9),(36,18),(17,28),(20,38),(36,46),(34,56),(20,61),(24,62),(29,62)]:road.stamp(0,55,3,3,x,y)
for x,y in [(16,10),(20,14),(22,16),(30,28),(32,35),(23,46),(30,54)]:road.rect(x,y,1,1,240,z=1)
road.stamp(0,227,4,4,34,38)
road.rect(35,41,1,1,tile(2,13),walk=True)
road.door(18,4,102,30,30,8)
road.event('Wild:NATU:shorebird',20,10,'Tidebound::NeighborQuest.wild(:shorebird)','Pokemon 01',opacity=0,move=1)
road.event('Wild:ZIGZAGOON:shoreforager',22,18,'Tidebound::NeighborQuest.wild(:shoreforager)','Pokemon 01',opacity=0,move=1)
road.event('Road thief',26,26,'Tidebound::NeighborQuest.first_thief','trainer_YOUNGSTER')
for x in range(25,28):road.event('Thief crossing',x,24,'Tidebound::NeighborQuest.first_thief',trigger=1)
road.event('Running thief',31,43,'Tidebound::NeighborQuest.witness_hideout','trainer_CAMPER',opacity=0)
for y in range(42,45):road.event('Storehouse approach',29,y,'Tidebound::NeighborQuest.witness_hideout',trigger=1)
road.event('Storehouse door',35,41,'Tidebound::NeighborQuest.hideout_door',trigger=1)
road.event('Road traveller',23,39,'Tidebound::NeighborQuest.rest','NPC 01',blocks=True)
road.event('Fire',24,40,'Tidebound::NeighborQuest.rest',blocks=True)
road.event('Southern steps',26,58,'pbMessage("The lower steps have washed away. New planks lie ready beside them. The coast road continues towards the distant docks.")')
road.event('Torn wrapping',31,34,'pbMessage("Straw packing, and an empty oil-shop bag. They came this way.")')
road.event('Shore flowers',16,10,'pbMessage("Small flowers turn away from the salt wind.")')

hideout=Map(109,'The Old Storehouse',22,18,3)
hideout.rect(2,3,18,13,tile(4,78),walk=True)
hideout.rect(2,2,18,2,tile(1,13),walk=False)
for x in (2,6,10,14,18):hideout.stamp(0,0,4,2,x,1)
for x,y in [(4,5),(5,5),(6,5),(4,6),(5,6),(16,5),(17,5),(17,6),(7,13),(8,13)]:
    hideout.event('Crate goods',x,y,'pbMessage("Oil tins, mended nets, a good blanket. Nothing here matches.")','Pokemon 01',opacity=0,blocks=True)
hideout.event('Abyss runner',11,9,'Tidebound::NeighborQuest.runner','trainer_BURGLAR',blocks=True)
hideout.event('Necklace thief',14,7,'Tidebound::NeighborQuest.second_thief','trainer_CAMPER',blocks=True)
hideout.event('Abyss packer',17,11,'Tidebound::NeighborQuest.packer','trainer_BUGCATCHER',blocks=True)
hideout.event('Abyss lookout',5,10,'Tidebound::NeighborQuest.lookout','trainer_YOUNGSTER',blocks=True)
hideout.event('Dispatch slip',16,8,'pbMessage("One box: nets. Two boxes: assorted. Three boxes: also assorted. A second hand has underlined: COUNT IT PROPERLY.")')
hideout.event('Arrival',2,15,'Tidebound::NeighborQuest.overhear',trigger=3)
hideout.rect(11,16,1,1,tile(4,78),walk=True)
hideout.door(11,16,108,35,43,2)
# Small additive scenery; original event IDs and travel coordinates are retained.
for m, plots in [(forest, [(6,16,4,3),(20,5,3,4),(20,18,4,3)]),
                 (road, [(20,7,3,3),(29,17,4,3),(29,29,4,3),(29,47,4,3)])]:
    for x,y,w,h in plots:
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                if m.walk[yy][xx] and m.layers[1][yy][xx]==0:
                    m.rect(xx,yy,1,1,tile(7,0),z=1)
for m,x,y,item in [(coast,12,18,'ORANBERRY'),(forest,12,19,'ORANBERRY'),
                   (forest,22,9,'ORANBERRY'),(road,21,16,'ORANBERRY'),
                   (road,28,38,'SITRUSBERRY')]:
    eid=m.event('Berry:'+item,x,y,f'Tidebound::FieldDetails.berry({m.id}, {x}, {y}, :{item})',
                'berrytree_'+item,blocks=False)
    m.events[eid].attributes['@pages'][0].attributes['@graphic'].attributes['@direction']=8
coast.event('Coast lamp:shop',24,12,'pbMessage("A sheltered flame warms the shopfront.")')
road.event('Coast lamp:storehouse',33,42,'pbMessage("The wick has been trimmed recently.")')
exec((DEV/'vault_maps.py').read_text())
MAPS=[home,coast,forest,lantern,astral,shop,bedroom,road,hideout]+[basement,vault,docks,museum]

def shoreline(m):
    old=copy.deepcopy(m.layers[0])
    def water(x,y):
        v=old[max(0,min(m.h-1,y))][max(0,min(m.w-1,x))]
        return 48<=v<192 or v==tile(1,151)
    for y in range(m.h):
        for x in range(m.w):
            if not 48<=old[y][x]<192:continue
            mask=sum(1<<i for i,(dx,dy) in enumerate([(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]) if water(x+dx,y+dy))
            m.layers[0][y][x]=48+NEIGHBORS[mask]
def coastal_shoreline(m):
    old=copy.deepcopy(m.layers[0])
    def land(x,y):
        if not (0<=x<m.w and 0<=y<m.h):return False
        v=old[y][x]
        return v==192 or (v>=384 and v not in [tile(6,150),tile(6,151)])
    offsets=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
    for y in range(m.h):
        for x in range(m.w):
            v=old[y][x]
            if v==192:
                mask=sum(1<<i for i,(dx,dy) in enumerate(offsets) if land(x+dx,y+dy))
                m.layers[0][y][x]=192+NEIGHBORS[mask]
            elif 48<=v<192:
                if any(0<=y+dy<m.h and 0<=x+dx<m.w and old[y+dy][x+dx]==192 for dx,dy in offsets):m.layers[0][y][x]=96
                else:
                    mask=sum(1<<i for i,(dx,dy) in enumerate(offsets) if not land(x+dx,y+dy))
                    m.layers[0][y][x]=48+NEIGHBORS[mask]
coastal_shoreline(coast)
shoreline(forest)
coastal_shoreline(road)
coastal_shoreline(docks)
exec((DEV/'landscape.py').read_text())
exec((DEV/'lighthouse_interiors.py').read_text())
exec((DEV/'demo_maps.py').read_text())

def build():
    for m in MAPS:m.save()
    system=loads((GAME/'Data/System.rxdata').read_bytes())
    system.attributes.update({'@start_map_id':115,'@start_x':7,'@start_y':8,'@magic_number':26092301})
    (GAME/'Data/System.rxdata').write_bytes(writes(system))
    infos=loads((GAME/'Data/MapInfos.rxdata').read_bytes())
    metadata=loads((GAME/'Data/map_metadata.dat').read_bytes())
    template=metadata[1]
    for m in MAPS:
        infos[m.id]=obj('RPG::MapInfo',name=m.name,parent_id=0,order=m.id,expanded=True,scroll_x=320,scroll_y=240)
        md=loads(writes(template));md.attributes.update({'@id':m.id,'@real_name':m.name,'@announce_location':True,'@outdoor_map':False,'@battle_background':'field' if m.id!=105 else 'cave1','@battle_environment':Symbol('Forest') if m.id==103 else Symbol('Cave') if m.id==105 else Symbol('None')})
        metadata[m.id]=md
    (GAME/'Data/MapInfos.rxdata').write_bytes(writes(infos))
    (GAME/'Data/map_metadata.dat').write_bytes(writes(metadata))
    collisions={str(m.id):[''.join('1' if b else '0' for b in row) for row in m.walk] for m in MAPS}
    (DEV/'collisions.json').write_text(json.dumps(collisions,indent=2))
    ruby='module Tidebound\n  MAP_PASSAGES = {\n'+''.join(f'    {k} => {json.dumps(v)},\n' for k,v in collisions.items())+'  }\nend\n'
    (DEV/'003_MapPassages.rb').write_text(ruby)
    for m in MAPS:m.render()
    (DEV/'map_manifest.json').write_text(json.dumps([{'id':m.id,'name':m.name,'width':m.w,'height':m.h,'targets':m.targets} for m in MAPS],indent=2))
    print('Built',len(MAPS),'native maps and collision masks')

if __name__=='__main__':build()
