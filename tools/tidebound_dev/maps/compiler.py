"""Export authored map records; procedural tools write the same records once."""

from dataclasses import dataclass
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .definitions import load
from .data import native_map, read
from . import scenery, tilesets
from .serialization import serialize


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
        self.definition = definition
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
            if eid in definition.retired_event_ids:
                raise ValueError(f"Map {self.id}: event {eid} reuses a retired ID")
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
    for name, definition in sorted(load(paths.root).items(), key=lambda item: item[1].id):
        record = read(paths.root / "content/maps" / name / "layout.json")
        tid = record["tileset_id"]
        if not 0 < tid < len(native_tilesets) or not native_tilesets[tid]:
            raise ValueError(f"Map {name}: missing tileset {tid}")
        area = AuthoredMap(definition, record, native_tilesets[tid])
        if tid in sources:
            folder = sources[tid][0]
            if (folder / "windows.png").exists():
                area.light_mask = f"{folder.name}/windows.png"
        area.key = name
        maps.append(area)
    return maps


def build(root):
    paths = BuildPaths(root)
    paths.generated.mkdir(parents=True, exist_ok=True)
    (root / ".build/maps").mkdir(parents=True, exist_ok=True)
    tilesets.build(root)
    maps = construct(paths)
    scenery.window_lights(paths, maps)
    serialize(paths, maps)
    return maps
