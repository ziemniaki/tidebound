"""Render a comparison sheet without touching the game sprites."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
r=Path(__file__).resolve().parent;p=r.parents[2]/'Graphics/Pokemon';g=r.parents[2]/'Graphics/Pokemon'
im=Image.new('RGB',(1120,730),'#1a2837');d=ImageDraw.Draw(im)
try:
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
 h=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27)
except OSError:f=h=ImageFont.load_default()
d.text((34,18),'Whyduck — exact Psyduck eyes / original hands (0.7.24)',fill='#ecf2f2',font=h)
for n,x,y,scale,label,src in [('Front/PSYDUCK.png',24,70,2,'PSYDUCK REFERENCE',g),('Front/WHYDUCK.png',402,70,2,'WHYDUCK FRONT',p),('Back/WHYDUCK.png',777,70,2,'WHYDUCK BACK',p),('Front shiny/WHYDUCK.png',60,467,1,'SHINY FRONT',p),('Back shiny/WHYDUCK.png',286,467,1,'SHINY BACK',p),('Icons/WHYDUCK.png',720,490,2,'ICON FRAMES',p)]:
 s=Image.open(src/n).convert('RGBA');s=s.resize((s.width*scale,s.height*scale),Image.Resampling.NEAREST)
 im.paste(s,(x,y),s);d.text((x,y+s.height+8),label,fill='#d4e0ef',font=f)
out=r/'whyduck_comparison.png';im.save(out);print(out)
