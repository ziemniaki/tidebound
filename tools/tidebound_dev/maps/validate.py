from .transfers import Transfer
from . import definitions
from collections import deque
from rubymarshal.reader import loads
import json, re, struct
from tidebound_dev.scripts.archive import validate_archive


def validate(root, event_scripts_output=None, check_scripts=True):
    D = root / "game"
    G = root / "game"
    if check_scripts:
        validate_archive(G, D.parent / "src")
    masks = json.loads((D / ".generated" / "collisions.json").read_text())
    manifest = json.loads((D / ".generated" / "map_manifest.json").read_text())
    spawns = {mid: definition.arrivals for mid, definition in definitions.BY_ID.items()}
    maze_data = json.loads((D / ".generated" / "maze_manifest.json").read_text())
    fail = []
    event_scripts = []
    count = 0
    for spec in manifest:
        mid = spec["id"]
        m = loads((G / f"Data/Map{mid:03}.rxdata").read_bytes()).attributes
        mask = masks[str(mid)]
        w = spec["width"]
        h = spec["height"]
        raw = m["@data"]._dump()
        if (
            (m["@width"], m["@height"]) != (w, h)
            or len(mask) != h
            or any(len(row) != w for row in mask)
        ):
            fail.append(f"{mid} map/mask dimensions disagree with manifest")
            continue
        if (
            len(raw) < 20
            or struct.unpack("<5i", raw[:20]) != (3, w, h, 3, w * h * 3)
            or len(raw) != 20 + w * h * 3 * 2
        ):
            fail.append(f"{mid} tile table dimensions disagree with manifest")
            continue

        def walk(x, y):
            return 0 <= x < w and 0 <= y < h and mask[y][x] == "1"

        q = deque([spawns[mid][0]])
        seen = set(q)
        while q:
            x, y = q.popleft()
            for p in [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]] + (
                [(dx, dy) for sx, sy, dx, dy in maze_data["warps"] if (x, y) == (sx, sy)]
                if mid == 114
                else []
            ):
                if p not in seen and walk(*p):
                    seen.add(p)
                    q.append(p)
        for spawn in spawns[mid]:
            if spawn not in seen or not walk(*spawn):
                fail.append(f"{mid} unreachable arrival {spawn}")
        transfers = {}
        for declaration in spec.get("transfers", []):
            key = (declaration["event"], declaration["page"])
            if key in transfers:
                fail.append(f"{mid}: duplicate transfer declaration for {key}")
            transfers[key] = Transfer(
                **{k: v for k, v in declaration.items() if k not in ("event", "page")}
            )
        used_transfers = set()
        for event_id, ev in m["@events"].items():
            e = ev.attributes
            x, y = e["@x"], e["@y"]
            name = str(e["@name"])
            if not (0 <= x < w and 0 <= y < h):
                fail.append(f"{mid} event {name} outside map at {x},{y}")
            for page_index, record in enumerate(e["@pages"]):
                page = record.attributes
                label = f"{mid}/{name}/page{page_index + 1}"
                charset = str(page["@graphic"].attributes["@character_name"])
                if charset and not (G / "Graphics/Characters" / f"{charset}.png").exists():
                    fail.append(f"{label} missing charset {charset}")
                if page["@trigger"] not in (3, 4) and name not in ["Lapras", "Pond obelisk (Surf)"]:
                    reachable = (
                        (x, y) in seen
                        if page["@trigger"] == 1
                        else any(
                            (x + dx, y + dy) in seen
                            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                        )
                    )
                    if not reachable:
                        fail.append(f"{label} unreachable event at {x},{y}")
                if any(c.attributes["@code"] == 201 for c in page["@list"]):
                    fail.append(
                        f"{label}: native Transfer Player command; use Map.door or a tested feature method"
                    )
                code = "\n".join(
                    str(c.attributes["@parameters"][0])
                    for c in page["@list"]
                    if c.attributes["@code"] in (355, 655)
                )
                if code:
                    event_scripts.append({"name": f"Map{label}", "code": code})
                key = (event_id, page_index)
                transfer = transfers.get(key)
                if transfer:
                    used_transfers.add(key)
                    try:
                        transfer.validate(masks)
                        if code.strip() != transfer.script():
                            fail.append(f"{label}: event code disagrees with declared transfer")
                    except ValueError as error:
                        fail.append(f"{label}: {error}")
                elif re.search(r"\bWorld\s*\.\s*travel(?:_coast)?\b", code):
                    fail.append(
                        f"{label}: undeclared transfer; use Map.door or a tested feature method"
                    )
                count += 1
        for key in transfers.keys() - used_transfers:
            fail.append(f"{mid}: transfer refers to missing event/page {key}")
        bgm = str(m["@bgm"].attributes["@name"])
        if not (G / "Audio/BGM" / f"{bgm}.ogg").exists():
            fail.append(f"{mid} missing BGM {bgm}")
        print(f"Map {mid}: {len(seen)} connected walkable cells; {len(m['@events'])} events")
    metadata = loads((G / "Data/map_metadata.dat").read_bytes())
    for mid in spawns:
        back = str(metadata[mid].attributes["@battle_background"])
        for suffix in ["_bg", "_base0", "_base1", "_message"]:
            if not (G / "Graphics/Battlebacks" / f"{back}{suffix}.png").exists():
                fail.append(f"{mid} missing battleback {back}{suffix}")
    coast = masks["102"]
    if len(coast) != 88 or len(coast[0]) != 108:
        fail.append("coast dimensions must be 108x88")
    if not all(
        9 <= x < 99 and 7 <= y < 81
        for y, row in enumerate(coast)
        for x, v in enumerate(row)
        if v == "1"
    ):
        fail.append("coast camera margin")
    if not all(coast[y][x] == "0" for y in range(30, 55) for x in range(80, 108)):
        fail.append("open sea beyond pier")
    if fail:
        raise RuntimeError("\n".join(fail))
    if event_scripts_output:
        event_scripts_output.write_text(json.dumps(event_scripts), encoding="utf-8")
    print(
        f"PASS: {count} event pages; declared arrivals/transfers and static interaction reachability checked. Scripted routes need gameplay scenarios."
    )
