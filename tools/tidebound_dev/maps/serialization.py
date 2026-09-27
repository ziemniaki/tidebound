from ..files import save_png
from .preview import PreviewRenderer
from .registry import write_registry
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import json
import hashlib

from .model import obj


def map_revision(game):
    # Essentials compares this native editor field to the copy saved with the
    # map factory. A changed layout/tileset must reload cached maps on Game.load.
    digest = hashlib.sha256()
    paths = sorted((game / "Data").glob("Map[0-9]*.rxdata"))
    for path in [*paths, game / "Data/Tilesets.rxdata"]:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return int.from_bytes(digest.digest()[:4], "little") & 0x7FFFFFFF


def serialize(paths, maps):
    write_registry(paths.root, maps)
    for m in maps:
        (paths.game / f"Data/Map{m.id:03}.rxdata").write_bytes(m.serialize())
    system = loads((paths.game / "Data/System.rxdata").read_bytes())
    system.attributes.update(
        {
            "@start_map_id": 115,
            "@start_x": 7,
            "@start_y": 8,
            "@magic_number": map_revision(paths.game),
        }
    )
    (paths.game / "Data/System.rxdata").write_bytes(writes(system))
    infos = loads((paths.game / "Data/MapInfos.rxdata").read_bytes())
    metadata = loads((paths.game / "Data/map_metadata.dat").read_bytes())
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
    (paths.game / "Data/MapInfos.rxdata").write_bytes(writes(infos))
    (paths.game / "Data/map_metadata.dat").write_bytes(writes(metadata))
    collisions = {
        str(m.id): ["".join("1" if b else "0" for b in row) for row in m.walk] for m in maps
    }
    (paths.generated / "collisions.json").write_text(json.dumps(collisions, indent=2))
    ruby = (
        "module Tidebound\n  MAP_PASSAGES = {\n"
        + "".join(f"    {k} => {json.dumps(v)},\n" for k, v in collisions.items())
        + "  }\nend\n"
    )
    (paths.root / "src" / "generated/map_passages.rb").write_text(ruby)
    preview_dir = paths.root / ".build/maps"
    preview_dir.mkdir(parents=True, exist_ok=True)
    previews = PreviewRenderer(paths.game)
    for m in maps:
        save_png(previews.render(m), preview_dir / f"map_{m.id}_preview.png")
    (paths.generated / "map_manifest.json").write_text(
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
