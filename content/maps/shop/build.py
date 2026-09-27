from tidebound_dev.maps.model import Map, tile
from tidebound_dev.maps.registry import MAPS, ACTORS


def build(context):
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
    shop.door(8, 12, "coast", "from_shop")

    return shop
