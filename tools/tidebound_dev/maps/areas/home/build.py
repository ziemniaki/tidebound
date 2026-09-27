from ...model import Map
from ...registry import MAPS, ACTORS


def build(context):
    interior = context.rooms
    home = Map(MAPS["home"], "The Keeper's House", 20, 16, 3)
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

    home.event(ACTORS["mother"], 12, 7, "Tidebound::Interactions.mother", "NPC 11", blocks=True)
    home.event("Book", 4, 10, "Tidebound::Opening.journal")
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
    home.door(6, 3, "bedroom", "from_home")
    home.door(10, 14, "coast", "from_home")
    home.door(17, 3, "lantern", "from_home")
    home.event("Cellar stairs", 3, 12, "Tidebound::VaultVisit.stairs", trigger=1, cue="south")
    home.event(
        ACTORS["seller_at_home"],
        14,
        12,
        'pbMessage("Seller: Your mother has a better head for keys than I do.")',
        "NPC 10",
        opacity=0,
    )

    return home
