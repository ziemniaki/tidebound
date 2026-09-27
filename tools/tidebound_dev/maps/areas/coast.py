from rubymarshal.reader import loads
from rubymarshal.writer import writes
from ...files import save_png
from ..harbor_art import wooden_village
from PIL import Image, ImageDraw
from ..model import Map, tile
from ..registry import MAPS, ACTORS
from ..shoreline import coastal_shoreline
from ..landscape import shade_water


def build(palette):
    coast = Map(MAPS["coast"], "Shiohama", 108, 88, 1, 96)
    # The ocean continues far past every reachable camera position.
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [
                (3, 7),
                (7, 5),
                (12, 5),
                (14, 8),
                (16, 12),
                (14, 16),
                (14, 19),
                (11, 22),
                (6, 22),
                (2, 19),
                (1, 13),
            ]
        ],
        tile(2, 27),
    )
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [(4, 8), (11, 7), (13, 10), (13, 16), (11, 20), (5, 20), (3, 16)]
        ],
        tile(1, 0),
    )
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [
                (20, -18),
                (38, -18),
                (39, 7),
                (41, 12),
                (39, 17),
                (37, 22),
                (33, 25),
                (25, 25),
                (21, 22),
                (19, 16),
            ]
        ],
        tile(1, 0),
    )
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [(22, 18), (29, 17), (36, 19), (37, 22), (33, 25), (25, 25), (21, 22)]
        ],
        192,
    )
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [
                (11, 18),
                (15, 18),
                (17, 19),
                (21, 18),
                (23, 20),
                (20, 22),
                (16, 21),
                (13, 22),
                (11, 20),
            ]
        ],
        tile(2, 27),
    )
    coast.path(*coast.absolute(7, 14), 4, 7, True)
    coast.path(*coast.absolute(10, 18), 7, 3, True)
    coast.path(*coast.absolute(16, 19), 8, 3, True)
    coast.path(*coast.absolute(23, 3), 3, 19)
    coast.path(*coast.absolute(24, 14), 13, 3)
    coast.path(*coast.absolute(33, 15), 4, 7)
    # Weathered timber projects above water; it is not a dirt peninsula.
    coast.rect(*coast.absolute(35, 20), 20, 1, tile(6, 150), walk=True)
    coast.rect(*coast.absolute(35, 21), 20, 1, tile(6, 151), walk=True)
    coast.rect(*coast.absolute(35, 22), 20, 1, tile(6, 152), z=1, walk=False)
    coast.rect(*coast.absolute(52, 19), 3, 1, tile(6, 150), walk=True)
    coast.rect(*coast.absolute(55, 20), 1, 2, tile(7, 151), z=1, walk=False)
    coast.stamp(5, 444, 3, 8, *coast.absolute(7, 7))
    coast.stamp(0, 227, 4, 4, *coast.absolute(20, 8))
    coast.stamp(0, 227, 4, 4, *coast.absolute(28, 7))
    coast.stamp(4, 228, 4, 4, *coast.absolute(34, 7))
    # Open corner beside the oil-shop roof.
    coast.rect(44, 28, 1, 1, 0, z=1, walk=True)
    coast.door(*coast.absolute(8, 15), 101, 10, 12, 8, cue="north")
    coast.walk[31][45] = True
    coast.event(
        "Shop door",
        *coast.absolute(21, 11),
        "Tidebound::Interactions.shop_door",
        trigger=1,
        cue="south",
    )
    coast.event(
        ACTORS["seller_outside"],
        *coast.absolute(22, 12),
        "Tidebound::Interactions.outside_seller",
        "NPC 10",
    )
    coast.event(
        ACTORS["pookie_outside"],
        *coast.absolute(11, 16),
        "Tidebound::Opening.pookie",
        "Pokemon 01",
        opacity=0,
    )
    coast.event(
        "Oil shop sign",
        *coast.absolute(23, 12),
        'pbMessage("LAMP OIL. Please ask the seller for assistance.\nA small bottle hangs beside the lettering.")',
    )
    coast.event(
        "Empty house",
        *coast.absolute(29, 11),
        'pbMessage("The door has swollen in its frame. Nobody answers.")',
    )
    coast.event(
        "Seated neighbour",
        *coast.absolute(31, 18),
        'pbMessage("Young as ever, aren\'t you? I wish I knew your secret.")\npbMessage("Your mother still lights the tower every night. I used to complain that it shone through my curtains.")',
        "NPC 14",
        blocks=True,
    )
    coast.event("Pier", *coast.absolute(54, 20), "Tidebound::Opening.pier", trigger=1)
    coast.event("Lapras", *coast.absolute(56, 23), "", role="lapras")
    coast.event(
        "Tide bell",
        *coast.absolute(18, 20),
        'pbMessage("A bell with no clapper. Salt has filled the inscription.")',
        role="tide_bell",
    )
    coast.event(
        "Forest path",
        *coast.absolute(24, 3),
        "Tidebound::Opening.forest_gate",
        trigger=1,
        cue="north",
    )

    # Only the authored entrance crosses into the northern forest.
    for x in range(20, 40):
        coast.walk[22][x + 24] = False
    for x in (23, 25):
        coast.walk[23][x + 24] = False
    coast.event(
        "Headland flowers",
        *coast.absolute(11, 12),
        'pbMessage("Late flowers, sheltered by a ring of flat stones.\nSomeone has tied the weakest stems to little sticks.")',
    )
    coast.event(
        "Sea glass",
        *coast.absolute(29, 24),
        'pbMessage("Green glass, worn smooth by the water.\nFor a moment, it catches the light.")',
        role="sea_glass",
    )
    coast.event(
        "Coast lamp:home",
        *coast.absolute(5, 16),
        'pbMessage("Mother lights this little lamp before dusk.\nSo you can always find the path home.")',
        role="coast_lamp",
    )
    coast.event(
        "Coast lamp:pier",
        *coast.absolute(52, 19),
        'pbMessage("A little oil lamp. Someone still tends it, even with the boats gone.")',
        role="coast_lamp",
    )
    coast.event(
        "Mooring rope",
        *coast.absolute(54, 21),
        'pbMessage("An old mooring rope disappears beneath the boards.")',
        role="mooring_rope",
    )

    # Southern rocky path.
    coast.polygon(
        [
            coast.absolute(x, y)
            for x, y in [(28, 23), (32, 23), (33, 28), (32, 32), (28, 32), (27, 28)]
        ],
        tile(2, 27),
    )
    coast.path(*coast.absolute(29, 24), 3, 8, True)
    coast.event(
        "South path",
        *coast.absolute(30, 31),
        "Tidebound::NeighborQuest.south_gate",
        trigger=1,
        cue="south",
    )
    coast.event(
        ACTORS["robbery_youth_one"], *coast.absolute(21, 11), "", "trainer_YOUNGSTER", opacity=0
    )
    coast.event(
        ACTORS["robbery_youth_two"], *coast.absolute(21, 12), "", "trainer_CAMPER", opacity=0
    )
    coast.event(
        "Coast road sign",
        *coast.absolute(31, 29),
        'pbMessage("COAST ROAD - SOUTH. The lettering has been repainted around the rusted nails.")',
    )

    for x, y, item in [(12, 18, "ORANBERRY")]:
        coast.event(
            "Berry:" + item,
            *coast.absolute(x, y),
            f"Tidebound::FieldDetails.berry({coast.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
            direction=8,
        )
    coast.event(
        "Coast lamp:shop",
        *coast.absolute(24, 12),
        'pbMessage("A sheltered flame warms the shopfront.")',
        role="coast_lamp",
    )

    coastal_shoreline(coast)
    # SHIOHAMA: a rock spine, sheltered garden and woodland thinning into village.
    # Steep shore edges are impassable.
    for x, y in [(46, 43), (59, 43), (50, 44)]:
        coast.walk[y][x] = False
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

    shade_water(coast)
    return coast


def save_tileset(paths, coast):
    # A separate atlas gives only Shiohama wooden homes; lighthouse pixels are exact.
    tilesets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    village_id = next(
        (
            i
            for i, t in enumerate(tilesets)
            if t and t.attributes.get("@name") == "Tidebound Village"
        ),
        len(tilesets),
    )
    ts = loads(writes(tilesets[coast.tileset]))
    ts.attributes.update(
        {"@id": village_id, "@name": "Tidebound Village", "@tileset_name": "TideboundVillage"}
    )
    original = Image.open(paths.game / "Graphics/Tilesets/TideboundLandscape.png").convert("RGBA")
    village = wooden_village(original)
    assert (
        village.crop((5 * 32, 444 * 32, 8 * 32, 452 * 32)).tobytes()
        == original.crop((5 * 32, 444 * 32, 8 * 32, 452 * 32)).tobytes()
    )
    save_png(village, paths.game / "Graphics/Tilesets/TideboundVillage.png")
    if village_id == len(tilesets):
        tilesets.append(ts)
    else:
        tilesets[village_id] = ts
    coast.tileset = village_id
    (paths.game / "Data/Tilesets.rxdata").write_bytes(writes(tilesets))
