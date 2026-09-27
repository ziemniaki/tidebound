"""Export authored map records; procedural tools write the same records once."""

from dataclasses import dataclass
import json
import re
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .definitions import DEFINITIONS
from .data import native_map, read
from . import scenery, tilesets
from .serialization import serialize
from ..files import ruby


@dataclass(frozen=True)
class BuildPaths:
    root: Path

    @property
    def game(self):
        return self.root / "game"

    @property
    def generated(self):
        return self.game / ".generated"


class AuthoredMap:
    def __init__(self, definition, record, tileset):
        self.native = native_map(record)
        fields = self.native.attributes
        self.id, self.name = definition.id, definition.name
        self.w, self.h = fields["@width"], fields["@height"]
        self.tileset = fields["@tileset_id"]
        self.light_mask = None
        rows = record["data"]["rows"]
        if record["data"]["shape"] != [self.w, self.h, 3]:
            raise ValueError(f"Map {self.id}: map dimensions disagree with tile data")
        self.layers = [rows[i * self.h : (i + 1) * self.h] for i in range(3)]
        self.events = fields["@events"]
        for eid, event in self.events.items():
            if eid not in definition.events.values():
                raise ValueError(f"Map {self.id}: event {eid} needs an ID reservation in map.json")
            if eid < 1 or event.attributes["@id"] != eid:
                raise ValueError(f"Map {self.id}: event key and ID disagree: {eid}")
        self.actor_settings = {int(k): v for k, v in definition.actor_settings.items()}
        passable = tilesets.passages(tileset)
        self.walk = [[passable(self.layers, x, y) for x in range(self.w)] for y in range(self.h)]

    def serialize(self):
        return writes(self.native)


def construct(paths):
    native_tilesets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    sources = tilesets.sources(paths.root)
    maps = []
    for name, definition in sorted(DEFINITIONS.items(), key=lambda item: item[1].id):
        record = read(paths.root / "content/maps" / name / "layout.json")
        tid = record["tileset_id"]
        if not 0 < tid < len(native_tilesets) or not native_tilesets[tid]:
            raise ValueError(f"Map {name}: missing tileset {tid}")
        area = AuthoredMap(definition, record, native_tilesets[tid])
        if tid in sources:
            folder = sources[tid][0]
            if (folder / "windows.png").exists():
                area.light_mask = f"{folder.name}/windows.png"
        maps.append(area)
    return maps


def mechanics(paths, maps):
    # Puzzle triggers derive from the editable event pages, so moving a pad moves
    # its runtime geometry too. Reward regions remain explicit authored data.
    maze = next(m for m in maps if m.id == 114)
    goal = next(eid for eid, info in maze.actor_settings.items() if info.get("role") == "room")
    target = maze.events[goal].attributes
    record = {
        "map": maze.id,
        "start": DEFINITIONS["maze"].entrances["entry"][:2],
        "goal": [target["@x"], target["@y"]],
        "pushers": [],
        "warps": [],
        "stops": [],
    }
    for event in maze.events.values():
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
    (paths.generated / "maze_manifest.json").write_text(json.dumps(record, indent=2))
    values = {
        "MAP": maze.id,
        "START": record["start"],
        "PUSHERS": {tuple(p[:2]): p[2] for p in record["pushers"]},
        "STOPS": record["stops"],
        "WARPS": {tuple(p[:2]): p[2:] for p in record["warps"]},
    }
    (paths.root / "src/generated/maze_geometry.rb").write_text(
        "# Generated from authored map events and mechanics.\nmodule Tidebound::PsychicMaze\n"
        + "".join(f"  {key} = {ruby(value)}.freeze\n" for key, value in values.items())
        + "end\n"
    )
    pond = read(paths.root / "content/maps/road/mechanics.json")
    road = next(m for m in maps if m.id == 108)
    native = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())[road.tileset]
    from .data import encode

    tags = encode(native.attributes["@terrain_tags"])["rows"][0]
    pond["water"] = [
        [x, y]
        for x in range(road.w)
        for y in range(road.h)
        if any(tags[layer[y][x]] == 6 for layer in road.layers)
    ]
    (paths.generated / "pond_manifest.json").write_text(json.dumps(pond, indent=2) + "\n")


def build(root):
    paths = BuildPaths(root)
    paths.generated.mkdir(parents=True, exist_ok=True)
    (root / ".build/maps").mkdir(parents=True, exist_ok=True)
    tilesets.build(root)
    maps = construct(paths)
    mechanics(paths, maps)
    scenery.window_lights(paths, maps)
    serialize(paths, maps)
