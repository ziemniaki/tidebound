from tidebound_dev.maps.model import Map
from tidebound_dev.maps.registry import MAPS, ACTORS


def build(context):
    interior = context.rooms
    bedroom = Map(MAPS["bedroom"], "Your Room", 16, 14, 3)
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
    bedroom.event("Bedroom exit", 8, 12, "Tidebound::Opening.bedroom_exit", trigger=1, cue="south")

    return bedroom
