from .registry import write_registry
from . import definitions
from PIL import Image, ImageDraw
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import copy
import json
import struct

from .model import Map, RoadMap, tile, table, command, script
from rubymarshal.classes import Symbol
from .model import obj


def serialize(paths, maps):
    write_registry(paths.root, maps)
    for m in maps:
        (paths.game / f"Data/Map{m.id:03}.rxdata").write_bytes(m.serialize())
    system = loads((paths.game / "Data/System.rxdata").read_bytes())
    system.attributes.update(
        {"@start_map_id": 115, "@start_x": 7, "@start_y": 8, "@magic_number": 26092503}
    )
    (paths.game / "Data/System.rxdata").write_bytes(writes(system))
    infos = loads((paths.game / "Data/MapInfos.rxdata").read_bytes())
    metadata = loads((paths.game / "Data/map_metadata.dat").read_bytes())
    template = metadata[1]
    for m in maps:
        infos[m.id] = obj(
            "RPG::MapInfo",
            name=m.name,
            parent_id=0,
            order=m.id,
            expanded=True,
            scroll_x=320,
            scroll_y=240,
        )
        md = loads(writes(template))
        md.attributes.update({"@id": m.id, **definitions.BY_ID[m.id].native_metadata(m.name)})
        metadata[m.id] = md
    (paths.game / "Data/MapInfos.rxdata").write_bytes(writes(infos))
    (paths.game / "Data/map_metadata.dat").write_bytes(writes(metadata))
    collisions = {
        str(m.id): ["".join("1" if b else "0" for b in row) for row in m.walk] for m in maps
    }
    (paths.tools / "generated" / "collisions.json").write_text(json.dumps(collisions, indent=2))
    ruby = (
        "module Tidebound\n  MAP_PASSAGES = {\n"
        + "".join(f"    {k} => {json.dumps(v)},\n" for k, v in collisions.items())
        + "  }\nend\n"
    )
    (paths.tools.parent / "src" / "generated/map_passages.rb").write_text(ruby)
    for m in maps:
        m.render(paths.game).save(paths.tools / "generated" / f"map_{m.id}_preview.png")
    (paths.tools / "generated" / "map_manifest.json").write_text(
        json.dumps(
            [
                {"id": m.id, "name": m.name, "width": m.w, "height": m.h, "targets": m.targets}
                for m in maps
            ],
            indent=2,
        )
    )
    print("Built", len(maps), "native maps and collision masks")
