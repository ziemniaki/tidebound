from ..files import save_png
from PIL import Image, ImageDraw
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import struct

from .model import table


"""Interior tile atlas and furniture painting, owned by one map compilation."""

from PIL import Image, ImageDraw
import random


class InteriorPainter:
    def __init__(self, game):
        self.I = Image.open(game / "Graphics/Tilesets/Interior general.png").convert("RGBA")
        self.interior_tiles = []
        self.interior_cache = {}
        self.interior_base = 384 + (self.I.height // 32) * 8

        # Pixel-exact object bounds avoid neighbouring objects and half-sprite fragments.
        self.BED = self.muted(self.crop((24, 4828, 74, 4896)))
        self.SHELF = self.muted(self.crop((96, 4480, 160, 4544)))
        self.CUPBOARD = self.muted(self.crop((66, 4600, 112, 4656)))
        self.CABINET = self.muted(self.crop((192, 4598, 256, 4656)), 0.65)
        self.SINK = self.muted(self.crop((32, 4728, 96, 4784)))
        ImageDraw.Draw(self.SINK).rectangle((32, 0, 63, 7), fill=(0, 0, 0, 0))
        self.COOKER = self.muted(self.crop((160, 4740, 192, 4786)))
        self.SOFA = self.muted(self.crop((64, 5026, 160, 5088)))
        self.STOOL = self.muted(self.crop((230, 5098, 252, 5120)))
        self.PLANT = self.muted(self.crop((128, 5538, 160, 5600)))
        self.BOOK = Image.new("RGBA", (32, 32))
        bd = ImageDraw.Draw(self.BOOK)
        bd.rectangle((5, 18, 8, 30), fill=(76, 61, 49, 255))
        bd.rectangle((23, 18, 26, 30), fill=(76, 61, 49, 255))
        bd.rectangle((2, 8, 29, 24), fill=(101, 80, 57, 255), outline=(60, 56, 49, 255), width=2)
        bd.line((4, 9, 27, 9), fill=(166, 137, 96, 255), width=2)
        bd.rectangle((8, 10, 23, 20), fill=(202, 196, 165, 255), outline=(96, 104, 100, 255))
        bd.line((15, 11, 15, 19), fill=(133, 127, 109, 255))
        bd.line((10, 14, 13, 14), fill=(141, 138, 120, 255))
        bd.line((18, 14, 21, 14), fill=(141, 138, 120, 255))
        self.BASIN = self.muted(self.crop((2, 4770, 30, 4800)))
        self.STAIR_DOWN = self.muted(self.crop((28, 4140, 96, 4216)), 0.55)
        self.STAIR_UP = self.muted(self.crop((100, 4140, 166, 4216)), 0.55)
        self.TABLE = self.muted(self.native(6, 212, 2, 2))
        # Archive cupboards retain native silhouettes, with weathered timber colours.
        self.ARCHIVE = self.CUPBOARD.copy()
        for yy in range(self.ARCHIVE.height):
            for xx in range(self.ARCHIVE.width):
                r, g, b, a = self.ARCHIVE.getpixel((xx, yy))
                if a:
                    l = int(r * 0.3 + g * 0.5 + b * 0.2)
                    self.ARCHIVE.putpixel(
                        (xx, yy), (int(l * 0.70), int(l * 0.65), int(l * 0.54), a)
                    )

    def itile(self, im):
        key = im.tobytes()
        if key not in self.interior_cache:
            self.interior_cache[key] = self.interior_base + len(self.interior_tiles)
            self.interior_tiles.append(im.copy())
        return self.interior_cache[key]

    def crop(self, box):
        return self.I.crop(box)

    def native(self, x, y, w=1, h=1):
        return self.crop((x * 32, y * 32, (x + w) * 32, (y + h) * 32))

    def muted(self, im, amount=0.30):
        grey = im.convert("L").convert("RGBA")
        grey.putalpha(im.getchannel("A"))
        return Image.blend(im, grey, amount)

    def fit_asset(self, im, w, h):
        if im.width > w * 32 or im.height > h * 32:
            im.thumbnail((w * 32, h * 32), Image.Resampling.NEAREST)
        out = Image.new("RGBA", (w * 32, h * 32))
        out.alpha_composite(im, ((w * 32 - im.width) // 2, h * 32 - im.height))
        return out

    def surface(self, m, im, x, y, solid=False, layer=1):
        for yy in range(im.height // 32):
            for xx in range(im.width // 32):
                cell = im.crop((xx * 32, yy * 32, xx * 32 + 32, yy * 32 + 32))
                if cell.getbbox():
                    previous = m.layers[layer][y + yy][x + xx]
                    if previous >= self.interior_base:
                        base = self.interior_tiles[previous - self.interior_base].copy()
                        base.alpha_composite(cell)
                        cell = base
                    m.layers[layer][y + yy][x + xx] = self.itile(cell)
                if solid:
                    m.walk[y + yy][x + xx] = False

    def prop(self, m, im, x, y, w, h, solid=True):
        self.surface(m, self.fit_asset(im.copy(), w, h), x, y, solid)

    def floor_tile(self, stone=False, variant=0):
        if not stone:
            im = self.muted(self.native(4, 78))
            return Image.blend(im, Image.new("RGBA", (32, 32), (101, 83, 65, 255)), 0.22)
        v = [0, 3, -2][variant % 3]
        im = Image.new("RGBA", (32, 32), (94 + v, 102 + v, 105 + v, 255))
        d = ImageDraw.Draw(im)
        d.line((0, 31, 31, 31), fill=(69, 79, 84, 255), width=2)
        d.line((31, 0, 31, 31), fill=(69, 79, 84, 255), width=2)
        d.line((2, 1, 28, 1), fill=(112, 119, 120, 255), width=1)
        r = random.Random(716 + variant)
        for _ in range(5):
            x = r.randrange(2, 14) * 2
            y = r.randrange(2, 14) * 2
            d.rectangle((x, y, x + 1, y + 1), fill=(86 + v, 95 + v, 99 + v, 255))
        return im

    def wall(self, stone=False):
        im = Image.new("RGBA", (32, 64), (127, 123, 103, 255))
        d = ImageDraw.Draw(im)
        if stone:
            d.rectangle((0, 0, 31, 63), fill=(74, 85, 92, 255))
            for y in [0, 16, 32, 48]:
                d.line((0, y, 31, y), fill=(42, 53, 62, 255), width=2)
                x = 8 if y % 32 else 24
                d.line((x, y, x, y + 14), fill=(51, 63, 71, 255), width=2)
            d.rectangle((0, 56, 31, 63), fill=(47, 57, 64, 255))
            d.line((0, 56, 31, 56), fill=(112, 116, 109, 255), width=2)
        else:
            d.rectangle((0, 0, 31, 7), fill=(78, 64, 53, 255))
            d.line((0, 8, 31, 8), fill=(166, 147, 115, 255), width=2)
            d.rectangle((0, 36, 31, 63), fill=(91, 78, 60, 255))
            for x in [0, 16, 30]:
                d.line((x, 38, x, 62), fill=(67, 62, 52, 255), width=2)
            d.rectangle((0, 34, 31, 38), fill=(159, 135, 96, 255))
            d.rectangle((0, 60, 31, 63), fill=(48, 48, 45, 255))
        return im

    def room(self, m, x, y, w, h, stone=False):
        m.layers = [[[0] * m.w for _ in range(m.h)] for _ in range(3)]
        m.walk = [[False] * m.w for _ in range(m.h)]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                m.layers[0][yy][xx] = self.itile(self.floor_tile(stone, (xx + yy) % 3))
                m.walk[yy][xx] = True
        for xx in range(x, x + w):
            self.surface(m, self.wall(stone), xx, y - 2)
        for xx in [x, x + w - 1]:
            for yy in range(y, y + h):
                edge = Image.new("RGBA", (32, 32))
                d = ImageDraw.Draw(edge)
                a = 0 if xx == x else 26
                d.rectangle((a, 0, a + 5, 31), fill=(48, 54, 56, 255))
                d.line((a + 3, 0, a + 3, 31), fill=(124, 125, 114, 255), width=2)
                self.surface(m, edge, xx, yy, False, 2)

    def rug(self, m, x, y, w, h, color):
        im = Image.new("RGBA", (w * 32, h * 32))
        d = ImageDraw.Draw(im)
        d.rectangle((2, 2, w * 32 - 3, h * 32 - 3), fill=color, outline=(64, 61, 59, 255), width=2)
        d.rectangle((8, 8, w * 32 - 9, h * 32 - 9), outline=(172, 155, 120, 255), width=2)
        for xx in range(10, w * 32 - 10, 12):
            d.rectangle((xx, 12, xx + 3, 13), fill=(140, 135, 116, 255))
            d.rectangle((xx, h * 32 - 14, xx + 3, h * 32 - 13), fill=(140, 135, 116, 255))
        # Composite over wood so the transparent rug margins never become void.
        base = Image.new("RGBA", im.size)
        for yy in range(h):
            for xx in range(w):
                base.alpha_composite(self.floor_tile(), (xx * 32, yy * 32))
        base.alpha_composite(im)
        self.surface(m, base, x, y, False, 0)

    def window(self, m, x, y, w=2):
        im = Image.new("RGBA", (w * 32, 64))
        d = ImageDraw.Draw(im)
        d.rectangle(
            (2, 4, w * 32 - 3, 53), fill=(52, 60, 63, 255), outline=(166, 162, 141, 255), width=2
        )
        d.rectangle((8, 10, w * 32 - 9, 45), fill=(22, 39, 57, 255))
        for xx in range(14, w * 32 - 10, 18):
            d.line((xx, 12, xx, 43), fill=(59, 78, 87, 255), width=2)
        d.line((8, 31, w * 32 - 9, 31), fill=(84, 99, 107, 255), width=2)
        d.rectangle((0, 52, w * 32 - 1, 59), fill=(101, 103, 97, 255))
        d.line((0, 52, w * 32 - 1, 52), fill=(191, 184, 153, 255), width=2)
        # Keep the wall behind the glass and sill, including transparent margins.
        base = Image.new("RGBA", im.size)
        for xx in range(w):
            base.alpha_composite(self.wall(m.id in (104, 110, 111)), (xx * 32, 0))
        base.alpha_composite(im)
        self.surface(m, base, x, y)

    def stairs(self, m, x, y, up=True):
        self.surface(
            m, self.fit_asset((self.STAIR_UP if up else self.STAIR_DOWN).copy(), 2, 3), x, y
        )
        for yy in range(y, y + 3):
            for xx in range(x, x + 2):
                m.walk[yy][xx] = True

    def lamp(self, m, x, y):
        im = Image.new("RGBA", (32, 32))
        d = ImageDraw.Draw(im)
        d.rectangle((9, 26, 23, 29), fill=(68, 59, 48, 255))
        d.rectangle((14, 11, 17, 27), fill=(130, 112, 73, 255))
        d.rectangle((9, 6, 22, 18), fill=(89, 82, 64, 255))
        d.rectangle((12, 8, 19, 15), fill=(234, 191, 111, 255))
        d.rectangle((8, 4, 23, 7), fill=(65, 68, 64, 255))
        self.surface(m, im, x, y)


def save_atlas(paths, interior, rooms):
    sets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    id = next(
        (
            i
            for i, t in enumerate(sets)
            if t and t.attributes.get("@name") == "Tidebound Lighthouse"
        ),
        len(sets),
    )
    ts = loads(writes(sets[3]))
    ts.attributes.update(
        {"@id": id, "@name": "Tidebound Lighthouse", "@tileset_name": "TideboundLighthouse"}
    )
    h = interior.I.height + ((len(interior.interior_tiles) + 7) // 8) * 32
    assert h <= 16384
    atlas = Image.new("RGBA", (256, h))
    atlas.alpha_composite(interior.I)
    for i, im in enumerate(interior.interior_tiles):
        atlas.alpha_composite(im, ((i % 8) * 32, interior.I.height + (i // 8) * 32))
    save_png(atlas, paths.game / "Graphics/Tilesets/TideboundLighthouse.png")
    for key in ["@passages", "@priorities", "@terrain_tags"]:
        raw = ts.attributes[key]._dump()
        size = struct.unpack("<5i", raw[:20])[4]
        vals = list(struct.unpack("<" + "h" * size, raw[20:]))
        vals = vals[: interior.interior_base] + [0] * max(0, interior.interior_base - len(vals))
        vals += [0] * len(interior.interior_tiles)
        ts.attributes[key] = table(vals, len(vals))
    if id == len(sets):
        sets.append(ts)
    else:
        sets[id] = ts
    (paths.game / "Data/Tilesets.rxdata").write_bytes(writes(sets))
    for m in rooms:
        m.tileset = id
