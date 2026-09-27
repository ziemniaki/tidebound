from PIL import Image, ImageDraw
from ...files import save_png
from ..model import Map
from ..registry import MAPS


def build(paths, interior):
    lantern = Map(MAPS["lantern"], "The Lantern Room", 14, 14, 3)
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

    lantern.event("Main lamp", 6, 5, "Tidebound::Opening.main_lamp", blocks=True, role="main_lamp")
    lantern.event(
        "Downward lamp",
        9,
        8,
        'pbMessage("A smaller lamp points straight down into the water.\nThe glass is warm.")',
        blocks=True,
        role="lamp",
    )
    lantern.door(6, 11, 101, 16, 4)

    return lantern
