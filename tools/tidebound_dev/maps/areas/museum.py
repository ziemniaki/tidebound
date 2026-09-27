from ..model import Map, tile
from ..registry import MAPS


def build():
    museum = Map(MAPS["museum"], "Dockside Museum", 30, 24, 3)
    museum.rect(3, 3, 24, 18, tile(1, 81), walk=True)
    museum.rect(3, 2, 24, 2, tile(1, 13), walk=False)
    for x in range(3, 27, 4):
        museum.stamp(0, 0, 4, 2, x, 1)
    museum.event(
        "Attendant",
        8,
        16,
        'pbMessage("Attendant: Welcome. Take your time. If you have come for the sabre, it is in the middle case.")\npbMessage("Attendant: People ask who made it. I would rather leave the label unfinished than put a guess on it.")',
        "NPC 11",
        blocks=True,
    )
    museum.event(
        "Sabre exhibit", 15, 8, "Tidebound::VaultVisit.sabre", blocks=True, role="sabre_exhibit"
    )
    for x, y, name, text in [
        (
            7,
            7,
            "Harbour bell",
            "A cracked harbour bell. The label lists the names of the people who paid to recast it.",
        ),
        (
            22,
            7,
            "Sounding weights",
            "Lead sounding weights and a carefully knotted line. An old way of learning how much water lies beneath a boat.",
        ),
        (
            22,
            14,
            "Ceramic fragments",
            "Fragments of bowls and plates from coastal households. Familiar blue reeds curve across one piece.",
        ),
        (
            7,
            12,
            "Shipping ledger",
            "A shipping ledger, open to a page of ordinary deliveries: lamp oil, flour, cloth.",
        ),
    ]:
        museum.event(
            "Museum case:" + name, x, y, f'pbMessage("{text}")', blocks=True, role="museum_case"
        )
    museum.event(
        "Visitor",
        18,
        12,
        'pbMessage("Visitor: I came in to get out of the wind. That was a while ago.")',
        "NPC 10",
        blocks=True,
    )
    museum.door(14, 21, 112, 32, 23, 2)

    return museum
