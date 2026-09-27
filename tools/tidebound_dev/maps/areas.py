from .registry import MAPS, ACTORS

"""Base area definitions; each builder returns an independent map."""
from .model import Map, CoastMap, RoadMap, tile


def build_home():
    home = Map(MAPS["home"], "The Keeper's House", 20, 16, 3)
    home.rect(2, 3, 16, 11, tile(4, 78), walk=True)
    home.rect(2, 2, 16, 2, tile(1, 13), walk=False)
    home.stamp(0, 0, 4, 2, 2, 1)
    home.stamp(0, 0, 4, 2, 6, 1)
    home.stamp(0, 0, 4, 2, 10, 1)
    home.stamp(0, 0, 4, 2, 14, 1)
    home.stamp(0, 151, 2, 2, 3, 4)
    home.stamp(0, 140, 3, 2, 12, 4)  # domestic furnishings
    home.stamp(6, 212, 2, 2, 8, 7)
    home.event(ACTORS["mother"], 12, 7, "Tidebound::Interactions.mother", "NPC 11", blocks=True)
    home.event("Book", 4, 10, "Tidebound::Opening.journal")
    home.stamp(0, 140, 3, 2, 3, 8)
    home.event("Opening", 2, 13, "Tidebound::Opening.home_arrival", trigger=3)
    home.event(
        ACTORS["house_natu"], 6, 5, "Tidebound::Opening.house_pet(:NATU)", "Pokemon 01", opacity=0
    )
    home.event(
        ACTORS["house_makuhita"],
        10,
        9,
        "Tidebound::Opening.house_pet(:MAKUHITA)",
        "Pokemon 01",
        opacity=0,
    )
    home.event(
        ACTORS["house_poochyena"],
        13,
        11,
        "Tidebound::Opening.house_pet(:POOCHYENA)",
        "Pokemon 01",
        opacity=0,
    )
    home.event(
        ACTORS["crate"],
        10,
        10,
        'pbMessage("Bottles wrapped in straw. Maku carries them as carefully as he can.")',
        "Pokemon 01",
        opacity=0,
    )
    home.event(
        "Crate spare",
        12,
        10,
        'pbMessage("One of the boxes Maku is helping Mother put away.")',
        "Pokemon 01",
        opacity=0,
        role="crate",
    )
    home.stamp(1, 237, 2, 2, 6, 3, walk=True)
    home.door(6, 3, 107, 8, 10, 8)
    # This autorun erases itself; persistent story flag prevents repetition on revisit.
    home.rect(10, 14, 1, 1, tile(4, 78), walk=True)
    home.door(10, 14, 102, 32, 36)
    home.stamp(1, 237, 2, 2, 16, 3, walk=True)
    home.door(17, 3, 104, 6, 9)

    return home


def build_coast():
    coast = CoastMap(MAPS["coast"], "Shiohama", 108, 88, 1, 96)
    # The ocean continues far past every reachable camera position.
    coast.polygon(
        [
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
        ],
        tile(2, 27),
    )
    coast.polygon([(4, 8), (11, 7), (13, 10), (13, 16), (11, 20), (5, 20), (3, 16)], tile(1, 0))
    coast.polygon(
        [
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
        ],
        tile(1, 0),
    )
    coast.polygon([(22, 18), (29, 17), (36, 19), (37, 22), (33, 25), (25, 25), (21, 22)], 192)
    coast.polygon(
        [(11, 18), (15, 18), (17, 19), (21, 18), (23, 20), (20, 22), (16, 21), (13, 22), (11, 20)],
        tile(2, 27),
    )
    coast.path(7, 14, 4, 7, True)
    coast.path(10, 18, 7, 3, True)
    coast.path(16, 19, 8, 3, True)
    coast.path(23, 3, 3, 19)
    coast.path(24, 14, 13, 3)
    coast.path(33, 15, 4, 7)
    # Weathered timber projects above water; it is not a dirt peninsula.
    coast.rect(35, 20, 20, 1, tile(6, 150), walk=True)
    coast.rect(35, 21, 20, 1, tile(6, 151), walk=True)
    coast.rect(35, 22, 20, 1, tile(6, 152), z=1, walk=False)
    coast.rect(52, 19, 3, 1, tile(6, 150), walk=True)
    coast.rect(55, 20, 1, 2, tile(7, 151), z=1, walk=False)
    coast.stamp(5, 444, 3, 8, 7, 7)
    coast.stamp(0, 227, 4, 4, 20, 8)
    coast.stamp(0, 227, 4, 4, 28, 7)
    coast.stamp(4, 228, 4, 4, 34, 7)
    coast.door(8, 15, 101, 10, 12, 8, cue="north")
    coast.walk[31][45] = True
    coast.event("Shop door", 21, 11, "Tidebound::Interactions.shop_door", trigger=1, cue="south")
    coast.event(
        ACTORS["seller_outside"], 22, 12, "Tidebound::Interactions.outside_seller", "NPC 10"
    )
    coast.event(
        ACTORS["pookie_outside"], 11, 16, "Tidebound::Opening.pookie", "Pokemon 01", opacity=0
    )
    coast.event(
        "Oil shop sign",
        23,
        12,
        'pbMessage("LAMP OIL. Please ask the seller for assistance.\nA small bottle hangs beside the lettering.")',
    )
    coast.event(
        "Empty house", 29, 11, 'pbMessage("The door has swollen in its frame. Nobody answers.")'
    )
    coast.event(
        "Seated neighbour",
        31,
        18,
        'pbMessage("Young as ever, aren\'t you? I wish I knew your secret.")\npbMessage("Your mother still lights the tower every night. I used to complain that it shone through my curtains.")',
        "NPC 14",
        blocks=True,
    )
    coast.event("Pier", 54, 20, "Tidebound::Opening.pier", trigger=1)
    coast.event("Lapras", 56, 23, "", role="lapras")
    coast.event(
        "Tide bell",
        18,
        20,
        'pbMessage("A bell with no clapper. Salt has filled the inscription.")',
        role="tide_bell",
    )
    coast.event("Forest path", 24, 3, "Tidebound::Opening.forest_gate", trigger=1, cue="north")

    for x in range(20, 39, 3):
        for y in range(-18, 3, 3):
            coast.stamp(0, 55, 3, 3, x, y)
    for x, y in [(3, 7), (12, 10), (18, 6), (25, 7), (32, 3), (36, 12)]:
        coast.stamp(3, 67, 3, 3, x, y)
    for x, y in [(1, 10), (1, 17), (11, 5), (13, 13), (6, 21), (16, 22), (20, 24), (37, 16)]:
        coast.stamp(0, 108, 3, 3, x, y)
    for i, (x, y) in enumerate(
        [
            (4, 16),
            (5, 19),
            (12, 17),
            (14, 20),
            (19, 22),
            (22, 23),
            (26, 24),
            (32, 24),
            (35, 23),
            (38, 20),
            (3, 20),
            (11, 21),
        ]
    ):
        sx, sy = [(0, 140), (2, 140), (0, 142), (3, 142), (2, 143)][i % 5]
        coast.stamp(sx, sy, 1, 1, x, y)
    for x, y in [
        (5, 11),
        (5, 12),
        (6, 12),
        (10, 16),
        (11, 17),
        (11, 12),
        (12, 12),
        (26, 18),
        (27, 18),
        (30, 16),
        (31, 16),
        (23, 17),
    ]:
        coast.rect(x, y, 1, 1, 240, z=1)
    for x, y in [(4, 12), (6, 17), (12, 19), (20, 17), (27, 16), (32, 18), (34, 23)]:
        coast.rect(x, y, 1, 1, tile(6, 0), z=1)
    # Only the authored entrance crosses into the northern forest.
    for x in range(20, 40):
        coast.walk[22][x + 24] = False
    for x in (23, 25):
        coast.walk[23][x + 24] = False
    coast.event(
        "Headland flowers",
        11,
        12,
        'pbMessage("Late flowers, sheltered by a ring of flat stones.\nSomeone has tied the weakest stems to little sticks.")',
    )
    coast.event(
        "Sea glass",
        29,
        24,
        'pbMessage("Green glass, worn smooth by the water.\nFor a moment, it catches the light.")',
        role="sea_glass",
    )
    coast.event(
        "Coast lamp:home",
        5,
        16,
        'pbMessage("Mother lights this little lamp before dusk.\nSo you can always find the path home.")',
        role="coast_lamp",
    )
    coast.event(
        "Coast lamp:pier",
        52,
        19,
        'pbMessage("A little oil lamp. Someone still tends it, even with the boats gone.")',
        role="coast_lamp",
    )
    coast.event(
        "Mooring rope",
        54,
        21,
        'pbMessage("An old mooring rope disappears beneath the boards.")',
        role="mooring_rope",
    )

    # Preserve all existing coast event IDs. Extend a small southern rocky path.
    coast.polygon([(28, 23), (32, 23), (33, 28), (32, 32), (28, 32), (27, 28)], tile(2, 27))
    coast.path(29, 24, 3, 8, True)
    coast.event("South path", 30, 31, "Tidebound::NeighborQuest.south_gate", trigger=1, cue="south")
    coast.event(ACTORS["robbery_youth_one"], 21, 11, "", "trainer_YOUNGSTER", opacity=0)
    coast.event(ACTORS["robbery_youth_two"], 21, 12, "", "trainer_CAMPER", opacity=0)
    coast.event(
        "Coast road sign",
        31,
        29,
        'pbMessage("COAST ROAD - SOUTH. The lettering has been repainted around the rusted nails.")',
    )

    for x, y, item in [(12, 18, "ORANBERRY")]:
        eid = coast.event(
            "Berry:" + item,
            x,
            y,
            f"Tidebound::FieldDetails.berry({coast.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
        )
        coast.events[eid].attributes["@pages"][0].attributes["@graphic"].attributes[
            "@direction"
        ] = 8
    coast.event(
        "Coast lamp:shop",
        24,
        12,
        'pbMessage("A sheltered flame warms the shopfront.")',
        role="coast_lamp",
    )

    return coast


def build_forest():
    forest = Map(MAPS["forest"], "The Listening Wood", 36, 30, 1, tile(1, 0))
    forest.rect(3, 3, 30, 24, tile(1, 0), walk=True)
    forest.rect(16, 3, 3, 24, tile(2, 13), walk=True)
    forest.rect(7, 20, 12, 3, tile(2, 13), walk=True)
    forest.rect(17, 10, 12, 3, tile(2, 13), walk=True)
    for x in range(1, 34, 3):
        for y in [0, 26]:
            if x in [16, 19] and y == 26:
                continue
            forest.stamp(0, 55, 3, 3, x, y)
    for x, y in [
        (2, 5),
        (2, 11),
        (2, 17),
        (6, 5),
        (7, 10),
        (10, 5),
        (24, 3),
        (28, 6),
        (30, 13),
        (25, 17),
        (25, 23),
        (7, 24),
        (11, 13),
    ]:
        forest.stamp(0, 55, 3, 3, x, y)
    forest.event("Ninja", 9, 20, "Tidebound::Opening.fire", "NPC 01", blocks=True)
    forest.event("Fire", 10, 21, "Tidebound::Opening.fire", blocks=True, role="fire")
    forest.event(
        "Wild:NATU",
        21,
        13,
        "Tidebound::Opening.bird",
        "Pokemon 01",
        opacity=0,
        move=1,
        species="NATU",
        role="wood_bird",
    )
    forest.event("Dark pool", 27, 10, "Tidebound::Opening.pool", trigger=1)
    forest.rect(26, 8, 4, 2, 144, walk=False)
    forest.event(
        "Shop keys", 14, 11, "Tidebound::Opening.forest_keys", "Pokemon 01", opacity=0, role="keys"
    )
    forest.event(
        "White flowers", 14, 9, 'pbMessage("Small white flowers. They have survived the cold.")'
    )
    forest.event("Northern way", 17, 3, "Tidebound::Opening.northern_way", trigger=1)
    forest.door(17, 27, 102, 48, 25)
    for x, y in [(12, 21), (14, 7), (14, 8), (14, 10), (22, 15), (23, 15), (24, 15)]:
        forest.rect(x, y, 1, 1, tile(7, 3), z=1)

    for x, y, w, h in [(6, 16, 4, 3), (20, 5, 3, 4), (20, 18, 4, 3)]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if forest.walk[yy][xx] and forest.layers[1][yy][xx] == 0:
                    forest.rect(xx, yy, 1, 1, tile(7, 0), z=1)

    for x, y, item in [(12, 19, "ORANBERRY"), (22, 9, "ORANBERRY")]:
        eid = forest.event(
            "Berry:" + item,
            x,
            y,
            f"Tidebound::FieldDetails.berry({forest.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
        )
        forest.events[eid].attributes["@pages"][0].attributes["@graphic"].attributes[
            "@direction"
        ] = 8

    return forest


def build_lantern():
    lantern = Map(MAPS["lantern"], "The Lantern Room", 14, 14, 3)
    lantern.rect(3, 3, 8, 8, tile(1, 81), walk=True)
    lantern.rect(3, 2, 8, 1, tile(1, 13), walk=False)
    lantern.event("Main lamp", 6, 5, "Tidebound::Opening.main_lamp", blocks=True, role="main_lamp")
    lantern.event(
        "Downward lamp",
        9,
        8,
        'pbMessage("A smaller lamp points straight down into the water.\nThe glass is warm.")',
        blocks=True,
        role="lamp",
    )
    lantern.rect(6, 11, 1, 1, tile(1, 81), walk=True)
    lantern.door(6, 11, 101, 16, 4)

    return lantern


def build_astral():
    astral = Map(MAPS["astral"], "Beyond the Shore", 32, 26, 1, tile(1, 0))
    astral.rect(3, 3, 26, 20, tile(1, 0), walk=True)
    astral.rect(14, 4, 3, 19, tile(2, 13), walk=True)
    for x, y in [
        (1, 1),
        (6, 1),
        (22, 1),
        (27, 1),
        (1, 8),
        (1, 16),
        (27, 8),
        (27, 17),
        (5, 20),
        (22, 20),
    ]:
        astral.stamp(0, 55, 3, 3, x, y)
    for i, (x, y) in enumerate([(9, 7), (21, 8), (7, 15), (23, 16), (13, 5), (18, 19)]):
        astral.event(
            f"Spirit:{i}",
            x,
            y,
            f"Tidebound::Opening.spirit({i})",
            "Pokemon 01",
            opacity=0,
            move=1,
            role="spirit",
            index=i,
        )
    astral.event("Guide", 15, 20, "Tidebound::Opening.guide", "NPC 01", opacity=120)
    astral.event("Return", 15, 22, "Tidebound::Opening.return_from_astral", trigger=1, role="lamp")
    astral.event("Ashes", 5, 12, "Tidebound::Opening.memorial", role="lamp")
    astral.event("Arrival", 3, 22, "Tidebound::Opening.astral_arrival", trigger=3)

    return astral


def build_shop():
    shop = Map(MAPS["shop"], "The Oil Shop", 16, 14, 3)
    shop.rect(2, 3, 12, 9, tile(4, 78), walk=True)
    shop.rect(2, 2, 12, 2, tile(1, 13), walk=False)
    for x in (2, 6, 10):
        shop.stamp(0, 0, 4, 2, x, 1)
    shop.stamp(3, 140, 3, 3, 3, 4)
    shop.stamp(0, 140, 2, 3, 10, 4)
    shop.stamp(6, 212, 2, 2, 10, 8)
    shop.event(
        ACTORS["oil_seller"], 7, 5, "Tidebound::Interactions.oil_seller", "NPC 10", blocks=True
    )
    shop.event(
        "Bottles",
        4,
        7,
        'pbMessage("Old glass, washed and washed again. Each bottle has a different name scratched underneath.")',
    )
    shop.event(
        "Old ledger",
        11,
        10,
        'pbMessage("The ledger lies open to a page with very few names.\nYour mother\'s is underlined.")',
    )
    shop.rect(8, 12, 1, 1, tile(4, 78), walk=True)
    shop.door(8, 12, 102, 45, 32, 2)

    return shop


def build_bedroom():
    bedroom = Map(MAPS["bedroom"], "Your Room", 16, 14, 3)
    bedroom.rect(2, 4, 12, 8, tile(4, 78), walk=True)
    bedroom.rect(2, 2, 12, 2, tile(1, 13), walk=False)
    for x in (2, 6, 10):
        bedroom.stamp(0, 0, 4, 2, x, 1)
    bedroom.stamp(0, 151, 2, 2, 3, 4)
    bedroom.stamp(0, 140, 3, 2, 10, 4)
    bedroom.event(
        "Room:NATU",
        7,
        8,
        "Tidebound::Opening.bedroom_pet",
        "Pokemon 01",
        opacity=0,
        role="room",
        species="NATU",
    )
    bedroom.event(
        ACTORS["mother_visiting"],
        8,
        11,
        'pbMessage("Mother: Downstairs, love.")',
        "NPC 11",
        opacity=0,
    )
    bedroom.event("Book", 4, 9, "Tidebound::Opening.journal")
    bedroom.event("Opening", 2, 11, "Tidebound::Opening.begin_story", trigger=3)
    bedroom.rect(8, 12, 1, 1, tile(4, 78), walk=True)
    bedroom.event("Bedroom exit", 8, 12, "Tidebound::Opening.bedroom_exit", trigger=1, cue="south")
    # The short pursuit route is separate from the future dock city.

    return bedroom


def build_road():
    road = RoadMap(MAPS["road"], "The South Coast Road", 56, 84, 1, 96)
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
    for x, y in [
        (14, 22),
        (20, 22),
        (28, 22),
        (34, 22),
        (37, 14),
        (32, 13),
        (36, 31),
        (17, 33),
        (18, 48),
        (36, 51),
    ]:
        road.stamp(0, 108, 3, 3, x, y)
    for x, y in [
        (20, 1),
        (23, 4),
        (28, 5),
        (32, 7),
        (35, 9),
        (36, 18),
        (17, 28),
        (20, 38),
        (36, 46),
        (34, 56),
        (20, 61),
        (24, 62),
        (29, 62),
    ]:
        road.stamp(0, 55, 3, 3, x, y)
    for x, y in [(16, 10), (20, 14), (22, 16), (30, 28), (32, 35), (23, 46), (30, 54)]:
        road.rect(x, y, 1, 1, 240, z=1)
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
        58,
        'pbMessage("The lower steps have washed away. New planks lie ready beside them. The coast road continues towards the distant docks.")',
    )
    road.event(
        "Torn wrapping",
        31,
        34,
        'pbMessage("Straw packing, and an empty oil-shop bag. They came this way.")',
    )
    road.event("Shore flowers", 16, 10, 'pbMessage("Small flowers turn away from the salt wind.")')

    for x, y, w, h in [(20, 7, 3, 3), (29, 17, 4, 3), (29, 29, 4, 3), (29, 47, 4, 3)]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if road.walk[yy][xx] and road.layers[1][yy][xx] == 0:
                    road.rect(xx, yy, 1, 1, tile(7, 0), z=1)

    for x, y, item in [(21, 16, "ORANBERRY"), (28, 38, "SITRUSBERRY")]:
        eid = road.event(
            "Berry:" + item,
            x,
            y,
            f"Tidebound::FieldDetails.berry({road.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
        )
        road.events[eid].attributes["@pages"][0].attributes["@graphic"].attributes["@direction"] = 8
    road.event(
        "Coast lamp:storehouse",
        33,
        42,
        'pbMessage("The wick has been trimmed recently.")',
        role="coast_lamp",
    )

    return road


def build_hideout():
    hideout = Map(MAPS["hideout"], "The Old Storehouse", 22, 18, 3)
    hideout.rect(2, 3, 18, 13, tile(4, 78), walk=True)
    hideout.rect(2, 2, 18, 2, tile(1, 13), walk=False)
    for x in (2, 6, 10, 14, 18):
        hideout.stamp(0, 0, 4, 2, x, 1)
    for x, y in [
        (4, 5),
        (5, 5),
        (6, 5),
        (4, 6),
        (5, 6),
        (16, 5),
        (17, 5),
        (17, 6),
        (7, 13),
        (8, 13),
    ]:
        hideout.event(
            "Crate goods",
            x,
            y,
            'pbMessage("Oil tins, mended nets, a good blanket. Nothing here matches.")',
            "Pokemon 01",
            opacity=0,
            blocks=True,
        )
    hideout.event("Abyss runner", 11, 9, "Tidebound::Hideout.guard", "trainer_BURGLAR", blocks=True)
    hideout.event(
        ACTORS["necklace_thief"], 14, 7, "Tidebound::Hideout.boss", "trainer_CAMPER", blocks=True
    )
    hideout.event(
        "Abyss packer", 17, 11, "Tidebound::NeighborQuest.packer", "trainer_BUGCATCHER", blocks=True
    )
    hideout.event(
        "Abyss lookout", 5, 10, "Tidebound::NeighborQuest.lookout", "trainer_YOUNGSTER", blocks=True
    )
    hideout.event(
        "Dispatch slip",
        16,
        8,
        'pbMessage("One box: nets. Two boxes: assorted. Three boxes: also assorted. A second hand has underlined: COUNT IT PROPERLY.")',
    )
    hideout.event("Arrival", 2, 15, "Tidebound::Hideout.arrival", trigger=3)
    hideout.rect(11, 16, 1, 1, tile(4, 78), walk=True)
    hideout.door(11, 16, 108, 35, 43, 2)

    return hideout
