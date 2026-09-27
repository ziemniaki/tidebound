from PIL import Image
from ...model import Map
from ...registry import MAPS


def build(context):
    paths = context.paths
    interior = context.rooms
    lantern = Map(MAPS["lantern"], "The Lantern Room", 14, 14, 3)
    interior.room(lantern, 3, 3, 8, 8, True)
    interior.window(lantern, 3, 1)
    interior.window(lantern, 5, 1, 4)
    interior.window(lantern, 9, 1)
    with Image.open(paths.root / "assets/pictures/Tidebound/beacon.png") as source:
        beacon = source.convert("RGBA")
    interior.surface(lantern, beacon, 5, 2, True)
    interior.prop(lantern, interior.ARCHIVE, 3, 6, 2, 2)
    interior.prop(lantern, interior.BOOK, 4, 8, 1, 1, False)
    interior.stairs(lantern, 5, 9, False)
    lantern.rect(6, 11, 1, 1, interior.itile(interior.floor_tile(True)), walk=True)
    interior.prop(lantern, interior.STOOL, 9, 8, 1, 1, False)

    lantern.event("Main lamp", 6, 5, "Tidebound::Opening.main_lamp", blocks=True, role="main_lamp")
    lantern.event(
        "Downward lamp",
        9,
        8,
        'pbMessage("A smaller lamp points straight down into the water.\nThe glass is warm.")',
        blocks=True,
        role="lamp",
    )
    lantern.door(6, 11, "home", "from_lantern")

    return lantern
