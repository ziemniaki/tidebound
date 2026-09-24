"""Exact palette edits for Tidebound Ekans/Arbok; preserve geometry and alpha.

Run from any directory with Pillow. Ordinary form-0 assets remain the source.
Shiny regional sprites use the same provisional gray palette, not stock purple.
"""
from pathlib import Path
from PIL import Image

G = Path(__file__).resolve().parents[3]
PALETTES = {
    ('EKANS', 'Front'): {
        (90,16,74):(52,54,57), (123,49,106):(78,81,84),
        (164,74,139):(112,115,118), (205,98,180):(150,153,156),
        (238,164,213):(196,199,201),
    },
    ('EKANS', 'Back'): {
        (92,18,76):(52,54,57), (124,50,108):(78,81,84),
        (164,74,140):(112,115,118), (204,98,180):(150,153,156),
    },
    ('ARBOK', 'Front'): {
        (82,57,123):(70,73,76), (123,98,172):(112,115,118),
        (164,131,197):(150,153,156), (197,164,238):(196,199,201),
    },
    ('ARBOK', 'Back'): {
        (84,58,124):(70,73,76), (124,98,172):(112,115,118),
        (164,130,196):(150,153,156),
    },
}
for species in ('EKANS', 'ARBOK'):
    PALETTES[(species, 'Icons')] = {
        (144,120,200):(112,115,118), (192,160,200):(169,172,175),
    }

for (species, folder), palette in PALETTES.items():
    source = G / 'Graphics/Pokemon' / folder / (species + '.png')
    original = Image.open(source).convert('RGBA')
    pixels = list(original.getdata())
    assert set(palette).issubset({p[:3] for p in pixels if p[3]})
    edited = original.copy()
    edited.putdata([(*palette.get(p[:3], p[:3]), p[3]) if p[3] else p for p in pixels])
    assert edited.getchannel('A').tobytes() == original.getchannel('A').tobytes()
    edited.save(source.with_name(species + '_1.png'))
    if folder in ('Front', 'Back'):
        edited.save(G / 'Graphics/Pokemon' / (folder + ' shiny') / (species + '_1.png'))
    print(species, folder, 'palette only; silhouette, details and alpha retained')
