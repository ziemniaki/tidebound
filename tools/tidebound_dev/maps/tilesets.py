"""Fixed native tilesets. Appending tiles never renumbers existing map references."""

from PIL import Image
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .data import decode, encode, read


def sources(root):
    records = {}
    for path in sorted((root / "content/tilesets").glob("*/tileset.json")):
        record = read(path)
        identifier = record["id"]
        if type(identifier) is not int or identifier < 1 or identifier in records:
            raise ValueError(f"{path}: tileset IDs must be positive and unique")
        records[identifier] = (path.parent, record)
    return records


def exports(root):
    from ..art.export import Export

    for folder, record in sources(root).values():
        yield Export(folder / "image.png", f"game/Graphics/Tilesets/{record['tileset_name']}.png")
    for path in sorted((root / "content/tilesets/ocean").glob("*.png")):
        name = path.stem
        yield Export(
            root / f"content/tilesets/ocean/{name}.png",
            f"game/Graphics/Autotiles/Tidebound {name.replace('_', ' ').title()}.png",
        )


def build(root):
    path = root / "game/Data/Tilesets.rxdata"
    records = loads(path.read_bytes())
    for identifier, (folder, source) in sources(root).items():
        if len(records) <= identifier:
            records.extend([None] * (identifier + 1 - len(records)))
        with Image.open(folder / "image.png") as image:
            width, height = image.size
        if width != 256 or height % 32 or not 0 < height <= 16384:
            raise ValueError(
                f"{folder}: tileset must be 256px wide and at most 16384px tall in 32px rows"
            )
        tables = [source[key] for key in ("passages", "priorities", "terrain_tags")]
        if len({tuple(t["shape"]) for t in tables}) != 1:
            raise ValueError(f"{folder}: passage/priority/terrain tables must have the same shape")
        if tables[0]["shape"][1:] != [1, 1] or tables[0]["shape"][0] < 384:
            raise ValueError(f"{folder}: tileset tables must contain the native autotile slots")
        records[identifier] = decode(source)
    path.write_bytes(writes(records))


def passages(record):
    """Essentials' ordinary tile passage (events and Surf are runtime state)."""
    passages = encode(record.attributes["@passages"])["rows"][0]
    priorities = encode(record.attributes["@priorities"])["rows"][0]
    terrain = encode(record.attributes["@terrain_tags"])["rows"][0]

    def passage(layers, x, y, direction=0):
        bit = 15 if direction == 0 else 1 << (direction // 2 - 1)
        for layer in reversed(layers):
            tile = layer[y][x]
            if tile == 0:
                continue
            if not 0 <= tile < len(passages):
                raise ValueError(
                    f"Tile {tile} at {x},{y} exceeds tileset {record.attributes['@id']}"
                )
            if terrain[tile] == 13:  # Essentials Neutral
                continue
            if passages[tile] & bit:
                return False
            if priorities[tile] == 0:
                return True
        return True

    return passage
