"""Dockside errands and a permanent northeast fighting quay."""

from PIL import Image, ImageDraw
from .model import tile


def ring_art(destination):
    # Draw at Gen 3's underlying pixel density, then double without smoothing.
    image = Image.new("RGBA", (128, 112))
    d = ImageDraw.Draw(image)
    d.rectangle((5, 17, 122, 103), fill="#343438")
    d.rectangle((8, 17, 119, 98), fill="#716455")
    for y in range(20, 98, 7):
        d.line((9, y, 118, y), fill="#5b5148")
        for x in range(17 + y % 3 * 9, 115, 29):
            d.line((x, y, x, y + 6), fill="#4b4541")
    d.ellipse((35, 32, 91, 84), outline="#b1a283", width=2)
    d.line((64, 34, 64, 82), fill="#a2967d", width=1)
    # Rear ropes, corner posts and sagged side ropes. Front rail has a gate.
    for y in (12, 17):
        d.line((9, y, 117, y), fill="#b6aa8b", width=2)
        d.line((9, y, 9, 83 + y // 4), fill="#aaa082", width=2)
        d.line((117, y, 117, 83 + y // 4), fill="#aaa082", width=2)
    for x, y in ((7, 7), (115, 7), (7, 81), (115, 81)):
        d.rectangle((x, y, x + 5, y + 20), fill="#292d32")
        d.rectangle((x + 1, y + 1, x + 3, y + 18), fill="#8a7760")
        d.rectangle((x, y + 3, x + 5, y + 4), fill="#c5b494")
    for y in (88, 94):
        d.line((11, y, 53, y), fill="#c1b293", width=2)
        d.line((75, y, 116, y), fill="#c1b293", width=2)
    for x, y in ((34, 79), (79, 39), (87, 76), (25, 45)):
        d.line((x, y, x + 4, y - 2), fill="#3f3d3b")
    image.resize((256, 224), Image.Resampling.NEAREST).save(destination)


def decorate(paths, docks):
    ring_art(paths.game / "Graphics/Pictures/Tidebound/Demo_quayring.png")
    # An old stone apron beside the northern warehouses. Clear all layers together.
    for y in range(15, 29):
        for x in range(62, 76):
            docks.layers[1][y][x] = docks.layers[2][y][x] = 0
            docks.rect(x, y, 1, 1, tile(4, 50), walk=True)
    # Continuous seawall, with the full west side connecting to the existing city.
    for x in range(62, 76):
        for y in (14, 29):
            docks.rect(x, y, 1, 1, tile(6, 150), z=1, walk=False)
    for y in range(15, 29):
        docks.rect(76, y, 1, 1, tile(6, 150), z=1, walk=False)
    docks.rect(65, 17, 8, 7, tile(4, 50), walk=False)
    # The picture and actors aren't interaction targets: spectators face the ring.
    docks.event(
        "Demo prop:quayring",
        65,
        17,
        'pbMessage("Old ropes, new wagers. The boards carry the marks of many bouts.")',
    )
    docks.event(
        "Ring bookkeeper", 68, 25, "Tidebound::QuayRing.talk", "trainer_SAILOR", blocks=True
    )
    for key, x, y in [("wager", 64, 20), ("scar", 74, 20), ("loser", 65, 25), ("watcher", 72, 25)]:
        docks.event(
            "Ring spectator:" + key,
            x,
            y,
            f"Tidebound::DockLife.spectator(:{key})",
            "trainer_SAILOR",
            blocks=True,
        )
    docks.event(
        "Ring notice",
        63,
        25,
        'pbMessage("QUAY RING. A new challenger every quarter-hour. Spectators settle their own debts.")',
    )
    for x, y in [(63, 16), (74, 16), (74, 27)]:
        docks.event(
            "Coast lamp:ring",
            x,
            y,
            'pbMessage("Salt has crusted around the warm lantern glass.")',
            blocks=True,
        )
    # Residents occupy spare pavement, never doorways or existing transfer points.
    people = [
        ("Sailmaker Ada", 16, 39, "sailmaker", "NPC 07"),
        ("Courier Ivo", 21, 31, "courier", "trainer_SAILOR"),
        ("Retired Tomas", 27, 16, "tomas", "NPC 04"),
        ("Cook Mara", 19, 23, "cook", "NPC 07"),
        ("Lamplighter Lio", 41, 25, "lamplighter", "NPC 04"),
        ("Netmender Sen", 40, 37, "netmender", "NPC 07"),
    ]
    for name, x, y, action, graphic in people:
        docks.event(name, x, y, f"Tidebound::DockLife.{action}", graphic, blocks=True)
    docks.event("Crate dry canvas", 49, 38, "Tidebound::DockLife.canvas", blocks=True)
