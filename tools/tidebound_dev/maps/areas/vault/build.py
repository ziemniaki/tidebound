from PIL import ImageDraw
from ...model import Map
from ...registry import MAPS, ACTORS


def build(context):
    interior = context.rooms
    vault = Map(MAPS["vault"], "The Lighthouse Vault", 28, 22, 3)
    interior.room(vault, 3, 3, 22, 16, True)
    for x in [4, 7, 19, 22]:
        interior.prop(vault, interior.ARCHIVE, x, 3, 2, 2)
    for x in [4, 22]:
        for y in [7, 12]:
            interior.prop(vault, interior.ARCHIVE, x, y, 2, 2)
    for y in range(7, 18):
        for x in [11, 12, 13]:
            im = interior.floor_tile(True)
            dr = ImageDraw.Draw(im)
            if x in [11, 13]:
                dr.line(
                    (3 if x == 11 else 28, 0, 3 if x == 11 else 28, 31),
                    fill=(143, 142, 121, 255),
                    width=2,
                )
            vault.layers[0][y][x] = interior.itile(im)
    for x in [8, 17]:
        interior.prop(vault, interior.CABINET, x, 14, 2, 2)
    vault.rect(12, 18, 1, 1, interior.itile(interior.floor_tile(True)), walk=True)
    for x, y in [(5, 10), (21, 10), (5, 15), (21, 15)]:
        vault.event(
            "Vault pillar",
            x,
            y,
            'pbMessage("The stone is cold and worn smooth at shoulder height.")',
            blocks=True,
            role="prop",
            asset="vault_pillar",
        )
    vault.event(
        ACTORS["mother_at_vault"],
        13,
        8,
        'pbMessage("Mother: The museum is along the quay. Keep to the lit road, love.")',
        "NPC 11",
    )
    vault.event(
        ACTORS["seller_at_vault"],
        11,
        8,
        'pbMessage("Seller: Tell them I sent you. It will not get you a discount. Entry is free.")',
        "NPC 10",
    )
    vault.event(
        "Necklace drawer",
        12,
        6,
        'pbMessage("A shallow drawer, now locked. The seller\'s necklace rests inside, wrapped in cloth.")',
        blocks=True,
        role="prop",
        asset="necklace_drawer",
    )
    vault.event(
        "Empty bays",
        20,
        6,
        'pbMessage("Numbered shelves. Most are empty. There is space here for much more than one household could need.")',
    )
    vault.event("Cabinet locks", 6, 6, 'pbMessage("Small brass locks. Mother has kept the keys.")')
    vault.event(
        "Old masonry",
        23,
        17,
        'pbMessage("The lowest stones are darker than the rest. The mortar has been renewed around them.")',
    )
    vault.event("Arrival", 3, 18, "Tidebound::VaultVisit.conversation", trigger=3)
    vault.door(12, 18, "basement", "from_vault")

    return vault
