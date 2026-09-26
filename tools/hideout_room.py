"""The inhabited storehouse: native furniture and small code-drawn clutter.
Executed inside lighthouse_interiors.py before its shared atlas is written.
Old map/event IDs and arrival (11,14) are retained.
"""
# Everything here is specific to the squat; shared lighthouse furniture stays intact.
def squat_asset(kind,w,h):
    im=Image.new('RGBA',(w*16,h*16));d=ImageDraw.Draw(im);W,H=im.size
    if kind=='mattress':
        d.rectangle((2,12,W-3,H-2),fill='#393c3b')
        for x in range(3,W-3,6):d.rectangle((x,12,x+3,H-1),fill='#606059')
        d.polygon([(4,9),(W-7,8),(W-4,H-6),(6,H-4),(3,H-12)],fill='#939489',outline='#444a48')
        d.rectangle((8,12,W-10,18),fill='#b0aea0')
        d.polygon([(4,23),(W-7,21),(W-5,H-6),(7,H-5)],fill='#676f6b')
        d.line((9,25,11,H-9,W-8,H-11),fill='#8b9286')
        d.rectangle((W-13,29,W-9,32),fill='#373e3c')
        d.rectangle((7,H-14,12,H-11),fill='#575d55')
    elif kind=='crates':
        for x,y,ww,hh in [(1,12,W-3,H-13),(4,2,W-10,13)]:
            d.rectangle((x,y,x+ww,y+hh),fill='#626661',outline='#2c3436')
            for xx in range(x+3,x+ww,7):d.line((xx,y+1,xx,y+hh-1),fill='#414c4d')
            d.line((x+1,y+hh-3,x+ww-1,y+3),fill='#919389',width=2)
        d.polygon([(8,3),(19,3),(17,8),(9,7)],fill='#222e31')
        d.rectangle((W-13,H-12,W-6,H-7),fill='#9b9a89')
    elif kind=='locker':
        d.rectangle((2,2,W-2,H-2),fill='#3f4a4b',outline='#262f33')
        d.rectangle((5,4,W-7,H-5),fill='#252f32')
        for y in [11,21]:d.rectangle((5,y,W-7,y+2),fill='#8b8d80')
        d.polygon([(W-11,3),(W-3,6),(W-5,H-3),(W-13,H-7)],fill='#626e69',outline='#2b3536')
        for x,y in [(8,8),(12,18),(7,26)]:d.rectangle((x,y,x+4,y+3),fill='#8a8877')
        d.line((W-8,8,W-10,24),fill='#a4a293')
    elif kind=='sofa':
        d.rectangle((4,H-7,W-5,H-2),fill='#282f33')
        d.rectangle((2,6,W-5,H-11),fill='#5c6663',outline='#282e32')
        d.rectangle((6,8,W-9,17),fill='#78817b')
        for x in [5,19,33]:
            d.rectangle((x,19,x+12,H-7),fill='#69726c',outline='#343e40')
            d.line((x+2,21,x+10,21),fill='#8c9183')
        d.rectangle((0,15,5,H-6),fill='#4f5b58')
        d.polygon([(W-7,18),(W-3,20),(W-2,H-5),(W-8,H-7)],fill='#424e4e')
        d.polygon([(9,9),(16,10),(13,14),(9,15)],fill='#30393b')
        d.line((10,11,14,12),fill='#b3ab94')
        d.line((24,23,27,25,26,28),fill='#252e32')
        d.rectangle((36,10,40,12),fill='#9b9c8b')
    elif kind=='trough':
        d.rectangle((3,H-9,W-3,H-5),fill='#505b57')
        d.rectangle((5,H-6,8,H-1),fill='#343e3e');d.rectangle((W-9,H-6,W-6,H-1),fill='#343e3e')
        d.polygon([(3,12),(W-3,14),(W-7,H-8),(6,H-7)],fill='#737f7b',outline='#313e41')
        d.ellipse((4,10,W-4,19),fill='#343f40',outline='#a0a498')
        for x in [9,16,22]:d.arc((x,12,x+6,18),0,300,fill='#bab5a1')
        d.line((6,21,7,H-8),fill='#404d46')
    elif kind=='bench':
        d.rectangle((4,17,11,H-1),fill='#4d5957');d.rectangle((W-12,17,W-5,H-1),fill='#4d5957')
        d.polygon([(1,9),(W-1,11),(W-3,20),(2,18)],fill='#85887c',outline='#303d40')
        d.line((4,13,W-5,15),fill='#4d5a58')
        d.line((W-10,11,W-8,17),fill='#28373b')
    elif kind=='bucket':
        d.polygon([(3,5),(W-3,5),(W-5,H-2),(5,H-2)],fill='#65736e',outline='#303e40')
        d.ellipse((3,2,W-3,8),fill='#939b8e',outline='#3b4a4c')
        d.line((5,9,W-5,9),fill='#414f4e')
    return im.resize((w*32,h*32),Image.Resampling.NEAREST)

room(hideout,2,4,18,12)
# Rough boards, not polished domestic parquet. Cold, low-contrast stains.
for y in range(4,16):
    for x in range(2,20):
        im=Image.new('RGBA',(32,32),(80+(x+y)%3*3,88+(x+y)%3*3,86+(x+y)%3*3,255));d=ImageDraw.Draw(im)
        d.line((0,15,31,15),fill='#343f42',width=2);d.line((0,31,31,31),fill='#343f42',width=2)
        seam=(x*7+y*11)%26+3;d.line((seam,0,seam,14),fill='#3f4a4b')
        d.line((2,4,22,4),fill='#646e68');d.line((8,25,28,25),fill='#444f50')
        if (x*13+y*7)%9<3:d.line((4,18,8,21,7,26,15,30),fill='#303f43',width=2)
        if (x+y)%4==0:d.ellipse((9,7,27,24),fill='#46564f')
        surface(hideout,im,x,y,False,0)
# Bare damp walls with peeling limewash and exposed timber.
for x in range(2,20):
    im=Image.new('RGBA',(32,64),'#606b68');d=ImageDraw.Draw(im)
    d.rectangle((0,0,31,6),fill='#313d40');d.rectangle((0,55,31,63),fill='#29383b')
    d.polygon([(0,48),(6,34),(12,46),(18,38),(25,49),(31,41),(31,56),(0,56)],fill='#43564f')
    d.line((2,7,2,54),fill='#424d4c',width=2)
    if x%3==0:
        d.polygon([(9,12),(24,10),(21,18),(25,23),(14,28),(11,20)],fill='#92978a')
        d.line((16,12,17,22,21,26),fill='#37484c',width=2)
    surface(hideout,im,x,2)
# Boarded windows admit only thin, dead-blue slits.
for x in [3,17]:
    im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
    d.rectangle((2,5,60,55),fill='#29393f',outline='#7a847c',width=2)
    for y in [11,26,41]:
        d.rectangle((6,y,57,y+10),fill='#4e5e5e',outline='#27393e',width=2)
        d.line((8,y+12,56,y+12),fill='#869a94',width=2)
        d.rectangle((11,y+4,12,y+5),fill='#b2b1a0')
    surface(hideout,im,x,2)
# A torn sackcloth mat, without decorative edging.
mat=Image.new('RGBA',(128,128));d=ImageDraw.Draw(mat)
d.polygon([(8,8),(116,13),(119,112),(102,118),(18,113),(10,100)],fill='#414c4c')
for y in range(18,112,10):d.line((15,y,109,y+3),fill='#505b55',width=2)
d.polygon([(40,10),(47,30),(51,11)],fill=(0,0,0,0))
surface(hideout,mat,14,4)
prop(hideout,squat_asset('mattress',2,3),3,4,2,3)
prop(hideout,squat_asset('mattress',2,3),6,4,2,3)
prop(hideout,squat_asset('crates',2,2),9,4,2,2)
prop(hideout,squat_asset('locker',2,2),11,3,2,2)
prop(hideout,squat_asset('sofa',3,2),15,3,3,2)
prop(hideout,squat_asset('trough',2,2),18,4,2,2)

def mess(kind,seed):
    # One tile, authored at 16px and enlarged exactly 2x like native furniture.
    im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);r=random.Random(seed)
    if kind=='box':
        d.polygon([(1,5),(7,2),(14,5),(14,14),(1,14)],fill='#80694e',outline='#373c3c')
        d.polygon([(1,5),(7,8),(14,5),(9,3),(5,4)],fill='#aa9270')
        d.line((7,8,7,14),fill='#4c4640');d.line((2,11,5,12),fill='#b1a184')
        d.rectangle((8,9,12,12),fill='#c2b89e');d.line((9,10,11,11),fill='#716e63')
    elif kind=='laundry':
        d.polygon([(0,13),(2,8),(5,9),(6,4),(11,3),(14,9),(15,14)],fill='#3a454b')
        d.polygon([(2,12),(4,8),(8,9),(10,5),(13,10),(13,13)],fill='#777c78')
        d.line((5,10,7,12,11,11),fill='#b1aaa0')
        d.rectangle((1,5,4,8),fill='#9a876c')
    else:
        d.ellipse((0,6,15,15),fill='#3b3735')
        for _ in range(5):
            x=r.randrange(1,11);y=r.randrange(5,12)
            d.polygon([(x,y),(x+4,y-2),(x+5,y+2),(x+1,y+3)],fill=r.choice(['#b4a689','#7b7766','#8d7359']))
        d.rectangle((10,4,13,10),fill='#425b51');d.rectangle((11,2,12,5),fill='#6f8071')
        d.ellipse((2,10,8,13),fill='#aea288',outline='#635f53')
    return im.resize((32,32),Image.Resampling.NEAREST)

# Two solid, visually continuous banks make a short west/east zigzag.
# Sparse dropped papers in the lanes remain passable; piled objects never do.
heaps=[(x,12) for x in range(5,20)]+[(x,8) for x in list(range(2,14))+list(range(16,20))]
for i,(x,y) in enumerate(heaps):surface(hideout,mess(['box','laundry','rubbish'][i%3],i),x,y,True)
for i,(x,y) in enumerate([(5,11),(6,11),(10,11),(17,11),(19,13),(18,13),(6,9),(7,9),(11,9),(2,7),(19,7)]):
    surface(hideout,mess(['laundry','box','rubbish'][i%3],40+i),x,y,True)
prop(hideout,squat_asset('bench',2,2),6,14,2,2);prop(hideout,squat_asset('bucket',1,1),8,14,1,1)
prop(hideout,squat_asset('crates',2,2),18,14,2,2)
surface(hideout,mess('rubbish',113),6,14,False,2)
surface(hideout,mess('laundry',114),3,5,False,2)
surface(hideout,mess('laundry',115),6,5,False,2)
for i,(x,y) in enumerate([(18,10),(6,10),(10,10),(3,13),(15,14),(18,14),(9,7),(5,7)]):
    surface(hideout,mess('rubbish',90+i),x,y,False)
for i,(x,y) in enumerate([(4,11),(8,11),(12,10),(16,11),(4,14),(10,15),(14,15),(17,14),(8,7)]):
    paper=Image.new('RGBA',(32,32));p=ImageDraw.Draw(paper)
    p.polygon([(6,20),(17,16),(24,22),(13,27)],fill='#a59b83',outline='#615c50')
    p.line((10,21,17,20),fill='#736e63',width=2)
    surface(hideout,paper,x,y,False)

# A wooden rune console: glass, brass studs and a corded handpiece, no electricity.
device=Image.new('RGBA',(64,32));d=ImageDraw.Draw(device)
d.rectangle((3,4,60,29),fill='#54483e',outline='#252c30',width=2)
d.rectangle((9,7,48,24),fill='#879b89',outline='#b9ae8b',width=2)
d.rectangle((13,10,44,21),fill='#233c40')
for x in [18,28,38]:d.line((x,18,x+3,12,x+5,17),fill='#8daea0',width=2)
d.ellipse((51,10,57,16),fill='#b3a16b');d.line((19,30,28,30,30,25),fill='#aaa48b',width=2)
surface(hideout,device,15,6,True)

# Retain native head/torso and fold the legs forward into a seated silhouette.
src=Image.open(GAME/'Graphics/Characters/trainer_CAMPER.png').convert('RGBA')
fw,fh=src.width//4,src.height//4
seat=Image.new('RGBA',(fw,fh));seat.alpha_composite(src.crop((0,0,fw,33)),(0,5))
seat.alpha_composite(src.crop((2,33,fw-2,40)),(2,35))
sd=ImageDraw.Draw(seat);sd.rectangle((10,32,21,35),fill='#584d43');sd.rectangle((12,32,13,33),fill='#b4ad8b')
sheet=Image.new('RGBA',src.size)
for yy in range(4):
    for xx in range(4):sheet.alpha_composite(seat,(xx*fw,yy*fh))
sheet.save(GAME/'Graphics/Characters/Tidebound_Ivo_Seated.png')

placements={
    'Abyss runner':(13,7,'Tidebound::Hideout.guard','trainer_YOUNGSTER'),
    'Necklace thief':(16,4,'Tidebound::Hideout.boss','Tidebound_Ivo_Seated'),
    'Abyss packer':(18,11,'Tidebound::NeighborQuest.packer','trainer_BUGCATCHER'),
    'Abyss lookout':(3,9,'Tidebound::NeighborQuest.lookout','trainer_YOUNGSTER'),
    'Dispatch slip':(12,4,'Tidebound::Hideout.cache',''),
    'Arrival':(2,15,'Tidebound::Hideout.arrival',''),
}
clutter_spots=[(5,12),(7,12),(9,12),(11,12),(13,12),(15,12),(17,12),(19,12),(7,8),(10,8)]
for e in hideout.events.values():
    a=e.attributes;name=a['@name'];p=a['@pages'][0].attributes
    if name=='Crate goods':
        x,y=clutter_spots.pop(0);a.update({'@name':'Clutter','@x':x,'@y':y})
        p['@graphic'].attributes.update({'@character_name':'','@opacity':255})
        p['@list']=script('Tidebound::Hideout.clutter')+[command(0)]
    elif name in placements:
        x,y,code,char=placements[name];a.update({'@x':x,'@y':y})
        p['@graphic'].attributes['@character_name']=char
        p['@list']=script(code)+[command(0)]
        p['@direction_fix']=(name=='Necklace thief')
        p['@through']=not bool(char)
        if char:hideout.walk[y][x]=False
hideout.targets=[(a['@name'],a['@x'],a['@y'],a['@pages'][0].attributes['@trigger'],not hideout.walk[a['@y']][a['@x']]) for a in [e.attributes for e in hideout.events.values()]]
for x in [14,15]:hideout.event('Sofa approach',x,9,'Tidebound::Hideout.approach',trigger=1)
hideout.event('Rune console',15,6,'Tidebound::Hideout.console')
hideout.event('Unwashed dishes',19,5,'pbMessage("Bowls in the washbasin. Someone has washed one spoon and given up.")')
hideout.rect(11,16,1,1,itile(floor_tile()),walk=True)

# Clone every squat tile through a restrained cold palette. Never recolour the
# shared atlas in place: the lighthouse and all other interiors stay unchanged.
squat_clones={}
for layer in hideout.layers:
    for row in layer:
        for xx,t in enumerate(row):
            if t<interior_base:continue
            if t not in squat_clones:
                im=interior_tiles[t-interior_base].copy()
                pixels=[]
                for r,g,b,a in im.getdata():
                    l=int(r*.30+g*.55+b*.15)
                    pixels.append((int(l*.76+r*.15),int(l*.82+g*.15),int(l*.87+b*.15),a))
                im.putdata(pixels);squat_clones[t]=itile(im)
            row[xx]=squat_clones[t]
