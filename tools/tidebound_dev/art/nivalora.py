"""Reduce the approved Nivalora sources with the fixed design palette."""

from PIL import Image

COLOURS = [
    (12, 30, 49),
    (34, 58, 80),
    (71, 104, 137),
    (98, 146, 183),
    (144, 189, 215),
    (181, 222, 244),
    (211, 239, 252),
    (249, 253, 255),
    (247, 241, 202),
    (220, 213, 170),
    (175, 170, 125),
    (105, 105, 71),
    (255, 219, 53),
    (213, 170, 33),
    (225, 241, 246),
    (125, 165, 188),
]
palette = Image.new("P", (1, 1))
palette.putpalette([c for rgb in COLOURS for c in rgb] + [0] * (768 - 48))


def reduce(source, max_size):
    im = Image.open(source).convert("RGBA")
    alpha = im.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
    im.putalpha(alpha)
    im = im.crop(alpha.getbbox())
    ratio = min(max_size[0] / im.width, max_size[1] / im.height)
    im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.Resampling.NEAREST)
    alpha = im.getchannel("A")
    rgb = Image.new("RGB", im.size, COLOURS[0])
    rgb.paste(im, mask=alpha)
    out = rgb.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
    out.putalpha(alpha)
    return out


def generate(game, assets):
    for face, source in [("Front", "approved_front.png"), ("Back", "rear_source.png")]:
        small = reduce(assets / source, (72, 72))
        double = small.resize((small.width * 2, small.height * 2), Image.Resampling.NEAREST)
        frame = Image.new("RGBA", (160, 160))
        frame.paste(
            double, ((160 - double.width) // 2, 8 if face == "Front" else 160 - double.height)
        )
        for directory in [face, face + " shiny"]:
            frame.save(game / f"Graphics/Pokemon/{directory}/NIVALORA.png")
    small = reduce(assets / "approved_front.png", (28, 28))
    icon = small.resize((small.width * 2, small.height * 2), Image.Resampling.NEAREST)
    sheet = Image.new("RGBA", (128, 64))
    for x, y in [(0, 6), (64, 4)]:
        sheet.paste(icon, (x + (64 - icon.width) // 2, y))
    sheet.save(game / "Graphics/Pokemon/Icons/NIVALORA.png")
