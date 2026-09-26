"""Recovered southern pond source. Runs after demo_maps.py in rebuild_maps.
A compact road-only atlas leaves other maps and their tile IDs untouched.
"""
import math
for y in range(48,road.h):
    for x in range(road.w):
        road.layers[0][y][x]=96
        road.layers[1][y][x]=road.layers[2][y][x]=0
        road.walk[y][x]=False
road.polygon([(17,48),(37,48),(43,54),(44,65),(40,74),(34,77),(19,76),(12,71),(11,59),(14,53)],tile(1,0))
water=set()
for y in range(56,72):
    for x in range(19,38):
        if ((x-28)/8.3)**2+((y-63)/7.4)**2 < 1+0.075*math.sin(y*2+x):water.add((x,y))
island={(x,y) for y in range(61,64) for x in range(26,29)}-{(26,61),(28,61)}
water-=island
for x,y in water:road.layers[0][y][x]=48;road.walk[y][x]=False
for x,y in island:road.layers[0][y][x]=tile(2,27);road.walk[y][x]=True
coastal_shoreline(road)
for e in road.events.values():
    a=e.attributes
    if a['@name']=='Southern steps':
        a['@x'],a['@y']=26,53
        a['@pages'][0].attributes['@list']=script('pbMessage("A narrow trail bends down to a pond. Fishing lines hang motionless over the water.")')+[command(0)]
    elif a['@name']=='Wild:PSYDUCK:shoreduck':a['@x'],a['@y']=19,62
road.targets=[(e.attributes['@name'],e.attributes['@x'],e.attributes['@y'],e.attributes['@pages'][0].attributes['@trigger'],t[4]) for e,t in zip(road.events.values(),road.targets)]
for key,x,y,direction in [('toma',25,55,2),('ida',38,63,4),('renzo',29,72,8)]:
    eid=road.event('Pond fisher '+key,x,y,f'Tidebound::Pond.fisher(:{key})','trainer_FISHERMAN',blocks=True)
    road.events[eid].attributes['@pages'][0].attributes['@graphic'].attributes['@direction']=direction
road.event('Berry:ORANBERRY',20,54,'Tidebound::FieldDetails.berry(108, 20, 54, :ORANBERRY)','berrytree_ORANBERRY')
road.events[len(road.events)].attributes['@pages'][0].attributes['@graphic'].attributes['@direction']=8
road.event('Pond hidden cache',13,69,'Tidebound::Pond.hidden_item')
road.event('Pond obelisk (Surf)',27,61,'pbMessage("A narrow stone, cold beneath your hand. Water has worn the marks too shallow to read.")',blocks=True)
road.event('Old fishing basket',37,70,'pbMessage("A basket repaired with three different kinds of twine. A tiny fish has been carved into the handle.")')
p=Landscape(road)
p.reserve(24,48,5,8)
for box in [(17,55,3,14),(36,55,4,17),(21,72,16,2),(19,53,18,3)]:p.reserve(*box)
hidden=[(17,58),(16,58),(15,58),(15,59),(15,60),(14,60),(14,61),(14,62),(14,63),(14,64),(14,65),(14,66),(14,67),(14,68),(14,69),(13,69)]
for x,y in hidden:p.reserve(x,y,1,1)
for box in [(16,51,5,6),(38,65,4,5)]:clearing(p,*box)
groves(p,[(14,57,2,6),(15,70,3,4),(22,76,6,2),(37,75,5,2),(42,58,2,6),(40,51,4,3)],160)
for x,y in [(12,60),(12,62),(12,64),(12,66),(15,61),(15,63),(15,65),(15,67)]:
    p.plant(ROUND,x,y,2,2,check=False)
for x,y in hidden:
    road.walk[y][x]=True;road.layers[0][y][x]=tile(1,0)
    if (x+y)%5==0:p.decal(art(6,0),x,y)
for x,y,s in [(15,52,2),(40,54,2),(39,71,2),(19,72,2),(31,75,2)]:rock_group(p,x,y,s,True)
for x,y in [(20,58),(21,56),(34,56),(36,59),(35,68),(22,70),(20,66)]:
    if (x,y) not in water and (x,y) not in island:p.decal(art(6,0),x,y)
for args in [(18,53,3,3),(40,67,2,3)]:grass_patch(p,*args)
for x,y in [(23,54),(24,54),(36,72),(37,73)]:p.decal(WHITE,x,y)
for x,y in [(24,56),(25,56),(26,56)]:
    if (x,y) not in water:road.layers[0][y][x]=tile(6,150)
basket=Image.new('RGBA',(32,32));bd=ImageDraw.Draw(basket)
bd.ellipse((5,24,29,31),fill=(27,37,40,170))
bd.arc((8,4,25,23),180,360,fill=(126,113,78),width=2)
bd.polygon([(6,16),(27,16),(25,29),(9,29)],fill=(108,95,66),outline=(50,58,50))
for yy in [19,23,27]:bd.line((9,yy,25,yy),fill=(153,136,92),width=2)
p.decal(basket,37,70)
obelisk=Image.new('RGBA',(32,96));od=ImageDraw.Draw(obelisk)
od.ellipse((3,82,29,94),fill=(32,39,42,180))
od.polygon([(5,85),(9,11),(17,3),(24,12),(27,85)],fill=(124,135,139),outline=(50,64,70))
od.polygon([(17,3),(24,12),(27,85),(19,89),(17,20)],fill=(81,99,106))
od.line([(10,17),(9,77)],fill=(173,182,179),width=2)
od.line([(14,34),(19,38),(14,43),(18,47)],fill=(67,83,89),width=2)
od.line([(21,58),(17,65),(21,76)],fill=(52,72,79),width=2)
p.plant(obelisk,27,59,1,3,check=False,solid=False)
road.walk[61][27]=False
p.finish()
assert not any(336<=v<384 for layer in road.layers for row in layer for v in row)
for x,y in water:road.layers[0][y][x]=336+road.layers[0][y][x]%48
source=Image.open(GAME/'Graphics/Tilesets/TideboundLandscape.png').convert('RGBA')
used=sorted({v for layer in road.layers for row in layer for v in row if v>=384 and v!=391})
remap={v:392+i for i,v in enumerate(used)};remap[391]=391
atlas=Image.new('RGBA',(256,math.ceil((8+len(used))/8)*32));atlas.paste(art(0,0,8,1),(0,0))
for old,new in remap.items():
    if old==391:continue
    im=_tile_images[old-_base_count][0] if old>=_base_count else source.crop((((old-384)%8)*32,((old-384)//8)*32,((old-384)%8+1)*32,((old-384)//8+1)*32))
    atlas.alpha_composite(im,(((new-384)%8)*32,((new-384)//8)*32))
for layer in road.layers:
    for row in layer:
        for x,v in enumerate(row):
            if v>=384:row[x]=remap[v]
atlas.save(GAME/'Graphics/Tilesets/TideboundPond.png')
tilesets=loads((GAME/'Data/Tilesets.rxdata').read_bytes())
pid=next((i for i,t in enumerate(tilesets) if t and t.attributes.get('@name')=='Tidebound Pond'),len(tilesets))
ts=loads(writes(tilesets[road.tileset]));ts.attributes.update({'@id':pid,'@name':'Tidebound Pond','@tileset_name':'TideboundPond'})
ts.attributes['@autotile_names'][6]='Still water'
for key in ['@passages','@priorities','@terrain_tags']:ts.attributes[key]=table([0]*(392+len(used)),392+len(used))
if pid==len(tilesets):tilesets.append(ts)
else:tilesets[pid]=ts
road.tileset=pid;(GAME/'Data/Tilesets.rxdata').write_bytes(writes(tilesets))
(DEV/'pond_manifest.json').write_text(json.dumps({'map':108,'water':sorted(water),'island':sorted(island),'hidden_path':hidden,'grass_type':'PondGrass','duck':[19,62],'obelisk':[27,61]},indent=2)+'\n')
(DEV/'024_PondGeometry.rb').write_text('# Generated by pond_map.py.\nmodule Tidebound::PondGeometry\n  WATER = '+str(sorted(water)).replace('(','[').replace(')',']')+'.freeze\n  ISLAND = '+str(sorted(island)).replace('(','[').replace(')',']')+'.freeze\nend\n')
