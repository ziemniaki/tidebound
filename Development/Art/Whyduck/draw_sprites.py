"""Manual Whyduck pixel art based on Psyduck and the supplied reference.

Two pink hemispheres grow through an opened skull; wings arc for a spell.
80x80 and 64x32 source grids are scaled exactly 2x without filtering.
"""
from pathlib import Path
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parents[3]/'Graphics/Pokemon'
O=(56,42,49,255); GAP=(66,40,58,255); LIP=(134,86,73,255)
BONE=(255,238,189,255); Y=(255,213,74,255); HI=(255,232,135,255)
SHADE=(230,164,82,255); MID=(222,180,82,255)
BEAK=(255,222,143,255); BEAKHI=(255,242,193,255); BEAKSH=(148,90,16,255)
EYE=(35,34,39,255); EYEWHITE=(255,253,241,255); EYEGREY=(203,195,181,255)
GO=(111,51,85,255); GD=(167,83,119,255); GS=(207,118,154,255)
GM=(237,162,190,255); GL=(255,200,219,255); GH=(255,234,239,255)
V=(155,99,129,255)
def poly(d,points,fill,outline=O):
    d.polygon(points,fill=fill)
    if outline:d.line(points+[points[0]],fill=outline,width=1)
def brain(d,rear=False):
    # A wide two-lobed contour with a deep central fissure and winding sulci.
    c=[(21,22),(23,18),(23,15),(26,13),(27,10),(31,9),
       (34,10),(37,8),(41,10),(43,8),(47,9),(51,11),
       (54,11),(56,14),(58,18),(57,21),(58,23),(55,25),
       (51,25),(48,27),(44,26),(41,28),(37,26),
       (33,27),(30,25),(26,26),(23,24)]
    poly(d,c,GS,GO)
    d.polygon([(24,17),(29,12),(33,11),(38,13),(40,11),(40,24),
               (35,25),(29,24),(24,22)],fill=GM)
    d.polygon([(42,11),(47,10),(51,13),(55,16),(56,21),
               (52,24),(47,25),(42,23)],fill=GM)
    for path in [[(40,10),(40,13),(39,15),(41,18),(39,20),(40,23)],
                 [(28,16),(31,14),(34,14),(35,17),(32,19),(29,19),(28,21)],
                 [(35,11),(36,14),(38,16),(37,18),(35,19),(35,22)],
                 [(26,22),(29,22),(31,20),(33,21),(33,24)],
                 [(45,11),(45,14),(48,15),(50,14),(53,17),(51,19)],
                 [(43,18),(45,19),(44,22),(47,23),(49,21),(53,22)],
                 [(31,24),(28,23),(26,24)],
                 [(47,25),(49,23),(51,24)]]:
        d.line(path,fill=GO if path[0][0]==40 else GD,width=1)
    for path in [[(27,16),(29,13),(32,12)],[(34,13),(36,12)],
                 [(43,13),(45,11)],[(48,13),(51,14)],[(53,18),(55,18)]]:
        d.line(path,fill=GL,width=1)
    for x,y in [(28,14),(33,12),(46,12),(52,14)]:d.point((x,y),fill=GH)
    d.line([(34,25),(36,26),(39,25),(42,26),(46,25)],fill=GD,width=1)
    # Short asymmetric roots occupy the skull cavity; no decorative headband.
    d.polygon([(34,25),(37,25),(39,27),(42,25),(44,27),
               (47,25),(46,29),(44,28),(41,31),(38,28),
               (36,30),(35,27)],fill=GS)
    d.line([(37,26),(39,29),(40,30)],fill=GD,width=1)
    d.line([(44,27),(43,29)],fill=GO,width=1)
def skull(d):
    # Brain overlaps the jagged bone rim and visible dark opening in the head.
    d.polygon([(26,30),(29,25),(33,27),(36,25),(40,27),
               (43,25),(47,27),(51,25),(54,30),(52,33),(28,33)],fill=GAP)
    d.line([(27,29),(29,27),(33,29),(36,27),(40,29),
            (43,27),(47,29),(50,27),(53,30)],fill=LIP,width=2)
    d.line([(26,31),(29,29),(32,31),(35,29),(38,31)],fill=BONE,width=1)
    d.line([(44,31),(47,29),(50,31),(53,29),(55,32)],fill=BONE,width=1)
    d.line([(27,32),(30,33),(32,32)],fill=LIP,width=1)
    d.line([(53,32),(51,33),(49,32)],fill=LIP,width=1)
    d.line([(27,29),(25,31),(25,34),(27,36)],fill=LIP,width=1)
    d.line([(53,29),(55,32),(54,35)],fill=LIP,width=1)
    d.line([(29,32),(31,34),(32,34)],fill=SHADE,width=1)
    d.line([(51,32),(49,34)],fill=SHADE,width=1)
    d.line([(30,29),(32,30),(35,29),(38,30),(41,29),(44,30),(48,29)],fill=V,width=1)
def arms(d,rear=False):
    # Uneven incantation pose; the viewer's left arm is lowered while the
    # right is raised. Back view mirrors the pose by reversing visible sides.
    def pose(points):return [(80-x if rear else x,y) for x,y in points]
    shade=SHADE if rear else Y
    low=[(31,47),(27,46),(23,47),(19,48),(15,49),(11,50),
         (8,51),(7,54),(8,56),(11,58),(15,58),(19,56),
         (23,54),(27,53),(31,53)]
    high=[(49,46),(53,44),(57,43),(60,41),(64,39),(68,38),
          (72,37),(74,38),(75,41),(72,44),(68,45),
          (64,45),(60,48),(54,50),(49,52)]
    for path in (low,high):poly(d,pose(path),shade)
    d.line(pose([(11,53),(18,52),(25,49)]),fill=HI if not rear else Y,width=2)
    d.line(pose([(70,40),(64,41),(56,46)]),fill=HI if not rear else Y,width=2)
    d.line(pose([(19,55),(24,52),(28,52)]),fill=SHADE,width=1)
    d.line(pose([(62,44),(59,47)]),fill=SHADE,width=1)
    # The actual Psyduck hand pixels are attached after the body is drawn.
def feet(d,rear=False):
    # Low, spread Psyduck feet: pale webbed toes outlined in ochre.
    for mirrored in (False,True):
        def h(path):return [(80-x if mirrored else x,y) for x,y in path]
        poly(d,h([(30,62),(34,62),(36,65),(35,67),(37,67),
                  (38,69),(36,70),(33,69),(31,70),(28,69),
                  (26,69),(25,67),(27,66),(28,64)]),BONE,BEAKSH)
        d.line(h([(28,66),(32,66),(33,68)]),fill=HI,width=1)
        d.line(h([(27,69),(29,68),(31,69)]),fill=BEAKSH,width=1)
def front():
    im=Image.new('RGBA',(80,80));d=ImageDraw.Draw(im)
    poly(d,[(50,55),(55,55),(59,58),(57,61),(51,63)],SHADE)
    feet(d);arms(d)
    # Match Psyduck's original chest: ochre flanks surround a golden belly.
    poly(d,[(34,43),(47,43),(52,47),(54,55),(53,61),
            (50,65),(45,66),(35,66),(30,64),(27,59),(27,52)],SHADE)
    d.polygon([(35,47),(44,47),(49,50),(51,54),(50,59),
               (47,62),(43,64),(35,64),(31,61),(29,56),
               (30,52)],fill=Y)
    d.line([(50,57),(49,61),(46,64)],fill=MID,width=1)
    d.line([(30,60),(34,64),(38,65)],fill=SHADE,width=1)
    poly(d,[(30,27),(36,24),(46,24),(52,27),(55,31),
            (57,37),(55,43),(51,47),(47,49),(33,49),
            (29,47),(26,43),(25,37),(26,31)],Y)
    d.polygon([(28,32),(33,28),(41,27),(47,29),(51,33),
               (51,38),(47,44),(35,45),(29,41)],fill=HI)
    d.line([(26,41),(28,45),(31,47)],fill=SHADE,width=2)
    # The exact pre-evolution eye artwork is composited after drawing.
    # The exact original Psyduck bill pixels are composited after drawing.
    skull(d);brain(d)
    return im
def back():
    im=Image.new('RGBA',(80,80));d=ImageDraw.Draw(im)
    feet(d,rear=True);arms(d,rear=True)
    poly(d,[(33,41),(47,41),(53,46),(56,55),(56,65),
            (51,64),(47,67),(34,67),(28,65),(25,61),(26,51)],SHADE)
    d.polygon([(29,50),(34,45),(48,45),(52,50),(54,64),
               (48,65),(34,65),(29,62)],fill=Y)
    d.line([(28,59),(31,65),(35,67)],fill=SHADE,width=1)
    poly(d,[(27,29),(33,25),(47,25),(53,29),(55,36),
            (54,44),(50,48),(44,50),(36,50),(30,47),
            (26,43),(25,36)],Y)
    d.polygon([(28,33),(35,28),(45,28),(52,33),(53,43),
               (48,47),(33,47),(28,41)],fill=HI)
    d.line([(27,41),(30,45),(33,47)],fill=SHADE,width=1)
    skull(d);brain(d,rear=True)
    return im
def shiny(im):
    colours={Y:(179,217,220,255),HI:(220,241,238,255),
             SHADE:(113,168,175,255),MID:(151,194,193,255),
             EYEWHITE:(248,251,247,255),EYEGREY:(191,206,207,255),
             BONE:(236,251,245,255),BEAK:(234,166,112,255),
             BEAKHI:(251,211,157,255),BEAKSH:(165,100,87,255),
             GO:(38,99,51,255),GD:(55,138,63,255),
             GS:(90,180,83,255),GM:(132,223,119,255),
             GL:(180,244,164,255),GH:(223,255,201,255),
             V:(100,81,150,255),LIP:(124,91,116,255),
             GAP:(55,58,91,255)}
    result=im.copy();result.putdata([colours.get(p,p) for p in im.get_flattened_data()])
    return result
def icon_frame(d,ox,bob=0):
    def shift(path):return [(ox+x,y+bob) for x,y in path]
    poly(d,shift([(12,15),(20,15),(22,19),(21,26),(19,28),
                  (13,28),(10,25),(10,20)]),Y)
    d.polygon(shift([(21,19),(23,22),(22,25),(20,27),
                     (18,27),(20,24)]),fill=SHADE)
    poly(d,shift([(12,21),(8,22),(5,24),(3,25),(3,27),(6,28),(9,26),(12,24)]),Y)
    poly(d,shift([(20,21),(23,19),(26,17),(29,17),(30,19),(28,21),(24,22),(21,24)]),Y)
    d.line(shift([(3,26),(5,25),(6,26)]),fill=BONE,width=1)
    d.line(shift([(27,18),(29,18)]),fill=BONE,width=1)
    poly(d,shift([(12,14),(15,13),(19,13),(22,16),(23,20),
                  (21,24),(11,24),(9,20),(10,17)]),HI)
    d.line(shift([(12,27),(12,28),(14,29),(16,28)]),fill=BONE,width=2)
    d.line(shift([(19,27),(19,28),(21,29),(23,28)]),fill=BONE,width=2)
    d.point((ox+14,29+bob),fill=BEAKSH)
    d.point((ox+21,29+bob),fill=BEAKSH)
    for left in (11,18):
        d.ellipse((ox+left,16+bob,ox+left+4,20+bob),fill=EYEWHITE,outline=O)
        d.point((ox+left+1,19+bob),fill=EYE)
    # Literal original Psyduck icon bill is pasted over this face below.
    d.line(shift([(11,15),(13,14),(15,15),(17,14),(19,15),(21,14)]),fill=LIP,width=2)
    d.line(shift([(11,16),(13,15),(16,16),(19,15),(21,16)]),fill=BONE,width=1)
    poly(d,shift([(9,12),(10,9),(12,8),(13,6),(16,6),(17,7),
                  (19,6),(22,7),(24,10),(23,14),(19,15),(16,14),(13,15),(10,14)]),GM,GO)
    d.line(shift([(11,10),(14,9),(15,11),(13,12),(14,14)]),fill=GD,width=1)
    d.line(shift([(18,8),(18,11),(17,12),(19,14)]),fill=GO,width=1)
    d.line(shift([(20,9),(22,10),(21,12),(23,13)]),fill=GD,width=1)
    d.point((ox+12,9+bob),fill=GH)
def save():
    hand=Image.open(Path(__file__).parent/'pieces'/'psyduck_hand.png').convert('RGBA')
    point_left=hand.transpose(Image.Transpose.ROTATE_90)
    point_right=hand.transpose(Image.Transpose.ROTATE_270)
    for folder,draw in [('Front',front),('Back',back)]:
        original=draw()
        for alt in (False,True):
            target=P/(folder+(' shiny' if alt else ''))/'WHYDUCK.png'
            sprite=shiny(original) if alt else original.copy()
            if folder=='Front':
                tag='_shiny' if alt else ''
                for side,dest in (('left',(28,33)),('right',(40,33))):
                    eye=Image.open(Path(__file__).parent/'pieces'/
                                   ('psyduck_eye_'+side+tag+'.png')).convert('RGBA')
                    sprite.alpha_composite(eye,dest)
                beak_file='psyduck_beak_shiny.png' if alt else 'psyduck_beak.png'
                beak=Image.open(Path(__file__).parent/'pieces'/beak_file).convert('RGBA')
                # The original bill rests just left and below the midpoint
                # between the eyes; do not redraw or scale its source pixels.
                sprite.alpha_composite(beak,(26,41))
                sprite.alpha_composite(point_left,(4,50))
                sprite.alpha_composite(point_right,(63,36))
            else:
                # Same physical arms, seen from behind: raised left,
                # lowered right, with Psyduck's original hand pixels.
                sprite.alpha_composite(point_left,(3,36))
                sprite.alpha_composite(point_right,(63,50))
            sprite.resize((160,160),Image.Resampling.NEAREST).save(target)
    icon=Image.new('RGBA',(64,32));d=ImageDraw.Draw(icon)
    icon_frame(d,0);icon_frame(d,32,1)
    icon_beak=Image.open(Path(__file__).parent/'pieces'/'psyduck_icon_beak.png').convert('RGBA')
    icon.alpha_composite(icon_beak,(10,20))
    icon.alpha_composite(icon_beak,(42,21))
    icon.resize((128,64),Image.Resampling.NEAREST).save(P/'Icons/WHYDUCK.png')
    print('Whyduck sprite draft: pink brain, Psyduck palms and webbed feet.')
save()
