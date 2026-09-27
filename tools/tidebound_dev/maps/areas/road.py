import math
import json
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from ...files import save_png
from ..model import table
from PIL import Image, ImageDraw
from ..model import Map, tile
from ..registry import MAPS, ACTORS
from ..shoreline import coastal_shoreline
from ..landscape import shade_water


def build(paths, palette):
    road = Map(MAPS["road"], "The South Coast Road", 56, 84, 1, 96)
    road.polygon(
        [
            (17, 1),
            (25, 1),
            (25, 6),
            (34, 6),
            (38, 11),
            (40, 19),
            (38, 23),
            (36, 27),
            (40, 33),
            (41, 45),
            (38, 55),
            (33, 64),
            (20, 64),
            (16, 59),
            (13, 50),
            (15, 40),
            (14, 32),
            (17, 27),
            (16, 20),
            (13, 16),
            (14, 8),
        ],
        tile(1, 0),
    )
    road.polygon([(14, 8), (16, 8), (17, 16), (19, 19), (18, 23), (16, 20), (13, 16)], 192)
    road.polygon([(15, 31), (17, 32), (17, 40), (16, 49), (19, 58), (17, 59), (13, 50)], 192)
    road.rect(17, 4, 3, 15, tile(2, 27), walk=True)
    road.rect(18, 17, 10, 3, tile(2, 13), walk=True)
    road.rect(25, 17, 3, 35, tile(2, 13), walk=True)
    road.rect(25, 42, 12, 3, tile(2, 13), walk=True)
    road.rect(25, 50, 3, 9, tile(2, 27), walk=True)
    # A narrow timber crossing visibly explains the first thief's chokepoint.
    road.rect(13, 24, 29, 2, 96, walk=False)
    road.rect(25, 24, 3, 2, tile(6, 150), walk=True)
    road.stamp(0, 227, 4, 4, 34, 38)
    road.rect(35, 41, 1, 1, tile(2, 13), walk=True)
    road.door(18, 4, 102, 54, 50, 8, cue="north")
    road.event(
        "Wild:NATU:shorebird",
        20,
        10,
        "Tidebound::NeighborQuest.wild(:shorebird)",
        "Pokemon 01",
        opacity=0,
        move=1,
        species="NATU",
        role="neighbor_wild",
        state="shorebird",
    )
    road.event(
        "Wild:ZIGZAGOON:shoreforager",
        22,
        18,
        "Tidebound::NeighborQuest.wild(:shoreforager)",
        "Pokemon 01",
        opacity=0,
        move=1,
        species="ZIGZAGOON",
        role="neighbor_wild",
        state="shoreforager",
    )
    road.event(
        ACTORS["road_thief"], 26, 26, "Tidebound::NeighborQuest.first_thief", "trainer_YOUNGSTER"
    )
    for x in range(25, 28):
        road.event("Thief crossing", x, 24, "Tidebound::NeighborQuest.first_thief", trigger=1)
    road.event(
        ACTORS["running_thief"],
        31,
        43,
        "Tidebound::NeighborQuest.witness_hideout",
        "trainer_CAMPER",
        opacity=0,
    )
    for y in range(42, 45):
        road.event(
            "Storehouse approach", 29, y, "Tidebound::NeighborQuest.witness_hideout", trigger=1
        )
    road.event(
        "Storehouse door", 35, 41, "Tidebound::NeighborQuest.hideout_door", trigger=1, cue="south"
    )
    road.event("Road traveller", 23, 39, "Tidebound::NeighborQuest.rest", "NPC 01", blocks=True)
    road.event("Fire", 24, 40, "Tidebound::NeighborQuest.rest", blocks=True, role="fire")
    road.event(
        "Southern steps",
        26,
        53,
        'pbMessage("A narrow trail bends down to a pond. Fishing lines hang motionless over the water.")',
    )
    road.event(
        "Torn wrapping",
        31,
        34,
        'pbMessage("Straw packing, and an empty oil-shop bag. They came this way.")',
    )
    road.event("Shore flowers", 16, 10, 'pbMessage("Small flowers turn away from the salt wind.")')

    for x, y, item in [(21, 16, "ORANBERRY"), (28, 38, "SITRUSBERRY")]:
        road.event(
            "Berry:" + item,
            x,
            y,
            f"Tidebound::FieldDetails.berry({road.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
            direction=8,
        )
    road.event(
        "Coast lamp:storehouse",
        33,
        42,
        'pbMessage("The wick has been trimmed recently.")',
        role="coast_lamp",
    )

    road.rect(37, 42, 8, 3, tile(2, 27), walk=True)
    road.event("Dock city", 44, 43, "Tidebound::VaultVisit.city_gate", trigger=1, cue="east")
    road.event("Dock road sign", 42, 41, 'pbMessage("DOCKS AND MUSEUM - EAST")')
    coastal_shoreline(road)
    # SOUTH ROAD: scrub woodland on the upper slopes, rocky tidal neck and lower bay.
    # Steep western bank beside the pursuit route.
    for y in range(33, 36):
        road.walk[y][17] = False
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

    shade_water(road)
    # A visible, stationary duck at a clear roadside pool approach. Static event avoids
    # wandering into grass battle triggers or hiding in existing scenery.
    road.event(
        "Wild:PSYDUCK:shoreduck",
        19,
        62,
        "Tidebound::Pond.psyduck",
        "Pokemon 01",
        opacity=0,
        species="PSYDUCK",
        role="shore_duck",
    )
    for x, y in [(27, 36), (26, 36), (27, 35), (27, 37)]:
        road.layers[1][y][x] = 0
        road.layers[2][y][x] = 0
        road.walk[y][x] = True

    paint_pond(paths, palette, road)
    return road


def paint_pond(paths, palette, road):
    """Southern pond decoration on the coast road.
    A compact road-only atlas leaves other maps and their tile IDs untouched.
    """
    for y in range(48, road.h):
        for x in range(road.w):
            road.layers[0][y][x] = 96
            road.layers[1][y][x] = road.layers[2][y][x] = 0
            road.walk[y][x] = False
    road.polygon(
        [
            (17, 48),
            (37, 48),
            (43, 54),
            (44, 65),
            (40, 74),
            (34, 77),
            (19, 76),
            (12, 71),
            (11, 59),
            (14, 53),
        ],
        tile(1, 0),
    )
    water = set()
    for y in range(56, 72):
        for x in range(19, 38):
            if ((x - 28) / 8.3) ** 2 + ((y - 63) / 7.4) ** 2 < 1 + 0.075 * math.sin(y * 2 + x):
                water.add((x, y))
    island = {(x, y) for y in range(61, 64) for x in range(26, 29)} - {(26, 61), (28, 61)}
    water -= island
    for x, y in water:
        road.layers[0][y][x] = 48
        road.walk[y][x] = False
    for x, y in island:
        road.layers[0][y][x] = tile(2, 27)
        road.walk[y][x] = True
    coastal_shoreline(road)
    for key, x, y, direction in [("toma", 25, 55, 2), ("ida", 38, 63, 4), ("renzo", 29, 72, 8)]:
        road.event(
            "Pond fisher " + key,
            x,
            y,
            f"Tidebound::Pond.fisher(:{key})",
            "trainer_FISHERMAN",
            blocks=True,
            direction=direction,
        )
    road.event(
        "Berry:ORANBERRY",
        20,
        54,
        "Tidebound::FieldDetails.berry(108, 20, 54, :ORANBERRY)",
        "berrytree_ORANBERRY",
        role="berry",
        direction=8,
    )
    road.event("Pond hidden cache", 13, 69, "Tidebound::Pond.hidden_item")
    road.event(
        "Pond obelisk (Surf)",
        27,
        61,
        'pbMessage("A narrow stone, cold beneath your hand. Water has worn the marks too shallow to read.")',
        blocks=True,
    )
    road.event(
        "Old fishing basket",
        37,
        70,
        'pbMessage("A basket repaired with three different kinds of twine. A tiny fish has been carved into the handle.")',
    )
    p = palette.painter(road)
    p.reserve(24, 48, 5, 8)
    for box in [(17, 55, 3, 14), (36, 55, 4, 17), (21, 72, 16, 2), (19, 53, 18, 3)]:
        p.reserve(*box)
    hidden = [
        (17, 58),
        (16, 58),
        (15, 58),
        (15, 59),
        (15, 60),
        (14, 60),
        (14, 61),
        (14, 62),
        (14, 63),
        (14, 64),
        (14, 65),
        (14, 66),
        (14, 67),
        (14, 68),
        (14, 69),
        (13, 69),
    ]
    for x, y in hidden:
        p.reserve(x, y, 1, 1)
    for box in [(16, 51, 5, 6), (38, 65, 4, 5)]:
        palette.clearing(p, *box)
    palette.groves(
        p,
        [
            (14, 57, 2, 6),
            (15, 70, 3, 4),
            (22, 76, 6, 2),
            (37, 75, 5, 2),
            (42, 58, 2, 6),
            (40, 51, 4, 3),
        ],
        160,
    )
    for x, y in [(12, 60), (12, 62), (12, 64), (12, 66), (15, 61), (15, 63), (15, 65), (15, 67)]:
        p.plant(palette.ROUND, x, y, 2, 2, check=False)
    for x, y in hidden:
        road.walk[y][x] = True
        road.layers[0][y][x] = tile(1, 0)
        if (x + y) % 5 == 0:
            p.decal(palette.art(6, 0), x, y)
    for x, y, s in [(15, 52, 2), (40, 54, 2), (39, 71, 2), (19, 72, 2), (31, 75, 2)]:
        palette.rock_group(p, x, y, s, True)
    for x, y in [(20, 58), (21, 56), (34, 56), (36, 59), (35, 68), (22, 70), (20, 66)]:
        if (x, y) not in water and (x, y) not in island:
            p.decal(palette.art(6, 0), x, y)
    for args in [(18, 53, 3, 3), (40, 67, 2, 3)]:
        palette.grass_patch(p, *args)
    for x, y in [(23, 54), (24, 54), (36, 72), (37, 73)]:
        p.decal(palette.WHITE, x, y)
    for x, y in [(24, 56), (25, 56), (26, 56)]:
        if (x, y) not in water:
            road.layers[0][y][x] = tile(6, 150)
    basket = Image.new("RGBA", (32, 32))
    bd = ImageDraw.Draw(basket)
    bd.ellipse((5, 24, 29, 31), fill=(27, 37, 40, 170))
    bd.arc((8, 4, 25, 23), 180, 360, fill=(126, 113, 78), width=2)
    bd.polygon([(6, 16), (27, 16), (25, 29), (9, 29)], fill=(108, 95, 66), outline=(50, 58, 50))
    for yy in [19, 23, 27]:
        bd.line((9, yy, 25, yy), fill=(153, 136, 92), width=2)
    p.decal(basket, 37, 70)
    obelisk = Image.new("RGBA", (32, 96))
    od = ImageDraw.Draw(obelisk)
    od.ellipse((3, 82, 29, 94), fill=(32, 39, 42, 180))
    od.polygon(
        [(5, 85), (9, 11), (17, 3), (24, 12), (27, 85)], fill=(124, 135, 139), outline=(50, 64, 70)
    )
    od.polygon([(17, 3), (24, 12), (27, 85), (19, 89), (17, 20)], fill=(81, 99, 106))
    od.line([(10, 17), (9, 77)], fill=(173, 182, 179), width=2)
    od.line([(14, 34), (19, 38), (14, 43), (18, 47)], fill=(67, 83, 89), width=2)
    od.line([(21, 58), (17, 65), (21, 76)], fill=(52, 72, 79), width=2)
    p.plant(obelisk, 27, 59, 1, 3, check=False, solid=False)
    road.walk[61][27] = False
    p.finish()
    assert not any(336 <= v < 384 for layer in road.layers for row in layer for v in row)
    for x, y in water:
        road.layers[0][y][x] = 336 + road.layers[0][y][x] % 48
    (paths.tools / "generated" / "pond_manifest.json").write_text(
        json.dumps(
            {
                "map": 108,
                "water": sorted(water),
                "island": sorted(island),
                "hidden_path": hidden,
                "grass_type": "PondGrass",
                "duck": [19, 62],
                "obelisk": [27, 61],
            },
            indent=2,
        )
        + "\n"
    )
    (paths.tools.parent / "src" / "generated/pond_geometry.rb").write_text(
        "# Generated by maps/areas/road.py.\nmodule Tidebound::PondGeometry\n  WATER = "
        + str(sorted(water)).replace("(", "[").replace(")", "]")
        + ".freeze\n  ISLAND = "
        + str(sorted(island)).replace("(", "[").replace(")", "]")
        + ".freeze\nend\n"
    )


def save_tileset(paths, palette, road):
    source = palette._native
    used = sorted(
        {v for layer in road.layers for row in layer for v in row if v >= 384 and v != 391}
    )
    remap = {v: 392 + i for i, v in enumerate(used)}
    remap[391] = 391
    road.source_tiles = {new: old for old, new in remap.items()}
    atlas = Image.new("RGBA", (256, math.ceil((8 + len(used)) / 8) * 32))
    atlas.paste(palette.art(0, 0, 8, 1), (0, 0))
    for old, new in remap.items():
        if old == 391:
            continue
        im = (
            palette._tile_images[old - palette._base_count][0]
            if old >= palette._base_count
            else source.crop(
                (
                    ((old - 384) % 8) * 32,
                    ((old - 384) // 8) * 32,
                    ((old - 384) % 8 + 1) * 32,
                    ((old - 384) // 8 + 1) * 32,
                )
            )
        )
        atlas.alpha_composite(im, (((new - 384) % 8) * 32, ((new - 384) // 8) * 32))
    for layer in road.layers:
        for row in layer:
            for x, v in enumerate(row):
                if v >= 384:
                    row[x] = remap[v]
    save_png(atlas, paths.game / "Graphics/Tilesets/TideboundPond.png")
    tilesets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    pid = next(
        (i for i, t in enumerate(tilesets) if t and t.attributes.get("@name") == "Tidebound Pond"),
        len(tilesets),
    )
    ts = loads(writes(tilesets[road.tileset]))
    ts.attributes.update({"@id": pid, "@name": "Tidebound Pond", "@tileset_name": "TideboundPond"})
    ts.attributes["@autotile_names"][6] = "Still water"
    for key in ["@passages", "@priorities", "@terrain_tags"]:
        ts.attributes[key] = table([0] * (392 + len(used)), 392 + len(used))
    if pid == len(tilesets):
        tilesets.append(ts)
    else:
        tilesets[pid] = ts
    road.tileset = pid
    (paths.game / "Data/Tilesets.rxdata").write_bytes(writes(tilesets))
