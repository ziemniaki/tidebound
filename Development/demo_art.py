"""Small hand-drawn sailing vessels and salt-weathered wooden cottages for Demo 1.
Built on a half-resolution pixel grid; no generated or upscaled smooth artwork.
"""
from PIL import Image,ImageDraw
from pathlib import Path
G=Path(__file__).resolve().parent.parent
OUT=G/'Graphics/Pictures/Tidebound';OUT.mkdir(exist_ok=True,parents=True)

def ship(name,trim,sail):
    im=Image.new('RGBA',(160,128));d=ImageDraw.Draw(im)
    ink=(47,48,59);wood=(126,99,77);light=(164,134,93);deck=(183,151,110)
    # Low reflection, keel and heavy hull; prow to the right.
    for y,w in [(115,130),(119,113),(122,88)]:
        d.line((16+(130-w)//2,y,16+(130+w)//2,y),fill=(93,124,151,135),width=1)
    hull=[(10,87),(128,84),(154,78),(141,100),(123,115),(37,115),(18,103)]
    d.polygon(hull,fill=ink)
    d.polygon([(13,87),(127,87),(148,83),(136,98),(120,111),(38,111),(21,101)],fill=wood)
    d.polygon([(13,87),(127,84),(151,79),(143,90),(125,100),(35,101),(19,94)],fill=deck,outline=ink)
    for y in [90,94,98]:d.line((25,y,130-(y-90)*2,y-2),fill=light)
    d.line((23,102,127,102),fill=trim,width=3);d.line((32,108,119,108),fill=(85,68,62))
    for x in range(41,120,13):
        d.line((x,105,x+2,109),fill=(101,78,62));d.point((x,104),fill=light)
    # Small aft cabin: planks, sloping roof and amber windows.
    d.rectangle((23,68,53,90),fill=ink);d.rectangle((25,70,51,89),fill=(139,111,83))
    for y in [74,79,84,88]:d.line((25,y,51,y),fill=(105,82,68))
    d.polygon([(20,68),(27,61),(52,61),(57,68)],fill=trim,outline=ink)
    for x in [29,43]:
        d.rectangle((x,73,x+5,80),fill=ink);d.rectangle((x+1,74,x+4,78),fill=(230,186,105));d.line((x+3,74,x+3,78),fill=wood)
    # Mast, two furled-looking broad canvas panels, visible stitching and rigging.
    d.line((76,11,76,93),fill=ink,width=5);d.line((76,12,76,92),fill=light,width=2)
    d.line((76,15,17,87),fill=(78,73,72));d.line((78,16,144,84),fill=(78,73,72))
    d.line((46,23,113,23),fill=ink,width=3);d.line((47,22,112,22),fill=light)
    d.polygon([(48,25),(110,25),(119,55),(110,59),(93,62),(72,60),(55,57),(59,43)],fill=ink)
    d.polygon([(50,26),(109,26),(116,54),(108,56),(92,59),(73,57),(58,55),(62,42)],fill=sail)
    shadow=tuple(max(0,c-26) for c in sail)
    d.polygon([(101,27),(109,26),(116,54),(108,56),(105,46)],fill=shadow)
    for x in [66,82,97]:
        d.line((x,28,x+5,55),fill=shadow)
        for y in [33,41,49]:d.point((x+(y-28)//6-1,y),fill=(222,212,178))
    d.line((53,62,117,62),fill=ink,width=3)
    d.polygon([(56,64),(115,64),(122,78),(109,83),(77,81),(54,78)],fill=ink)
    d.polygon([(58,65),(113,65),(119,77),(108,80),(78,78),(57,76)],fill=sail)
    d.polygon([(106,65),(113,65),(119,77),(109,80)],fill=shadow)
    # A modest swallowtail pennant and coiled ropes on deck.
    d.polygon([(79,11),(99,13),(94,17),(99,20),(79,18)],fill=trim,outline=ink)
    for x,y in [(62,88),(112,91)]:
        d.ellipse((x,y,x+9,y+4),outline=(105,87,67));d.ellipse((x+2,y+1,x+7,y+3),outline=light)
    for x in [18,33,125,139]:d.line((x,91,x,96),fill=ink)
    im.resize((320,256),Image.Resampling.NEAREST).save(OUT/f'Demo_{name}.png')
ship('ship1',(114,126,138),(194,184,157))
ship('ship2',(120,141,130),(207,199,169))
im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
for x,y,w,h in [(1,15,15,14),(13,9,17,17),(6,1,14,14)]:
    d.rectangle((x,y,x+w,y+h),fill=(141,113,81),outline=(53,48,47))
    for yy in range(y+3,y+h,4):d.line((x+1,yy,x+w-1,yy),fill=(104,82,65))
    d.line((x+2,y+1,x+2,y+h-1),fill=(189,155,110));d.line((x+w-2,y+1,x+w-2,y+h-1),fill=(67,66,65))
    d.line((x+3,y+2,x+w-3,y+h-2),fill=(164,136,97))
im.resize((64,64),Image.Resampling.NEAREST).save(OUT/'Demo_cargo.png')

# Clone the landscape atlas for Shiohama alone. Keep exact glass/mullion pixels,
# native tile coordinates, transparency and lighthouse rows 444..451 unchanged.
def wooden_village(atlas):
    result=atlas.copy()
    for sx,sy in [(0,227),(4,228)]:
        house=atlas.crop((sx*32,sy*32,(sx+4)*32,(sy+4)*32))
        px=house.load()
        for y in range(128):
            for x in range(128):
                r,g,b,a=px[x,y]
                if not a:continue
                # Original glass includes blue doors, retained for geometric fidelity.
                if b>=180 and g>r+25 and b>g+25:continue
                lum=(r+g+b)//3
                if y<96:
                    # Old shingles; original raised seams and ragged edges survive.
                    px[x,y]=(int(lum*.60)+24,int(lum*.57)+24,int(lum*.55)+28,a)
                else:
                    # Walls acquire salt-worn horizontal timber courses.
                    if lum<90:px[x,y]=(61,53,51,a)
                    elif y>=123:
                        v=(x//12+(y//4))%3;px[x,y]=(112+v*10,116+v*9,118+v*8,a)
                    else:
                        grain=7 if y%6==0 else -13 if y%6==5 else 0
                        px[x,y]=(max(0,int(lum*.52)+46+grain),max(0,int(lum*.42)+35+grain),max(0,int(lum*.32)+30+grain),a)
        # Low-contrast pegs and irregular wood grain on opaque wall portions only.
        for y in [100,106,112,118]:
            for x in [6,38,64,112]:
                r,g,b,a=px[x,y]
                if a and not (b>=180 and g>r+25 and b>g+25):px[x,y]=(78,66,55,a)
        result.paste(house,(sx*32,sy*32))
    return result

# Small, readable interaction markers: notice board, ledger table and memorial.
for name in ['board','ledger','memorial']:
    im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
    if name=='board':
        d.rectangle((3,4,4,15),fill=(83,69,56));d.rectangle((11,4,12,15),fill=(83,69,56))
        d.rectangle((1,1,14,10),fill=(65,57,53));d.rectangle((2,2,13,9),fill=(161,128,89))
        d.rectangle((4,3,11,8),fill=(218,199,158))
        for y in [4,6]:d.line((5,y,10,y),fill=(105,96,83))
    elif name=='ledger':
        d.rectangle((3,8,4,15),fill=(92,70,52));d.rectangle((12,8,13,15),fill=(92,70,52))
        d.rectangle((1,6,14,11),fill=(73,61,54));d.rectangle((2,6,13,9),fill=(168,137,99))
        d.rectangle((4,3,12,7),fill=(211,197,159));d.line((8,3,8,7),fill=(119,102,79))
        for y in [4,6]:d.point((6,y),fill=(98,91,79));d.point((10,y),fill=(98,91,79))
    else:
        d.polygon([(2,13),(3,5),(6,2),(13,4),(15,13)],fill=(64,69,78))
        d.polygon([(3,12),(4,6),(7,3),(12,5),(13,12)],fill=(161,166,163))
        for y in [6,8,10]:d.line((6,y,10,y),fill=(101,109,114))
        d.line((2,12,5,14),fill=(202,158,117),width=2)
    im.resize((32,32),Image.Resampling.NEAREST).save(OUT/f'Demo_{name}.png')
