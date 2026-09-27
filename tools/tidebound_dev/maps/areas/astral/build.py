from ...model import Map, tile
from ...registry import MAPS


def build(context):
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
            f"Tidebound::Astral.spirit({i})",
            "Pokemon 01",
            opacity=0,
            move=1,
            role="spirit",
            index=i,
        )
    astral.event("Guide", 15, 20, "Tidebound::Astral.guide", "NPC 01", opacity=120)
    astral.event("Return", 15, 22, "Tidebound::Astral.leave", trigger=1, role="lamp")
    astral.event("Ashes", 5, 12, "Tidebound::Astral.memorial", role="lamp")
    astral.event("Arrival", 3, 22, "Tidebound::Astral.arrival", trigger=3)

    return astral
