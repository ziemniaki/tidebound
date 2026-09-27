from ..model import Map
from ..registry import MAPS


def build(interior):
    basement = Map(MAPS["basement"], "The Lighthouse Cellar", 26, 20, 3)
    interior.room(basement, 3, 4, 20, 13, True)
    interior.stairs(basement, 5, 12)
    for x in [10, 13, 20]:
        interior.prop(basement, interior.ARCHIVE, x, 4, 2, 2)
    interior.prop(basement, interior.SHELF, 4, 8, 2, 2)
    interior.prop(basement, interior.ARCHIVE, 20, 8, 2, 2)
    interior.prop(basement, interior.BASIN, 9, 13, 1, 1)
    interior.prop(basement, interior.ARCHIVE, 14, 13, 2, 2)
    for x in [15, 18]:
        for y in [2, 3, 4]:
            interior.surface(basement, interior.wall(True).crop((0, 0, 32, 32)), x, y, True)

    basement.door(6, 14, 101, 4, 12, 6)
    for x, y in [(5, 5), (6, 5), (8, 6), (20, 13), (21, 13), (20, 14)]:
        basement.event(
            "Crate cellar",
            x,
            y,
            'pbMessage("Oil tins and spare glass, wrapped carefully against the damp.")',
            "Pokemon 01",
            opacity=0,
            blocks=True,
            role="crate",
        )
    basement.event(
        "Old tools",
        6,
        11,
        'pbMessage("A brush worn down to its wood. A spare lamp spindle. Tools repaired more often than replaced.")',
    )
    basement.event("Vault doorway", 17, 4, "Tidebound::VaultVisit.vault_door", cue="north")
    basement.event(
        "Vault ironwork",
        17,
        3,
        'pbMessage("The iron door is far thicker than the cellar walls. Mother has left it open.")',
        blocks=True,
        role="prop",
        asset="vault_ironwork",
    )
    basement.event(
        "Coast lamp:cellar",
        13,
        8,
        'pbMessage("Mother has brought a lamp down.")',
        role="coast_lamp",
    )

    return basement
