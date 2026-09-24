"""Preview the committed pixel sprites at readable sizes (nearest-neighbour)."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
G=Path(__file__).resolve().parents[3]
P=G/'Graphics/Pokemon'
out=Path(__file__).resolve().parent/'whyduck_preview.png'
im=Image.new('RGB',(820,745),(20,28,41));d=ImageDraw.Draw(im)
try:
 regular=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
 head=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27)
except OSError:regular=head=ImageFont.load_default()
d.text((38,20),'Whyduck  /  Tidebound regional evolution',font=head,fill=(238,242,244))
d.text((40,59),'Water / Psychic    |    hand-drawn Gen 3 pixel art',font=regular,fill=(177,202,216))
for folder,x,y,scale,label in [('Front',48,96,2,'FRONT'),('Back',420,96,2,'BACK'),
                              ('Front shiny',70,476,1,'SHINY FRONT'),
                              ('Back shiny',287,476,1,'SHINY BACK')]:
 s=Image.open(P/folder/'WHYDUCK.png').convert('RGBA');box=(x-8,y-8,x+s.width*scale+8,y+s.height*scale+8)
 d.rounded_rectangle(box,radius=11,fill=(42,56,72),outline=(100,128,147),width=2)
 im.paste(s.resize((s.width*scale,s.height*scale),Image.Resampling.NEAREST),(x,y),s.resize((s.width*scale,s.height*scale),Image.Resampling.NEAREST))
 d.text((x,y+s.height*scale+9),label,font=regular,fill=(206,222,236))
icon=Image.open(P/'Icons/WHYDUCK.png').convert('RGBA').resize((256,128),Image.Resampling.NEAREST)
d.rounded_rectangle((498,476,784,666),radius=11,fill=(42,56,72),outline=(100,128,147),width=2)
im.paste(icon,(510,496),icon)
d.text((520,680),'TWO ICON FRAMES',font=regular,fill=(206,222,236))
im.save(out)
print(out)
