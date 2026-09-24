"""Extract Psyduck eye artwork; only relocate its original pupil pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parent
source_root=r.parents[2]/'Graphics/Pokemon'
for folder,tag in [('Front',''),('Front shiny','_shiny')]:
 im=Image.open(source_root/folder/'PSYDUCK.png').convert('RGBA').resize((80,80),Image.Resampling.NEAREST)
 for name,polygon,box,old,new in [
  ('left',[(29,25),(31,25),(33,26),(35,27),(35,29),(34,30),(32,31),(29,31),(27,30),(26,29),(27,27)],(26,24,37,33),(31,27),(30,29)),
  ('right',[(41,25),(45,25),(47,26),(48,27),(48,29),(46,30),(40,31),(38,30),(37,28),(38,26)],(37,24,49,33),(42,26),(41,29)),
 ]:
  mask=Image.new('L',(80,80));ImageDraw.Draw(mask).polygon(polygon,fill=255)
  cut=im.copy();cut.putalpha(Image.composite(im.getchannel('A'),Image.new('L',(80,80)),mask))
  cut.putpixel(old,(255,255,255,255))
  cut.putpixel(new,(16,16,16,255))
  cut.crop(box).save(r/'pieces'/('psyduck_eye_'+name+tag+'.png'))
print('Copied Psyduck eye pixels and moved pupils down-left.')
