"""Second false bedroom: a larger, fractured room with a readable winding route."""
folded=Map(116,'Your Room, Again',30,26,27)
room(folded,2,4,26,20)
window(folded,5,2);window(folded,15,2);window(folded,21,2)
rug(folded,5,20,6,3,(83,66,98,255))
rug(folded,17,10,5,2,(67,95,96,255))
rug(folded,21,4,6,3,(95,65,83,255))
# Three rows of repeated cupboards narrow the room into a winding route.
# Every opening is at least three tiles wide, never a hidden passage.
for y,gap in [(18,range(24,28)),(13,range(4,8)),(8,range(20,24))]:
 for x in range(2,28,2):
  if x not in gap:prop(folded,SHELF,x,y,2,2)
# Whole furniture silhouettes remain readable even where their surfaces fracture.
prop(folded,BED,24,4,2,3)
prop(folded,BED,3,15,2,3)
prop(folded,PLANT,26,20,1,2)
prop(folded,STOOL,8,16,1,1)
prop(folded,CUPBOARD,12,4,2,2)
for x,y,kind in [(12,22,'tooth'),(26,15,'snow'),(9,11,'cradle'),(19,6,'voice')]:
 prop(folded,BOOK,x,y,1,1)
 folded.event('Folded reading '+kind,x,y,'Tidebound::DreamRoom.folded_reading(:'+kind+')')
 lamp(folded,x+1,y)
for x,y,kind in [(4,17,'empty_bed'),(8,16,'chair'),(26,21,'plant'),(12,5,'cupboard')]:
 folded.event('Folded '+kind,x,y,'Tidebound::DreamRoom.folded_reading(:'+kind+')')
# Only externally approachable bed tiles have interaction events.
for x,y in [(24,4),(25,4),(24,5),(25,5),(24,6),(25,6)]:
 folded.event('Folded bed',x,y,'Tidebound::DreamRoom.folded_bed')
stairs(folded,6,22,False)
for x in [6,7]:folded.event('Folded stairs',x,24,'Tidebound::DreamRoom.folded_reset',trigger=1)
folded.event('Opening',2,23,'Tidebound::DreamRoom.folded_arrival',trigger=3)
# Recolour and fracture this map's tile copies, leaving all existing rooms intact.
folded_tiles={}
def folded_tile(t):
 if t==0:return black
 if t in folded_tiles:return folded_tiles[t]
 im=interior_tiles[t-interior_base].copy() if t>=interior_base else native((t-384)%8,(t-384)//8)
 pix=im.load()
 for yy in range(32):
  for xx in range(32):
   r,g,b,a=pix[xx,yy];l=(r+g+b)//3
   pix[xx,yy]=(min(255,int(l*.78)+10),min(255,int(l*.76)+5),min(255,int(l*.98)+12),a)
 folded_tiles[t]=itile(im);return folded_tiles[t]
for layer in range(3):
 for y in range(folded.h):
  for x in range(folded.w):
   t=folded.layers[layer][y][x]
   if t:folded.layers[layer][y][x]=folded_tile(t)
   elif layer==0:folded.layers[layer][y][x]=black
# Thin displaced strips and rune-like stitches; topology never depends on these marks.
for x,y in [(4,20),(12,20),(18,16),(24,13),(5,10),(13,10),(17,6),(22,5),(6,15),(14,8)]:
 for layer in [0,1]:
  t=folded.layers[layer][y][x]
  if t<interior_base:continue
  im=interior_tiles[t-interior_base].copy();band=im.crop((0,12,28,16));im.paste(band,(4,12))
  dr=ImageDraw.Draw(im);dr.line((6,22,15,22,15,28),fill=(91,133,132,170),width=2)
  folded.layers[layer][y][x]=itile(im)
# Whole bookcase silhouettes, with displaced writing-height strips inside them.
for x,y in [(8,18),(18,13),(10,8),(24,8)]:
 patch=Image.new('RGBA',(64,64))
 for yy in range(2):
  for xx in range(2):patch.alpha_composite(interior_tiles[folded.layers[1][y+yy][x+xx]-interior_base],(xx*32,yy*32))
 old=patch.copy();dr=ImageDraw.Draw(patch)
 for top,bottom,offset in [(16,23,6),(33,39,-4),(48,52,3)]:
  dr.rectangle((2,top,61,bottom),fill=(37,33,52,255))
  part=old.crop((8,top,56,bottom+1));patch.alpha_composite(part,(8+offset,top))
  dr.line((8,top-1,56,top-1),fill=(99,146,148,230),width=1)
 for yy in range(2):
  for xx in range(2):folded.layers[1][y+yy][x+xx]=itile(patch.crop((xx*32,yy*32,xx*32+32,yy*32+32)))
# Impossible seams cross the planks but do not obscure navigable floor.
for y,start,end in [(21,13,24),(16,12,23),(11,3,16),(6,7,16)]:
 for x in range(start,end):
  t=folded.layers[0][y][x];im=interior_tiles[t-interior_base].copy();dr=ImageDraw.Draw(im)
  h=14+(x%3)*2;dr.line((0,h,15,h,15,h+2,31,h+2),fill=(43,38,58,255),width=3)
  dr.line((0,h-1,13,h-1),fill=(105,132,138,255),width=1)
  folded.layers[0][y][x]=itile(im)
MAPS.append(folded)
(DEV/'folded_manifest.json').write_text(json.dumps({'map':116,'start':[7,22],'bed':[24,5],'bed_approach':[25,7],'clues':[[12,22],[26,15],[9,11],[19,6]],'reset_tiles':[[6,24],[7,24]],'gaps':[[25,18],[5,13],[22,8]],'events':len(folded.events)},indent=2))
