from ..files import save_png
from PIL import Image, ImageDraw
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import json
import struct

from .model import table


def decorate(paths, interior, bedroom, home, lantern, basement, vault):
    interior.room(bedroom, 2, 4, 12, 8)
    interior.window(bedroom, 4, 2)
    interior.window(bedroom, 10, 2)
    interior.prop(bedroom, interior.BED, 3, 4, 2, 3)
    interior.prop(bedroom, interior.SHELF, 11, 4, 2, 2)
    interior.prop(bedroom, interior.CUPBOARD, 8, 4, 2, 2)
    interior.rug(bedroom, 5, 7, 5, 3, (74, 92, 100, 255))
    interior.prop(bedroom, interior.BOOK, 3, 8, 1, 1)
    interior.lamp(bedroom, 3, 9)
    interior.prop(bedroom, interior.STOOL, 4, 9, 1, 1)
    interior.prop(bedroom, interior.PLANT, 12, 9, 1, 2)
    interior.stairs(bedroom, 7, 10, False)
    bedroom.rect(8, 12, 1, 1, interior.itile(interior.floor_tile()), walk=True)

    interior.room(home, 2, 3, 16, 11)
    interior.window(home, 8, 1)
    interior.window(home, 12, 1)
    interior.stairs(home, 5, 1)
    interior.stairs(home, 16, 1)
    interior.stairs(home, 2, 10, False)
    interior.prop(home, interior.SHELF, 3, 3, 2, 2)
    interior.prop(home, interior.CUPBOARD, 10, 3, 2, 2)
    interior.prop(home, interior.SINK, 12, 4, 2, 2)
    interior.prop(home, interior.COOKER, 14, 4, 1, 2)
    interior.prop(home, interior.BASIN, 15, 5, 1, 1)
    interior.rug(home, 7, 6, 4, 4, (100, 76, 64, 255))
    interior.prop(home, interior.TABLE, 8, 7, 2, 2)
    interior.prop(home, interior.SOFA, 4, 8, 3, 2)
    interior.prop(home, interior.BOOK, 4, 10, 1, 1, False)
    interior.lamp(home, 5, 10)
    interior.prop(home, interior.PLANT, 15, 7, 1, 2)
    interior.rug(home, 14, 10, 2, 2, (87, 99, 84, 255))
    interior.prop(home, interior.CUPBOARD, 16, 10, 2, 2)
    home.rect(10, 14, 1, 1, interior.itile(interior.floor_tile()), walk=True)
    # The room already has a clear corridor around the table; keep its top solid.
    for yy in range(7, 12):
        home.walk[yy][3] = True

    interior.room(lantern, 3, 3, 8, 8, True)
    interior.window(lantern, 3, 1)
    interior.window(lantern, 5, 1, 4)
    interior.window(lantern, 9, 1)
    beacon = Image.new("RGBA", (96, 128))
    b = ImageDraw.Draw(beacon)
    b.ellipse((4, 101, 91, 125), fill=(41, 51, 57, 255), outline=(146, 148, 128, 255), width=2)
    b.rectangle((34, 75, 61, 111), fill=(94, 100, 96, 255))
    b.rectangle((40, 75, 55, 109), fill=(135, 139, 122, 255))
    b.ellipse((12, 70, 83, 91), fill=(67, 77, 80, 255), outline=(158, 143, 103, 255), width=2)
    b.rectangle((20, 22, 75, 75), fill=(99, 94, 70, 255))
    b.ellipse((20, 8, 75, 36), fill=(157, 139, 88, 255), outline=(51, 61, 66, 255), width=2)
    b.rectangle((28, 25, 67, 75), fill=(120, 128, 112, 255))
    for yy in range(26, 75, 6):
        b.line((30, yy, 65, yy), fill=(180, 175, 128, 255), width=2)
    for xx in [20, 24, 68, 72]:
        b.rectangle((xx, 24, xx + 3, 79), fill=(68, 74, 68, 255))
    b.ellipse((18, 73, 77, 87), fill=(123, 114, 82, 255), outline=(57, 66, 67, 255), width=2)
    b.rectangle((44, 0, 51, 13), fill=(76, 85, 81, 255))
    interior.surface(lantern, beacon, 5, 2, True)
    interior.prop(lantern, interior.ARCHIVE, 3, 6, 2, 2)
    interior.prop(lantern, interior.BOOK, 4, 8, 1, 1, False)
    interior.stairs(lantern, 5, 9, False)
    lantern.rect(6, 11, 1, 1, interior.itile(interior.floor_tile(True)), walk=True)
    interior.prop(lantern, interior.STOOL, 9, 8, 1, 1, False)
    glow = Image.new("RGBA", (96, 128))
    g = ImageDraw.Draw(glow)
    for yy in range(26, 75, 6):
        g.rectangle((30, yy, 65, yy + 2), fill=(255, 221, 144, 180))
    g.rectangle((43, 29, 51, 70), fill=(255, 232, 174, 130))
    save_png(glow, paths.game / "Graphics/Pictures/Tidebound_Beacon_Glow.png")

    interior.room(basement, 3, 4, 20, 13, True)
    interior.stairs(basement, 5, 12)
    for x in [10, 13, 20]:
        interior.prop(basement, interior.ARCHIVE, x, 4, 2, 2)
    interior.prop(basement, interior.SHELF, 4, 8, 2, 2)
    interior.prop(basement, interior.ARCHIVE, 20, 8, 2, 2)
    interior.prop(basement, interior.BASIN, 9, 13, 1, 1)
    interior.prop(basement, interior.ARCHIVE, 14, 13, 2, 2)
    for x in [15, 18]:
        for y in [2, 3, 4]:
            interior.surface(basement, interior.wall(True).crop((0, 0, 32, 32)), x, y, True)

    interior.room(vault, 3, 3, 22, 16, True)
    for x in [4, 7, 19, 22]:
        interior.prop(vault, interior.ARCHIVE, x, 3, 2, 2)
    for x in [4, 22]:
        for y in [7, 12]:
            interior.prop(vault, interior.ARCHIVE, x, y, 2, 2)
    for y in range(7, 18):
        for x in [11, 12, 13]:
            im = interior.floor_tile(True)
            dr = ImageDraw.Draw(im)
            if x in [11, 13]:
                dr.line(
                    (3 if x == 11 else 28, 0, 3 if x == 11 else 28, 31),
                    fill=(143, 142, 121, 255),
                    width=2,
                )
            vault.layers[0][y][x] = interior.itile(im)
    for x in [8, 17]:
        interior.prop(vault, interior.CABINET, x, 14, 2, 2)
    vault.rect(12, 18, 1, 1, interior.itile(interior.floor_tile(True)), walk=True)
    for m in [bedroom, home, lantern, basement, vault]:
        for name, x, y, trigger, blocks in m.targets:
            if blocks:
                m.walk[y][x] = False


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
    (paths.tools / "generated" / "lighthouse_manifest.json").write_text(
        json.dumps(
            {
                "maps": [101, 104, 107, 110, 111],
                "tileset": id,
                "tiles": len(interior.interior_tiles),
                "revision": 1,
            },
            indent=2,
        )
    )
