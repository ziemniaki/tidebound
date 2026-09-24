"""Mechanical conversion of approved artwork to Essentials pixel assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
A=Path(__file__).resolve().parent;G=A.parents[2]
COLOURS=[(12,30,49),(34,58,80),(71,104,137),(98,146,183),
 (144,189,215),(181,222,244),(211,239,252),(249,253,255),
 (247,241,202),(220,213,170),(175,170,125),(105,105,71),
 (255,219,53),(213,170,33),(225,241,246),(125,165,188)]
palette=Image.new('P',(1,1));palette.putpalette([c for rgb in COLOURS for c in rgb]+[0]*(768-48))
def reduce(source,max_size):
 im=Image.open(source).convert('RGBA')
 alpha=im.getchannel('A').point(lambda a:255 if a>=128 else 0)
 im.putalpha(alpha);im=im.crop(alpha.getbbox())
 ratio=min(max_size[0]/im.width,max_size[1]/im.height)
 im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.NEAREST)
 alpha=im.getchannel('A')
 rgb=Image.new('RGB',im.size,COLOURS[0]);rgb.paste(im,mask=alpha)
 out=rgb.quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA');out.putalpha(alpha)
 return out
for face,source in [('Front','approved_front.png'),('Back','rear_source.png')]:
 small=reduce(A/source,(72,72))
 small.save(A/(face.lower()+'_logical.png'))
 double=small.resize((small.width*2,small.height*2),Image.Resampling.NEAREST)
 frame=Image.new('RGBA',(160,160));frame.paste(double,((160-double.width)//2,8 if face=='Front' else 160-double.height))
 frame.save(A/(face.lower()+'.png'))
 for directory in [face,face+' shiny']:frame.save(G/f'Graphics/Pokemon/{directory}/FROSTCOON_EVOLUTION.png')
small=reduce(A/'approved_front.png',(28,28))
icon=small.resize((small.width*2,small.height*2),Image.Resampling.NEAREST)
sheet=Image.new('RGBA',(128,64))
for x,y in [(0,6),(64,4)]:sheet.paste(icon,(x+(64-icon.width)//2,y))
sheet.save(A/'icon.png');sheet.save(G/'Graphics/Pokemon/Icons/FROSTCOON_EVOLUTION.png')
# Review at nearest-neighbour zoom, with ordinary-resolution assets underneath.
preview=Image.new('RGB',(1040,640),(43,51,65));draw=ImageDraw.Draw(preview)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
for x,face in [(10,'front'),(360,'back')]:
 im=Image.open(A/(face+'.png'))
 draw.text((x+10,18),face.upper(),fill='#d6e7ec',font=font)
 enlarged=im.resize((320,320),Image.Resampling.NEAREST);preview.paste(enlarged,(x,60),enlarged)
 preview.paste(im,(x+80,430),im)
draw.text((735,18),'PARTY ICON',fill='#d6e7ec',font=font)
for i in range(2):
 im=sheet.crop((64*i,0,64*i+64,64));big=im.resize((128,128),Image.Resampling.NEAREST)
 preview.paste(big,(728+144*i,150),big);preview.paste(im,(764+144*i,465),im)
draw.text((22,607),'Top: enlarged for inspection. Bottom: game asset dimensions.',fill='#a9beca',font=font)
preview.save(A/'preview.png')
# Party preview uses precisely the two engine icon frames.
frames=[]
for i in range(2):
 im=sheet.crop((64*i,0,64*i+64,64)).resize((192,192),Image.Resampling.NEAREST)
 bg=Image.new('RGBA',im.size,(43,51,65,255));bg.alpha_composite(im);frames.append(bg.convert('RGB'))
frames[0].save(A/'icon_preview.gif',save_all=True,append_images=frames[1:],duration=320,loop=0)
print('Front/back 160x160, <=16 colours, 128x64 icon; alpha is binary.')

# Keep registered species art synchronized after future approved sprite edits.
if (G/'PBS/pokemon_nivalora.txt').exists():
 import shutil
 for directory in ['Front','Back','Front shiny','Back shiny','Icons']:
  shutil.copy2(G/f'Graphics/Pokemon/{directory}/FROSTCOON_EVOLUTION.png',G/f'Graphics/Pokemon/{directory}/NIVALORA.png')
