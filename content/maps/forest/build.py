from tidebound_dev.maps.model import Map, tile
from tidebound_dev.maps.registry import MAPS
from tidebound_dev.maps.shoreline import shoreline


def build(context):
    palette = context.palette
    forest = Map(MAPS["forest"], "The Listening Wood", 36, 30, 1, tile(1, 0))
    forest.rect(3, 3, 30, 24, tile(1, 0), walk=True)
    forest.rect(16, 3, 3, 24, tile(2, 13), walk=True)
    forest.rect(7, 20, 12, 3, tile(2, 13), walk=True)
    forest.rect(17, 10, 12, 3, tile(2, 13), walk=True)
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
    forest.door(17, 27, "coast", "from_forest")

    for x, y, item in [(12, 19, "ORANBERRY"), (22, 9, "ORANBERRY")]:
        forest.event(
            "Berry:" + item,
            x,
            y,
            f"Tidebound::FieldDetails.berry({forest.id}, {x}, {y}, :{item})",
            "berrytree_" + item,
            blocks=False,
            role="berry",
            direction=8,
        )
    shoreline(forest)
    # LISTENING WOOD: the path threads three groves, a key clearing, pool and camp.
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

    return forest
