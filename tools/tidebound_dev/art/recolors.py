"""Palette-only regional artwork. Source geometry and alpha stay unchanged."""

from PIL import Image


def recolor(path, palette):
    with Image.open(path) as image:
        edited = image.convert("RGBA")
    pixels = list(edited.get_flattened_data())
    missing = palette.keys() - {p[:3] for p in pixels if p[3]}
    if missing:
        raise ValueError(f"{path}: expected source palette colours missing: {sorted(missing)}")
    edited.putdata([(*palette.get(p[:3], p[:3]), p[3]) if p[3] else p for p in pixels])
    return edited
