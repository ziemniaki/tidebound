from .transfers import Transfer
from . import definitions
from collections import deque
from rubymarshal.reader import loads
import json, re, struct
from tidebound_dev.scripts.archive import validate_archive


def validate(root, event_scripts_output=None, check_scripts=True):
    G = root / "game"
    if check_scripts:
        validate_archive(G, root / "src")
    masks = json.loads((G / ".generated" / "collisions.json").read_text())
    manifest = json.loads((G / ".generated" / "map_manifest.json").read_text())
    spawns = {d.id: list(d.arrivals) for d in definitions.load(root).values()}
    native_maps = {
        spec["id"]: loads((G / f"Data/Map{spec['id']:03}.rxdata").read_bytes()).attributes
        for spec in manifest
    }
    # Editor-created maps can use ordinary incoming transfers without named entrances.
    for native in native_maps.values():
        for event in native["@events"].values():
            for page in event.attributes["@pages"]:
                for command in page.attributes["@list"]:
                    attrs = command.attributes
                    if attrs["@code"] == 201 and attrs["@parameters"][0] == 0:
                        _, mid, x, y, *_ = attrs["@parameters"]
                        if mid in spawns and (x, y) not in spawns[mid]:
                            spawns[mid].append((x, y))
    maze_path = G / ".generated/maze_manifest.json"
    maze_data = json.loads(maze_path.read_text()) if maze_path.exists() else {}
    fail = []
    event_scripts = []
    count = 0
    for spec in manifest:
        mid = spec["id"]
        m = native_maps[mid]
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

        arrivals = spawns.get(mid, [])
        q = deque(p for p in arrivals if walk(*p))
        seen = set(q)
        while q:
            x, y = q.popleft()
            for p in [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]] + (
                [(dx, dy) for sx, sy, dx, dy in maze_data["warps"] if (x, y) == (sx, sy)]
                if mid == maze_data.get("map")
                else []
            ):
                if p not in seen and walk(*p):
                    seen.add(p)
                    q.append(p)
        for spawn in arrivals:
            if spawn not in seen or not walk(*spawn):
                fail.append(f"{mid} unreachable arrival {spawn}")
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
                if (
                    arrivals
                    and page["@trigger"] not in (3, 4)
                    and name not in ["Lapras", "Pond obelisk (Surf)"]
                ):
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
                for command in page["@list"]:
                    attrs = command.attributes
                    if attrs["@code"] == 201 and attrs["@parameters"][0] == 0:
                        _, destination, tx, ty, direction, *_ = attrs["@parameters"]
                        try:
                            Transfer(destination, tx, ty, direction or 2).validate(masks)
                        except ValueError as error:
                            fail.append(f"{label}: {error}")
                code = "\n".join(
                    str(c.attributes["@parameters"][0])
                    for c in page["@list"]
                    if c.attributes["@code"] in (355, 655)
                )
                if code:
                    event_scripts.append({"name": f"Map{label}", "code": code})
                if re.search(r"\bWorld\s*\.\s*travel(?:_coast)?\b", code):
                    fail.append(
                        f"{label}: undeclared transfer; use native Transfer Player or a tested feature method"
                    )
                count += 1
        for kind in ("bgm", "bgs"):
            name = str(m[f"@{kind}"].attributes["@name"])
            if (
                m[f"@autoplay_{kind}"]
                and name
                and not any(
                    (G / "Audio" / kind.upper() / (name + suffix)).is_file()
                    and not (name + suffix).lower().endswith(".wma")
                    for suffix in ("", ".ogg", ".wav", ".mid", ".midi")
                )
            ):
                fail.append(f"{mid} missing {kind.upper()} {name}")
        print(f"Map {mid}: {len(seen)} reachable walkable cells; {len(m['@events'])} events")
    metadata = loads((G / "Data/map_metadata.dat").read_bytes())
    for mid in spawns:
        back = str(metadata[mid].attributes["@battle_background"])
        for suffix in ["_bg", "_base0", "_base1", "_message"]:
            if not (G / "Graphics/Battlebacks" / f"{back}{suffix}.png").exists():
                fail.append(f"{mid} missing battleback {back}{suffix}")
    if fail:
        raise RuntimeError("\n".join(fail))
    if event_scripts_output:
        event_scripts_output.write_text(json.dumps(event_scripts), encoding="utf-8")
    print(
        f"PASS: {count} event pages; declared arrivals/transfers and static interaction reachability checked. Scripted routes need gameplay scenarios."
    )
