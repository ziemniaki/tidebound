from PIL import Image, ImageDraw
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import json
import struct

from .model import tile, table
import math
from collections import deque
from .shoreline import shoreline


def decorate(paths, palette, coast, forest, road, docks):
    # LISTENING WOOD: the path threads three groves, a key clearing, pool and camp.
    palette.clear_nature(forest)
    f = palette.painter(forest)
    f.reserve(12, 7, 5, 6)
    f.reserve(7, 19, 8, 5)
    f.reserve(25, 8, 5, 5)
    f.reserve(16, 0, 3, 30)
    for area in [
        (6, 14, 6, 5),
        (11, 17, 6, 2),
        (20, 4, 4, 4),
        (19, 7, 5, 3),
        (20, 17, 5, 5),
        (19, 19, 3, 3),
    ]:
        palette.clearing(f, *area)
    # Irregular pool bank; retain the original encounter square and approach.
    for x, y in [(27, 7), (28, 7), (29, 7), (30, 8), (30, 9)]:
        forest.layers[0][y][x] = 144
        forest.walk[y][x] = False
    shoreline(forest)
    palette.groves(
        f,
        [
            (4, 3, 4, 3),
            (5, 12, 3, 5),
            (7, 26, 5, 3),
            (12, 15, 3, 3),
            (23, 2, 4, 3),
            (32, 7, 3, 5),
            (30, 19, 4, 5),
            (24, 26, 5, 3),
        ],
        240,
    )
    for x, y in [(24, 7), (30, 10), (31, 12)]:
        palette.rock_group(f, x, y, 1)
    # Keys sit among a colony of small white flowers, with a clear approach from path.
    for x, y in [(13, 8), (14, 8), (15, 8), (13, 9), (14, 10), (15, 10), (13, 11), (14, 12)]:
        f.decal(palette.WHITE, x, y)
    for args in [(8, 16, 4, 3), (22, 5, 3, 3), (22, 19, 4, 3)]:
        palette.grass_patch(f, *args)
    # A continuous canopy encloses the wood; overlapping crowns hide the map boundary.
    for side in [0, 33]:
        for y in range(0, 28, 2):
            f.plant(palette.PINE if y % 6 else palette.ROUND, side, y, 3, 3, check=False)
    for x in range(2, 33, 2):
        if not 14 <= x <= 18:
            f.plant(palette.ROUND if x % 6 else palette.PINE, x, 0, 3, 3, check=False)
        if not 14 <= x <= 20:
            f.plant(palette.PINE if x % 4 else palette.ROUND, x, 27, 3, 3, check=False)
    f.finish()

    # SHIOHAMA: a rock spine, sheltered garden and woodland thinning into village.
    palette.clear_nature(coast)
    c = palette.painter(coast)
    # Preserve Pookie, robbery and seller walking routes explicitly, beyond event buffers.
    c.reserve(31, 34, 7, 7)
    c.reserve(44, 31, 7, 10)
    c.reserve(47, 23, 3, 13)
    c.reserve(48, 34, 13, 3)
    c.reserve(57, 35, 4, 7)
    c.reserve(59, 40, 20, 2)
    c.reserve(52, 42, 5, 11)
    c.reserve(34, 38, 14, 4)
    # Small garden and house approaches stay open; village margins become thickets.
    c.reserve(28, 30, 10, 4)
    palette.groves(
        c,
        [
            (47, 7, 4, 5),
            (56, 8, 4, 5),
            (60, 19, 3, 4),
            (43, 23, 2, 2),
            (52, 29, 3, 3),
            (61, 32, 3, 3),
        ],
        160,
    )
    # Trees shelter the backs of houses; the exposed lighthouse has no tall trees.
    for x, y in [(49, 28), (59, 24), (61, 30), (50, 38)]:
        c.plant(palette.AUTUMN, x, y, 2, 2)
    for x, y, s in [
        (25, 29, 3),
        (25, 36, 3),
        (35, 25, 3),
        (37, 33, 3),
        (30, 41, 3),
        (39, 41, 2),
        (44, 43, 2),
        (62, 37, 3),
        (27, 26, 2),
        (28, 40, 2),
        (38, 29, 2),
        (25, 33, 2),
        (38, 38, 2),
        (53, 49, 1),
        (57, 48, 2),
    ]:
        palette.rock_group(c, x, y, s, True)
    # Tide-washed skerries continue the lighthouse's geology into the sea, not random clutter.
    for x, y, s in [(22, 31, 2), (23, 38, 2), (27, 44, 2), (32, 46, 1), (38, 44, 1), (21, 35, 1)]:
        palette.rock_group(c, x, y, s, True)
    # Small planted beds sit on both sides of the tower, encircled by low stone edging.
    for cells in [
        [(29, 31), (29, 32), (30, 32), (30, 33)],
        [(35, 30), (35, 31), (36, 31), (35, 32), (36, 32), (36, 33)],
    ]:
        for x, y in cells:
            if coast.layers[1][y][x] == 0:
                c.ground(x, y, 0.34)
                c.decal(palette.WHITE if (x + y) % 3 == 0 else palette.FLOWER, x, y)
                # Low edging is visual only: garden interactions stay reachable.
                edging = Image.new("RGBA", (32, 32))
                ed = ImageDraw.Draw(edging)
                for xx in [2, 10, 20]:
                    ed.rectangle((xx, 27, xx + 7, 30), fill=(103, 112, 103, 255))
                    ed.line((xx, 27, xx + 6, 27), fill=(155, 165, 145, 255), width=1)
                c.overlay.alpha_composite(edging, (x * 32, y * 32))
    for x, y in [(29, 34), (30, 35), (36, 34), (37, 37)]:
        c.decal(palette.art(6, 0), x, y)
    # Beach grass forms a narrow sheltered drift, away from the primary approach.
    for x, y in [(49, 39), (50, 39), (51, 39), (51, 40), (55, 38), (56, 38), (61, 41)]:
        c.decal(palette.art(6, 0), x, y)
    palette.scree(
        c,
        [(24, 25, 28, 42), (28, 24, 38, 28), (37, 28, 40, 38), (27, 41, 38, 44), (62, 33, 66, 39)],
    )
    c.finish()
    # Keep the original gate, avoiding accidental new entry through the tree line.
    for y in range(23):
        for x in range(coast.w):
            coast.walk[y][x] = False
    for x in (47, 49):
        coast.walk[23][x] = False

    # SOUTH ROAD: scrub woodland on the upper slopes, rocky tidal neck and lower bay.
    palette.clear_nature(road)
    r = palette.painter(road)
    r.reserve(24, 21, 5, 9)
    r.reserve(28, 41, 17, 4)
    r.reserve(21, 37, 9, 5)
    for area in [
        (20, 7, 4, 5),
        (19, 10, 4, 3),
        (29, 16, 5, 5),
        (27, 18, 3, 2),
        (29, 28, 5, 5),
        (27, 30, 3, 2),
        (29, 46, 5, 5),
        (27, 48, 3, 2),
    ]:
        palette.clearing(r, *area)
    palette.groves(
        r,
        [
            (23, 3, 3, 3),
            (32, 9, 4, 3),
            (35, 17, 3, 4),
            (19, 32, 3, 3),
            (34, 31, 3, 4),
            (19, 47, 3, 4),
            (33, 51, 3, 4),
            (26, 60, 5, 3),
        ],
        170,
    )
    for x, y, s in [
        (14, 21, 3),
        (20, 22, 2),
        (29, 22, 3),
        (35, 22, 3),
        (36, 28, 2),
        (14, 40, 2),
        (14, 48, 3),
        (18, 56, 2),
        (35, 54, 3),
        (29, 64, 2),
    ]:
        palette.rock_group(r, x, y, s, True)
    for x, y, s in [(11, 46, 2), (12, 51, 1), (39, 52, 2), (40, 28, 1)]:
        palette.rock_group(r, x, y, s, True)
    for args in [(21, 9, 3, 3), (31, 18, 3, 3), (31, 30, 3, 3), (31, 48, 3, 3)]:
        palette.grass_patch(r, *args)
    for x, y in [(16, 10), (16, 11), (17, 10), (22, 38), (28, 37)]:
        r.decal(palette.WHITE, x, y)
    palette.scree(
        r,
        [(12, 20, 24, 24), (29, 21, 39, 24), (12, 33, 16, 53), (35, 53, 39, 60), (18, 61, 34, 65)],
    )
    r.finish()

    # DOCKS: a few tended courtyard plots, salt grass outside the working quays.
    d = palette.painter(docks)
    dock_event_buffer = {
        (xx, yy)
        for _, x, y, trigger, _ in docks.targets
        if trigger != 3
        for yy in range(y - 1, y + 2)
        for xx in range(x - 1, x + 2)
    }
    for x, y, w, h in [
        (26, 10, 10, 5),
        (54, 16, 8, 3),
        (12, 22, 7, 2),
        (28, 34, 3, 4),
        (58, 33, 4, 6),
    ]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if docks.layers[1][yy][xx] == 0 and (xx, yy) not in dock_event_buffer:
                    docks.layers[0][yy][xx] = tile(1, 0)
                    d.protected.discard((xx, yy))
    for x, y in [(27, 10), (32, 11), (59, 16), (58, 34)]:
        d.plant(palette.AUTUMN, x, y, 2, 2)
    for x, y in [
        (30, 12),
        (33, 13),
        (54, 17),
        (56, 17),
        (13, 22),
        (14, 22),
        (17, 22),
        (28, 35),
        (29, 36),
        (60, 37),
    ]:
        d.decal(palette.WHITE if x % 2 else palette.art(6, 0), x, y)
    for x, y, s in [(7, 33, 2), (11, 38, 2), (15, 43, 1), (61, 40, 2)]:
        palette.rock_group(d, x, y, s, True)
    d.finish()

    # Water depth is legible without compromising the animated native sea or vast horizon.
    # Only the story outdoor maps receive this cloned tileset; demo/astral remain untouched.
    tilesets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    landscape_id = next(
        (
            i
            for i, t in enumerate(tilesets)
            if t and t.attributes.get("@name") == "Tidebound Landscape"
        ),
        len(tilesets),
    )
    ts = loads(writes(tilesets[1]))
    ts.attributes["@id"] = landscape_id
    ts.attributes["@name"] = "Tidebound Landscape"
    ts.attributes["@tileset_name"] = "TideboundLandscape"
    for m in [coast, forest, road, docks]:
        m.tileset = landscape_id
    # Keep the native wave animations, tint only blue water pixels (not shore rock).
    for name, source, factors in [
        ("Tidebound Shallows", "Sea", (0.98, 1.13, 1.03)),
        ("Tidebound Open Sea", "Sea without shore", (0.87, 0.98, 1.0)),
        ("Tidebound Deep Sea", "Sea without shore", (0.76, 0.87, 0.94)),
    ]:
        im = Image.open(paths.game / "Graphics/Autotiles" / f"{source}.png").convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                red, green, blue, a = px[x, y]
                if blue > red and blue > green:
                    px[x, y] = (
                        int(red * factors[0]),
                        min(255, int(green * factors[1])),
                        min(255, int(blue * factors[2])),
                        a,
                    )
        im.save(paths.game / "Graphics/Autotiles" / f"{name}.png")
    ts.attributes["@autotile_names"][:3] = [
        "Tidebound Shallows",
        "Tidebound Open Sea",
        "Tidebound Deep Sea",
    ]
    for m in [coast, road, docks]:
        dist = [[999] * m.w for _ in range(m.h)]
        q = deque()
        for y in range(m.h):
            for x in range(m.w):
                v = m.layers[0][y][x]
                if v >= 192 and v not in (tile(6, 150), tile(6, 151)):
                    dist[y][x] = 0
                    q.append((x, y))
        while q:
            x, y = q.popleft()
            for xx, yy in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= xx < m.w and 0 <= yy < m.h and dist[yy][xx] > dist[y][x] + 1:
                    dist[yy][xx] = dist[y][x] + 1
                    q.append((xx, yy))
        for y in range(m.h):
            for x in range(m.w):
                v = m.layers[0][y][x]
                if 48 <= v < 192:
                    distance = dist[y][x]
                    if distance <= 2:
                        m.layers[0][y][x] = 48 + (v % 48 if v < 96 else 0)
                    elif distance <= 7:
                        m.layers[0][y][x] = 96
                    else:
                        m.layers[0][y][x] = 144
    # Extend native tables and atlas deterministically. Base tile IDs and window pixels stay exact.
    height = (palette._native.height // 32 + math.ceil(len(palette._tile_images) / 8)) * 32
    atlas = Image.new("RGBA", (256, height))
    atlas.alpha_composite(palette._native)
    for i, (im, tag) in enumerate(palette._tile_images):
        atlas.alpha_composite(im, ((i % 8) * 32, palette._native.height + (i // 8) * 32))
    assert height <= 16384, "Keep landscape tileset within Mac 16K texture limit"
    atlas.save(paths.game / "Graphics/Tilesets/TideboundLandscape.png")
    for key in ["@passages", "@priorities", "@terrain_tags"]:
        data = ts.attributes[key]._dump()
        header = struct.unpack("<5i", data[:20])
        values = list(struct.unpack("<" + "h" * header[4], data[20:]))
        values = values[: palette._base_count] + [0] * max(0, palette._base_count - len(values))
        values += [tag if key == "@terrain_tags" else 0 for im, tag in palette._tile_images]
        ts.attributes[key] = table(values, len(values))
    if landscape_id == len(tilesets):
        tilesets.append(ts)
    else:
        tilesets[landscape_id] = ts
    (paths.game / "Data/Tilesets.rxdata").write_bytes(writes(tilesets))
    (paths.tools / "generated" / "landscape_manifest.json").write_text(
        json.dumps(
            {
                "revision": 2,
                "maps": [102, 103, 108, 112],
                "tileset_id": landscape_id,
                "baked_tiles": len(palette._tile_images),
                "trees_and_rocks": {str(p.m.id): len(p.sprites) for p in [c, f, r, d]},
            },
            indent=2,
        )
    )
