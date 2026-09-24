"""Small one-time opening puzzle; invoked before lighthouse atlas serialization."""
maze=Map(114,'Your Room',29,25,27)
# Opaque void also occludes the engine's below-map water-reflection sprite.
void=itile(Image.new('RGBA',(32,32),(0,0,0,255)))
maze.layers[0]=[[void]*maze.w for _ in range(maze.h)]
block=Image.new('RGBA',(32,32));bd=ImageDraw.Draw(block)
bd.rectangle((0,0,31,31),fill=(55,56,57,255));bd.rectangle((2,2,29,9),fill=(128,119,95,255));bd.line((2,2,29,2),fill=(169,154,116,255),width=2);bd.rectangle((3,12,28,27),fill=(45,53,58,255))
for x,c in [(5,(94,113,119,255)),(11,(130,105,98,255)),(17,(132,128,104,255)),(23,(102,117,109,255))]:
 bd.rectangle((x,14,x+3,25),fill=c);bd.rectangle((x,16,x+3,17),fill=(174,164,133,255))
bd.rectangle((1,28,30,31),fill=(80,76,65,255))
for x,y,w,h in [(2,14,9,9),(2,2,17,11),(21,2,7,8)]:
 for yy in range(y,y+h):
  for xx in range(x,x+w):maze.layers[0][yy][xx]=itile(floor_tile());surface(maze,block,xx,yy)
walk={(x,y) for x in range(3,10) for y in range(15,22)}|{(x,y) for x in range(22,27) for y in range(3,9)}
for x0,y0,x1,y1 in [(3,11,17,11),(3,3,3,11),(3,3,17,3),(9,3,9,7),(3,7,17,7),(17,3,17,11),(9,5,17,5),(11,5,11,11),(16,3,16,5),(4,10,4,11)]:
 walk.update((x,y) for x in range(x0,x1+1) for y in range(y0,y1+1))
for x,y in walk:maze.layers[1][y][x]=0;maze.walk[y][x]=True
window(maze,5,12);window(maze,23,0);prop(maze,BED,3,15,2,3);prop(maze,BOOK,3,19,1,1);rug(maze,23,4,3,3,(78,83,109,255))
pushers={(7,20):8,(3,9):8,(3,3):6,(9,3):2,(9,7):6,(17,7):2,(17,5):8}
stops={(7,16),(17,11),(17,3)}
warps={(9,16):(4,11),(4,10):(9,17),(7,11):(5,20),(16,3):(22,5),(22,6):(16,4)}
def marker(kind,value=0):
 im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);d.rectangle((3,3,28,28),fill=(69,76,94,255),outline=(149,149,149,255),width=2)
 if kind=='arrow':
  d.polygon([(16,7),(24,17),(19,17),(19,24),(13,24),(13,17),(8,17)],fill=(221,203,143,255));im=im.rotate({8:0,6:-90,2:180,4:90}[value],resample=Image.Resampling.NEAREST)
 elif kind=='stop':
  d.polygon([(16,7),(25,16),(16,25),(7,16)],fill=(177,193,182,255));d.polygon([(16,11),(21,16),(16,21),(11,16)],fill=(68,81,83,255))
 else:
  c=[(166,194,182,255),(193,166,202,255),(190,151,144,255)][value];d.ellipse((7,7,24,24),outline=c,width=2);d.ellipse((11,11,20,20),outline=c,width=2)
  for x in [8,23]:d.rectangle((x,4,x+1,6),fill=c)
 return im
for (x,y),direction in pushers.items():
 surface(maze,marker('arrow',direction),x,y);maze.event('Slide tile',x,y,f'Tidebound::PsychicMaze.slide({direction})',trigger=1)
for x,y in stops:surface(maze,marker('stop'),x,y)
for (x,y),(dx,dy) in warps.items():
 color=0 if (x,y) in [(9,16),(4,10)] else 2 if (x,y)==(7,11) else 1
 surface(maze,marker('warp',color),x,y);maze.event('Round patch',x,y,f'Tidebound::PsychicMaze.warp({dx}, {dy})',trigger=1)
maze.event('Room:NATU',24,5,'Tidebound::PsychicMaze.finish','Pokemon 01',opacity=0)
maze.event('Game rules',3,19,'Tidebound::PsychicMaze.rules');maze.event('Opening',2,23,'Tidebound::PsychicMaze.arrival',trigger=3)
MAPS.append(maze)
manifest={'map':114,'start':[5,20],'goal':[24,5],'pushers':[[x,y,d] for (x,y),d in pushers.items()],'stops':[list(p) for p in sorted(stops)],'warps':[[x,y,dx,dy] for (x,y),(dx,dy) in warps.items()]}
(DEV/'maze_manifest.json').write_text(json.dumps(manifest,indent=2))
p=DEV/'018_PsychicMaze.rb';s=p.read_text();start=s.index('  # GENERATED PUZZLE DATA');end=s.index('  # END GENERATED PUZZLE DATA')
ruby='  # GENERATED PUZZLE DATA\n  MAP = 114\n  START = [5,20].freeze\n'
ruby+='  PUSHERS = {'+','.join(f'[{x},{y}]=>{d}' for (x,y),d in pushers.items())+'}.freeze\n'
ruby+='  STOPS = '+str([list(p) for p in sorted(stops)])+'.freeze\n'
ruby+='  WARPS = {'+','.join(f'[{x},{y}]=>[{dx},{dy}]' for (x,y),(dx,dy) in warps.items())+'}.freeze\n'
p.write_text(s[:start]+ruby+s[end:])
