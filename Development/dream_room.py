"""The false ordinary bedroom, before the one-time psychic maze."""
dream=Map(115,'Your Room',16,14,27)
room(dream,2,4,12,8)
# Opaque darkness suppresses native water-reflection sprites outside the room.
black=itile(Image.new('RGBA',(32,32),(0,0,0,255)))
for y,row in enumerate(dream.layers[0]):
 for x,t in enumerate(row):
  if t==0:dream.layers[0][y][x]=black
window(dream,6,2)
prop(dream,BED,3,4,2,3)
# Books and timber: no electronic technology in the region.
prop(dream,SHELF,8,4,2,2)
prop(dream,STOOL,8,6,1,1);prop(dream,SHELF,11,4,2,2)
rug(dream,5,7,5,3,(77,91,114,255));prop(dream,BOOK,3,8,1,1);lamp(dream,3,9)
prop(dream,PLANT,12,9,1,2)
clock=Image.new('RGBA',(32,32));cd=ImageDraw.Draw(clock)
cd.ellipse((5,3,26,26),fill=(69,71,75,255),outline=(179,158,110,255),width=2)
cd.ellipse((8,6,23,22),fill=(206,202,174,255));cd.line((16,8,16,15,21,15),fill=(69,76,80,255),width=2)
surface(dream,clock,13,3)
stairs(dream,7,10,False)
# Every piece of furniture is inspectable; multi-tile props share one handler.
def inspect_prop(label,points,method):
 for x,y in points:dream.event('Dream '+label,x,y,'Tidebound::DreamRoom.'+method)
inspect_prop('bed',[(x,y) for x in [3,4] for y in [4,5,6]],'bed')
inspect_prop('book cupboard',[(x,y) for x in [8,9] for y in [4,5]],'cupboard')
inspect_prop('chair',[(8,6)],'inspect_object(:chair)')
inspect_prop('shelf',[(x,y) for x in [11,12] for y in [4,5]],'inspect_object(:shelf)')
inspect_prop('window',[(6,3),(7,3)],'inspect_object(:window)')
inspect_prop('clock',[(13,3)],'inspect_object(:clock)')
inspect_prop('book',[(3,8)],'inspect_object(:book)')
inspect_prop('lamp',[(3,9)],'inspect_object(:lamp)')
inspect_prop('plant',[(12,9),(12,10)],'inspect_object(:plant)')
inspect_prop('rug',[(5,9)],'inspect_object(:rug)')
for x in [7,8]:dream.event('Dream exit',x,12,'Tidebound::DreamRoom.exit_loop',trigger=1)
dream.event('Room:NATU',10,8,'Tidebound::DreamRoom.wick','Pokemon 01',opacity=0)
dream.event('Opening',2,11,'Tidebound::DreamRoom.arrival',trigger=3)
MAPS.append(dream)
(DEV/'dream_manifest.json').write_text(json.dumps({'map':115,'start':[7,8],'wick':[10,8],'loop_tiles':[[7,12],[8,12]],'object_names':['bed','cupboard','chair','shelf','window','clock','book','lamp','plant','rug'],'events':len(dream.events)},indent=2))
