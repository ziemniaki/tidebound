"""Explicit editor import with a three-way comparison against the last export."""

import hashlib
import json
from PIL import Image
from rubymarshal.reader import loads
from .data import encode, map_record, native_map, decode, dump, read
from .tilesets import sources
from ..files import sha256

SESSION = ".build/editor.json"


def bindings(root):
    result = {}
    for path in sorted((root / "content/maps").glob("*/map.json")):
        definition = read(path)
        name = path.parent.relative_to(root).as_posix()
        result[f"{name}/layout.json"] = ("map", definition["id"])
        result[f"{name}/map.json"] = ("info", definition["id"])
    for identifier, (folder, record) in sources(root).items():
        name = folder.relative_to(root).as_posix()
        result[f"{name}/tileset.json"] = ("tileset", identifier)
        result[f"{name}/image.png"] = ("image", identifier)
    return result


def image_value(path):
    # A pixel fingerprint avoids false conflicts from different PNG encoders.
    with Image.open(path) as image:
        pixels = image.convert("RGBA")
        return hashlib.sha256(str(pixels.size).encode() + pixels.tobytes()).hexdigest()


def read_source(root, name):
    path = root / name
    if path.suffix == ".png":
        return image_value(path)
    value = read(path)
    if path.name == "map.json":
        return {
            "name": value["name"],
            "parent_id": value.get("parent_id", 0),
            "order": value.get("order") or value["id"],
        }
    return value


def native_values(root, links):
    if not links:
        return {}
    game = root / "game"
    tilesets = loads((game / "Data/Tilesets.rxdata").read_bytes())
    infos = loads((game / "Data/MapInfos.rxdata").read_bytes())
    result = {}
    for name, (kind, identifier) in links.items():
        if kind == "map":
            result[name] = map_record(
                loads((game / f"Data/Map{identifier:03}.rxdata").read_bytes())
            )
        elif kind == "tileset":
            result[name] = encode(tilesets[identifier])
        elif kind == "image":
            image = str(tilesets[identifier].attributes["@tileset_name"])
            result[name] = image_value(game / f"Graphics/Tilesets/{image}.png")
        else:
            attrs = infos[identifier].attributes
            result[name] = {k: encode(attrs["@" + k]) for k in ("name", "parent_id", "order")}
    return result


def other_files(root, links):
    # Changes outside this importer remain native inputs. Name them rather than
    # pretending that "imported" also covers stock maps, scripts or the database.
    owned = {f"Map{identifier:03}.rxdata" for kind, identifier in links.values() if kind == "map"}
    return {
        p.name: sha256(p)
        for p in sorted((root / "game/Data").glob("Map[0-9]*.rxdata"))
        if p.name not in owned
    }


def remember(root):
    links = bindings(root)
    path = root / SESSION
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "bindings": links,
                "native": native_values(root, links),
                "other": other_files(root, links),
            }
        )
    )


def require_import(root):
    path = root / SESSION
    if not path.exists():
        return
    session = read(path)
    current = native_values(root, session["bindings"])
    changed = [name for name in current if current[name] != session["native"][name]]
    if changed:
        raise ValueError(
            "Saved RPG Maker changes need uv run editor import before rebuilding:\n"
            + "\n".join(changed)
        )


def merge(base, source, edited, path):
    if edited == base or source == edited:
        return source
    if source == base:
        return edited
    if all(isinstance(v, dict) for v in (base, source, edited)):
        result = {}
        missing = object()
        for key in dict.fromkeys([*source, *edited]):
            b, s, e = (v.get(key, missing) for v in (base, source, edited))
            value = merge(b, s, e, f"{path}/{key}")
            if value is not missing:
                result[key] = value
        return result
    if all(isinstance(v, list) for v in (base, source, edited)) and len(base) == len(source) == len(
        edited
    ):
        return [
            merge(b, s, e, f"{path}/{i}") for i, (b, s, e) in enumerate(zip(base, source, edited))
        ]
    raise ValueError(
        f"Editor/source conflict at {path}. Keep both edits and resolve this field before importing."
    )


def import_changes(root):
    path = root / SESSION
    if not path.exists():
        raise ValueError(
            "No editor export to compare. Run uv run editor before editing the project."
        )
    session = read(path)
    current = native_values(root, session["bindings"])
    other = other_files(root, session["bindings"])
    changed_other = [
        name
        for name in other.keys() | session.get("other", {}).keys()
        if other.get(name) != session.get("other", {}).get(name)
    ]
    if changed_other:
        print(
            "Native maps outside authored bundles were preserved, not imported. "
            "Add new maps as content/maps bundles; keep stock/database edits in game/:\n"
            + "\n".join(changed_other)
        )
    pending = {}
    for name, edited in current.items():
        if edited == session["native"][name]:
            continue
        source = read_source(root, name)
        result = merge(session["native"][name], source, edited, name)
        if name.endswith(".png"):
            if result == source:
                continue
            native = loads((root / "game/Data/Tilesets.rxdata").read_bytes())
            filename = str(native[session["bindings"][name][1]].attributes["@tileset_name"])
            result = (root / f"game/Graphics/Tilesets/{filename}.png").read_bytes()
        elif name.endswith("layout.json"):
            native_map(result)  # Validate native tables before writing any source.
            metadata = name.replace("layout.json", "map.json")
            declaration = pending.get(metadata, read(root / metadata))
            reserved = declaration["events"]
            added = edited["events"].keys() - session["native"][name]["events"].keys()
            for event in added:
                if int(event) in reserved.values() and event not in source["events"]:
                    raise ValueError(
                        f"{name}: event {event} reuses a reserved ID; allocate above {max(reserved.values())}"
                    )
                if int(event) not in reserved.values():
                    reserved[f"event_{event}"] = int(event)
            if added:
                pending[metadata] = declaration
        elif name.endswith("tileset.json"):
            decode(result)
        elif name.endswith("map.json"):
            result = {**pending.get(name, read(root / name)), **result}
        pending[name] = result
    # Compute every merge first. Conflicts never partially import a session.
    for name, result in pending.items():
        target = root / name
        if target.suffix == ".png":
            target.write_bytes(result)
        else:
            target.write_text(dump(result))
    remember(root)
    print(f"Imported {len(pending)} changed map/tileset files. Review git diff; rebuild to play.")
