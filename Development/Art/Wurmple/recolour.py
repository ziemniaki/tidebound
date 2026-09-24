"""User-authorized exact palette edit. Run with Python 3 and Pillow.

Preserves every source pixel position and alpha value; no image generation,
resampling, new outlines or shading. Stock form-0 sprites are never overwritten.
"""
from pathlib import Path
from PIL import Image

G = Path(__file__).resolve().parents[3]
PALETTES = {
    'Front': {
        (164,24,57):(60,112,152),
        (205,82,90):(124,204,236),
        (246,123,98):(180,232,252),
        (246,164,139):(220,248,255),
        (98,82,82):(66,78,90),
    },
    'Back': {
        (164,26,60):(60,112,152),
        (204,82,92):(124,204,236),
        (244,122,100):(180,232,252),
        (100,82,84):(66,78,90),
    },
    'Icons': {
        (232,112,152):(144,216,240),
        (248,176,160):(208,240,252),
    },
}

for folder, palette in PALETTES.items():
    source = G / 'Graphics/Pokemon' / folder / 'WURMPLE.png'
    original = Image.open(source).convert('RGBA')
    pixels = list(original.getdata())
    assert set(palette).issubset({p[:3] for p in pixels if p[3]})
    edited = original.copy()
    edited.putdata([(*palette.get(p[:3], p[:3]), p[3]) if p[3] else p for p in pixels])
    assert edited.getchannel('A').tobytes() == original.getchannel('A').tobytes()
    assert edited.size == original.size
    edited.save(source.with_name('WURMPLE_1.png'))
    if folder in ('Front', 'Back'):
        # A distinct shiny palette is not yet designed. Avoid a red fallback.
        edited.save(G / 'Graphics/Pokemon' / (folder + ' shiny') / 'WURMPLE_1.png')
    print(folder, original.size, 'exact geometry and alpha preserved')
