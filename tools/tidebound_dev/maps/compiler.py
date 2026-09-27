"""Export authored map records; procedural tools write the same records once."""

import hashlib
import json
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .definitions import load
from .data import native_map, read
from . import scenery, tilesets
from .model import obj
from .registry import write_registry


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


def construct(root):
    native_tilesets = loads((root / "game/Data/Tilesets.rxdata").read_bytes())
    sources = tilesets.sources(root)
    maps = []
    for name, definition in sorted(load(root).items(), key=lambda item: item[1].id):
        record = read(root / "content/maps" / name / "layout.json")
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


def map_revision(game):
    # Essentials compares this native editor field to the copy saved with the
    # map factory. A changed layout/tileset must reload cached maps on Game.load.
    digest = hashlib.sha256()
    paths = sorted((game / "Data").glob("Map[0-9]*.rxdata"))
    for path in [*paths, game / "Data/Tilesets.rxdata"]:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return int.from_bytes(digest.digest()[:4], "little") & 0x7FFFFFFF


def serialize(root, maps):
    game = root / "game"
    write_registry(root, maps)
    for m in maps:
        (game / f"Data/Map{m.id:03}.rxdata").write_bytes(writes(m.native))
    system = loads((game / "Data/System.rxdata").read_bytes())
    system.attributes["@magic_number"] = map_revision(game)
    (game / "Data/System.rxdata").write_bytes(writes(system))
    infos = loads((game / "Data/MapInfos.rxdata").read_bytes())
    metadata = loads((game / "Data/map_metadata.dat").read_bytes())
    template = metadata[1]
    for m in maps:
        infos[m.id] = obj(
            "RPG::MapInfo",
            name=m.name,
            parent_id=m.definition.parent_id,
            order=m.definition.order or m.id,
            expanded=True,
            scroll_x=320,
            scroll_y=240,
        )
        md = loads(writes(template))
        md.attributes.update({"@id": m.id, **m.definition.native_metadata(m.name)})
        metadata[m.id] = md
    (game / "Data/MapInfos.rxdata").write_bytes(writes(infos))
    (game / "Data/map_metadata.dat").write_bytes(writes(metadata))
    collisions = {
        str(m.id): ["".join("1" if b else "0" for b in row) for row in m.walk] for m in maps
    }
    (game / ".generated/collisions.json").write_text(json.dumps(collisions, indent=2))
    ruby = (
        "module Tidebound\n  MAP_PASSAGES = {\n"
        + "".join(f"    {k} => {json.dumps(v)},\n" for k, v in collisions.items())
        + "  }\nend\n"
    )
    (root / "src/generated/map_passages.rb").write_text(ruby)
    (game / ".generated/map_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": m.id,
                    "name": m.name,
                    "width": m.w,
                    "height": m.h,
                }
                for m in maps
            ],
            indent=2,
        )
    )
    print("Built", len(maps), "native maps and collision masks")


def build(root):
    (root / "game/.generated").mkdir(parents=True, exist_ok=True)
    (root / ".build/maps").mkdir(parents=True, exist_ok=True)
    tilesets.build(root)
    maps = construct(root)
    scenery.window_lights(root, maps)
    serialize(root, maps)
    return maps
