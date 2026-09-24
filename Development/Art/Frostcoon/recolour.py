"""Manually specified palette edit of included Silcoon sprites; no generation.

Every pixel position and alpha value is preserved, including both icon frames.
Run standalone or via rebuild_glaciverm_data.py to keep rebuilds reproducible.
"""
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parents[3]
PALETTES = {
 'Front': {(238,238,230):(231,249,255),(222,213,230):(179,228,248),
           (189,189,205):(121,189,224),(172,172,180):(92,159,197),
           (139,139,148):(66,125,164),(106,106,115):(47,90,123),
           (24,24,24):(22,43,62),(16,16,24):(15,32,48),
           (197,8,0):(225,190,49),(246,106,98):(255,233,122)},
 'Back': {(236,238,228):(231,249,255),(220,214,228):(179,228,248),
          (188,190,204):(121,189,224),(172,174,180):(92,159,197),
          (140,138,148):(66,125,164),(108,106,116):(47,90,123),
          (28,26,28):(22,43,62),(252,254,252):(250,255,255),
          (196,10,4):(225,190,49)},
 'Icons': {(248,248,248):(223,247,255),(184,184,176):(137,205,235),
           (120,120,120):(87,154,194),(96,96,88):(54,105,145),
           (64,64,64):(25,50,72),(240,96,80):(248,216,79)}
}
for folder,palette in PALETTES.items():
 original=Image.open(G/'Graphics/Pokemon'/folder/'SILCOON.png').convert('RGBA')
 assert set(palette).issubset({p[:3] for p in original.getdata() if p[3]})
 edited=original.copy()
 edited.putdata([(*palette.get(p[:3],p[:3]),p[3]) if p[3] else p for p in original.getdata()])
 assert edited.getchannel('A').tobytes()==original.getchannel('A').tobytes()
 edited.save(G/'Graphics/Pokemon'/folder/'FROSTCOON.png')
 if folder!='Icons':edited.save(G/'Graphics/Pokemon'/(folder+' shiny')/'FROSTCOON.png')
print('Frostcoon front/back/shiny/icon: frozen-silk blue palette, golden eye; native geometry retained.')
