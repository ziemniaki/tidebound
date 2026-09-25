"""The inhabited storehouse: native furniture and small code-drawn clutter.
Executed inside lighthouse_interiors.py before its shared atlas is written.
Old map/event IDs and arrival (11,14) are retained.
"""
room(hideout,2,4,18,12)
window(hideout,3,2);window(hideout,17,2)
rug(hideout,14,4,4,4,(73,65,69,255))
prop(hideout,BED,3,4,2,3);prop(hideout,BED,6,4,2,3)
prop(hideout,SHELF,9,4,2,2);prop(hideout,CUPBOARD,11,3,2,2)
prop(hideout,SOFA,15,3,3,2);prop(hideout,SINK,18,4,2,2)
lamp(hideout,14,3);lamp(hideout,4,10)

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
prop(hideout,TABLE,6,14,2,2);prop(hideout,STOOL,8,14,1,1)
prop(hideout,CUPBOARD,18,14,2,2)
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
