"""Tidebound puzzle/reward exports derived from native map data."""

import json
import re
from rubymarshal.reader import loads
from ..files import ruby
from ..maps.data import read, encode


def build(root, maps):
    by_name = {area.key: area for area in maps}
    if "coast" in by_name:
        check_coast(by_name["coast"])
    if "maze" in by_name:
        maze(root, by_name["maze"])
    if "road" in by_name:
        pond(root, by_name["road"])


def maze(root, area):
    # Puzzle triggers derive from the editable event pages, so moving a pad moves
    # its runtime geometry too. Reward regions remain explicit authored data.
    goal = next(eid for eid, info in area.actor_settings.items() if info.get("role") == "room")
    target = area.events[goal].attributes
    record = {
        "map": area.id,
        "start": area.definition.entrances["entry"][:2],
        "goal": [target["@x"], target["@y"]],
        "pushers": [],
        "warps": [],
        "stops": [],
    }
    for event in area.events.values():
        e = event.attributes
        for page in e["@pages"]:
            for command in page.attributes["@list"]:
                c = command.attributes
                if c["@code"] == 108 and str(c["@parameters"][0]) == "tidebound:slide_stop":
                    record["stops"].append([e["@x"], e["@y"]])
                if c["@code"] not in (355, 655):
                    continue
                script = str(c["@parameters"][0])
                for kind, pattern in (
                    ("pushers", r"PsychicMaze\.slide\((\d+)\)"),
                    ("warps", r"PsychicMaze\.warp\((\d+),\s*(\d+)\)"),
                ):
                    match = re.search(pattern, script)
                    if match:
                        record[kind].append([e["@x"], e["@y"], *map(int, match.groups())])
    (root / "game/.generated/maze_manifest.json").write_text(json.dumps(record, indent=2))
    values = {
        "MAP": area.id,
        "START": record["start"],
        "PUSHERS": {tuple(p[:2]): p[2] for p in record["pushers"]},
        "STOPS": record["stops"],
        "WARPS": {tuple(p[:2]): p[2:] for p in record["warps"]},
    }
    (root / "src/generated/maze_geometry.rb").write_text(
        "# Generated from authored map events and mechanics.\nmodule Tidebound::PsychicMaze\n"
        + "".join(f"  {key} = {ruby(value)}.freeze\n" for key, value in values.items())
        + "end\n"
    )


def pond(root, road):
    pond = read(root / "content/maps/road/mechanics.json")
    native = loads((root / "game/Data/Tilesets.rxdata").read_bytes())[road.tileset]

    tags = encode(native.attributes["@terrain_tags"])["rows"][0]
    pond["water"] = [
        [x, y]
        for x in range(road.w)
        for y in range(road.h)
        if any(tags[layer[y][x]] == 6 for layer in road.layers)
    ]
    (root / "game/.generated/pond_manifest.json").write_text(json.dumps(pond, indent=2) + "\n")


def check_coast(area):
    coast = area.walk
    if len(coast) != 88 or len(coast[0]) != 108:
        raise ValueError("coast dimensions must be 108x88")
    if not all(
        9 <= x < 99 and 7 <= y < 81 for y, row in enumerate(coast) for x, v in enumerate(row) if v
    ):
        raise ValueError("coast camera margin")
    if not all(not coast[y][x] for y in range(30, 55) for x in range(80, 108)):
        raise ValueError("open sea beyond pier")
