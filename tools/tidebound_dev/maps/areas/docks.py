from ..model import Map, tile
from ..registry import MAPS
from ..shoreline import coastal_shoreline
from ..landscape import shade_water


def build(paths, palette):
    docks = Map(MAPS["docks"], "The Docks", 80, 64, 1, 96)
    docks.polygon([(9, 15), (62, 15), (62, 39), (55, 44), (16, 44), (9, 35)], tile(2, 27))
    docks.rect(9, 26, 47, 5, tile(2, 27), walk=True)
    docks.rect(10, 26, 3, 5, tile(2, 13), walk=True)
    docks.door(10, 28, 108, 43, 43, 4, cue="west")
    # Museum: wider public facade with a shallow green roof and a stone forecourt.
    for yy in range(4):
        for xx, sx in enumerate([4, 5, 5, 5, 5, 5, 6, 7]):
            docks.rect(28 + xx, 18 + yy, 1, 1, tile(sx, 223 + yy), z=1, walk=False)
    docks.rect(31, 21, 1, 1, tile(4, 226), z=1, walk=True)
    docks.door(31, 21, "museum", 14, 18, 8, name="Museum door", cue="south")
    docks.event(
        "Museum sign",
        35,
        23,
        'pbMessage("DOCKSIDE MUSEUM. Objects from the coast. Admission free. Please wipe your shoes.")',
    )
    for x, y in [(16, 17), (43, 17), (53, 20)]:
        docks.stamp(0, 227, 4, 4, x, y)
    for x, y in [(44, 30), (45, 30), (48, 33), (50, 33), (18, 33)]:
        docks.event(
            "Crate dock",
            x,
            y,
            'pbMessage("Freight labels lie beneath newer freight labels. Most of the names have blurred in the salt air.")',
            "Pokemon 01",
            opacity=0,
            blocks=True,
            role="crate",
        )
    for x in [25, 42, 54]:
        docks.rect(x, 41, 3, 10, tile(6, 150), walk=True)
        docks.rect(x, 51, 3, 1, tile(6, 152), z=1, walk=False)
    for x, y in [(14, 27), (28, 23), (37, 27), (43, 39), (55, 34)]:
        docks.event(
            "Coast lamp:dock",
            x,
            y,
            'pbMessage("A warm lantern in a thick glass hood.")',
            role="coast_lamp",
        )
    docks.event(
        "Porter",
        22,
        30,
        'pbMessage("Porter: Mind the ropes. We have enough things falling into the water.")',
        "NPC 03",
        blocks=True,
    )
    docks.event(
        "Mender",
        38,
        35,
        'pbMessage("Net mender: They bring torn nets here from every little village along the coast. Some come back with the same knot I tied last year.")',
        "NPC 14",
        blocks=True,
    )
    docks.event(
        "Warehouse notice",
        45,
        22,
        'pbMessage("Deliveries by arrangement. No loose goods accepted without a name and a count.")',
    )
    docks.event(
        "Closed quay",
        59,
        28,
        'pbMessage("A chain closes the far quay. Work lamps glow beyond it.")',
    )

    # Dock expansion. Existing museum, quay event IDs, entrances and piers stay put.
    # Streets/pavements are drawn beneath buildings, so no facade footprint is erased.
    def surface(x, y, w, h, t):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if docks.walk[yy][xx]:
                    docks.layers[0][yy][xx] = t

    # Northern residential blocks grow from the existing town land.
    for yy in range(9, 18):
        for xx in range(11, 65):
            if docks.layers[1][yy][xx] == 0:
                docks.rect(xx, yy, 1, 1, tile(2, 27), walk=True)
    surface(10, 24, 54, 9, tile(4, 50))
    surface(10, 27, 54, 4, tile(2, 27))
    surface(21, 12, 5, 30, tile(4, 42))
    surface(38, 12, 5, 29, tile(4, 42))
    surface(49, 19, 4, 23, tile(4, 42))
    surface(26, 21, 12, 6, tile(4, 50))
    surface(12, 14, 51, 3, tile(4, 42))
    surface(16, 39, 41, 5, tile(4, 42))
    for x, y in [(13, 10), (20, 10), (40, 9), (49, 10), (58, 12)]:
        docks.stamp(4, 228, 4, 4, x, y)
    # Narrow domestic lanes and a waterfront workshop.
    docks.stamp(0, 227, 4, 4, 13, 34)
    docks.stamp(4, 228, 4, 4, 32, 33)
    # Larger customs warehouse: matching native roof and pane tiles.
    for yy in range(4):
        for xx, sx in enumerate([4, 5, 5, 5, 5, 5, 6, 7]):
            docks.rect(44 + xx, 34 + yy, 1, 1, tile(sx, 223 + yy), z=1, walk=False)
    docks.rect(47, 37, 1, 1, tile(4, 226), z=1)  # Freight door is visibly closed, not a transfer.
    # Give closed building frontages ordinary descriptions; only museum entry is live.
    for x, y, text in [
        (14, 38, "SAIL REPAIRS. A needle taps against a thimble behind the door."),
        (33, 37, "Rooms above the quay. Someone has left boots drying inside."),
        (47, 38, "CUSTOMS STORE. Sealed cargo awaiting a count."),
        (54, 24, "A chandler's window. Rope, wax and spare wicks, arranged with great care."),
        (18, 21, "The bakery has closed. The smell of bread lingers in the doorway."),
    ]:
        docks.event("Dock frontage", x, y, f"pbMessage({text!r})")
    for x, y in [(23, 17), (40, 23), (51, 31), (18, 40), (35, 40), (57, 41)]:
        docks.event(
            "Coast lamp:quay",
            x,
            y,
            'pbMessage("The lantern hood keeps most of the rain off the wick.")',
            role="coast_lamp",
        )
    # Mooring posts, rolled nets and two working skiffs frame the old piers.
    for x, y in [(25, 44), (27, 49), (42, 44), (44, 49), (54, 44), (56, 49)]:
        docks.event(
            "Dock bollard",
            x,
            y,
            'pbMessage("Salt has gathered around the rope. The knot is fresh.")',
            role="dock_bollard",
        )
    for x, y in [(26, 47), (43, 46), (55, 47), (20, 40)]:
        docks.event(
            "Dock nets",
            x,
            y,
            'pbMessage("Nets lie drying in careful folds. A few scales still catch the light.")',
            role="dock_nets",
        )
    docks.event(
        "Dock boat",
        24,
        48,
        'pbMessage("A little working boat, tied close to the pier. Water knocks softly against its hull.")',
        role="dock_boat",
    )
    docks.event(
        "Dock boat",
        45,
        50,
        'pbMessage("A mended oar rests across the seats. Someone has painted over the boat\'s old name.")',
        role="dock_boat",
    )
    docks.event(
        "Dock stall",
        30,
        39,
        'pbMessage("An empty fish stall. The boards have been scrubbed clean.")',
        role="dock_stall",
    )
    docks.event(
        "Quay worker",
        34,
        40,
        'pbMessage("Worker: The small boats still call. Oil out, torn nets back. There is always something to mend.")',
        "trainer_SAILOR",
    )
    docks.event(
        "Dock resident",
        24,
        17,
        'pbMessage("Resident: The windows stay lit so the crews can find the quay. Even when nobody is expected.")',
        "NPC 14",
    )
    coastal_shoreline(docks)
    # DOCKS: a few tended courtyard plots, salt grass outside the working quays.
    d = palette.painter(docks)
    dock_event_buffer = {
        (xx, yy)
        for _, x, y, trigger, _ in docks.targets
        if trigger != 3
        for yy in range(y - 1, y + 2)
        for xx in range(x - 1, x + 2)
    }
    for x, y, w, h in [
        (26, 10, 10, 5),
        (54, 16, 8, 3),
        (12, 22, 7, 2),
        (28, 34, 3, 4),
        (58, 33, 4, 6),
    ]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if docks.layers[1][yy][xx] == 0 and (xx, yy) not in dock_event_buffer:
                    docks.layers[0][yy][xx] = tile(1, 0)
                    d.protected.discard((xx, yy))
    for x, y in [(27, 10), (32, 11), (59, 16), (58, 34)]:
        d.plant(palette.AUTUMN, x, y, 2, 2)
    for x, y in [
        (30, 12),
        (33, 13),
        (54, 17),
        (56, 17),
        (13, 22),
        (14, 22),
        (17, 22),
        (28, 35),
        (29, 36),
        (60, 37),
    ]:
        d.decal(palette.WHITE if x % 2 else palette.art(6, 0), x, y)
    for x, y, s in [(7, 33, 2), (11, 38, 2), (15, 43, 1), (61, 40, 2)]:
        palette.rock_group(d, x, y, s, True)
    d.finish()

    shade_water(docks)
    # Two moored wooden sailing ships, approached through existing three-wide piers.
    # Ship art is offset from these reachable interactive mooring points.
    docks.event(
        "Demo prop:ship1",
        27,
        47,
        'pbMessage("The Salt Thread. Its hull smells of pine tar. A cargo list promises flour, hinges and letters.")',
        role="demo_prop",
        asset="ship1",
    )
    docks.event(
        "Demo prop:ship2",
        56,
        47,
        'pbMessage("The Little Promise. Fresh rope and carefully mended sails. A little duck is carved into the tiller.")',
        role="demo_prop",
        asset="ship2",
    )
    for x in [28, 57]:
        docks.rect(x, 48, 1, 1, tile(6, 150), walk=False)
    # Work parties gather in loose groups; the middle of each pier remains open.
    crew = [
        ("ropes", 24, 41),
        ("keeper", 26, 42),
        ("flour", 25, 46),
        ("stars", 27, 45),
        ("letters", 30, 41),
        ("cargo", 33, 42),
        ("museum", 39, 40),
        ("snow", 46, 42),
        ("pie", 53, 40),
        ("sleep", 55, 42),
        ("islands", 54, 46),
        ("repairs", 56, 45),
        ("mate", 50, 40),
    ]
    for i, (key, x, y) in enumerate(crew):
        docks.event(
            "Sailor " + key,
            x,
            y,
            f"Tidebound::DemoLaunch.talk(:{key})",
            "trainer_SAILOR",
            blocks=True,
            direction=[2, 4, 6, 8][i % 4],
        )
    for key, x, y in [("nell", 26, 49), ("oren", 43, 42)]:
        docks.event(
            "Sailor " + key,
            x,
            y,
            f"Tidebound::DemoLaunch.sailor_battle(:{key})",
            "trainer_SAILOR",
            blocks=True,
        )
    docks.event(
        "Island captain", 55, 49, "Tidebound::DemoLaunch.voyage", "trainer_SAILOR", blocks=True
    )
    for x, y in [(35, 38), (48, 39), (51, 41)]:
        docks.event(
            "Demo prop:cargo",
            x,
            y,
            'pbMessage("Crates of lamp oil and flour. The destination is written twice: PSYDUCK ISLAND.")',
            blocks=True,
            role="demo_prop",
            asset="cargo",
        )
        # Collision follows the complete 2x2 stack, not just the interactive anchor.
        for yy in range(y, y + 2):
            for xx in range(x, x + 2):
                docks.walk[yy][xx] = False
    for name, x, y, text in [
        (
            "board",
            51,
            38,
            "NEXT WATCH: The Little Promise, Psyduck Island. Passengers: ask the captain on the eastern pier.",
        ),
        (
            "ledger",
            36,
            41,
            "Flour: twelve sacks. Oil: six tins. Letters: one sealed box. Paid in full, except for the letters.",
        ),
        (
            "memorial",
            19,
            40,
            "A low stone bears names worn shallow by hands. Fresh knots of ribbon hang from the rail beside it.",
        ),
    ]:
        docks.event(
            "Demo prop:" + name,
            x,
            y,
            f'pbMessage("{text}")',
            blocks=True,
            role="demo_prop",
            asset=name,
        )
    return docks
