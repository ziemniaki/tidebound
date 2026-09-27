"""Explicit editor import with a three-way comparison against the last export."""

import hashlib
import json
from pathlib import PureWindowsPath
from PIL import Image
from rubymarshal.reader import loads
from .data import encode, map_record, native_map, decode, dump, read
from .tilesets import sources
from .definitions import load
import re
import unicodedata

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


def close(root):
    (root / SESSION).unlink(missing_ok=True)


def map_ids(root):
    return sorted(int(p.stem[3:]) for p in (root / "game/Data").glob("Map[0-9]*.rxdata"))


def new_maps(root, session):
    """RPG Maker allocates native IDs; import their full records without a second allocator."""
    infos = loads((root / "game/Data/MapInfos.rxdata").read_bytes())
    pending = {}
    definitions = load(root)
    used = {key.casefold() for key in definitions}
    authored_ids = {definition.id for definition in definitions.values()}
    for identifier in sorted(set(map_ids(root)) - set(session["map_ids"])):
        if identifier in authored_ids:
            raise ValueError(f"New editor map {identifier}: ID already used by an authored map")
        info = infos[identifier].attributes
        name = str(info["@name"])
        ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
        key = re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
        if not key or not key[0].isalpha() or PureWindowsPath(key).is_reserved():
            key = f"map_{identifier}"
        if key.casefold() in used:
            key = f"{key}_{identifier}"
        if key.casefold() in used:
            raise ValueError(f"New map {identifier}: bundle name {key} already exists")
        used.add(key.casefold())
        folder = f"content/maps/{key}"
        pending[f"{folder}/map.json"] = {
            "id": identifier,
            "name": name,
            "entrances": {},
            "parent_id": info["@parent_id"],
            "order": info["@order"],
        }
        pending[f"{folder}/layout.json"] = map_record(
            loads((root / f"game/Data/Map{identifier:03}.rxdata").read_bytes())
        )
        native_map(pending[f"{folder}/layout.json"])
    return pending


def remember(root, links=None):
    if links is None:
        links = bindings(root)
    path = root / SESSION
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "bindings": links,
                "native": native_values(root, links),
                "map_ids": map_ids(root),
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
    added = sorted(set(map_ids(root)) - set(session["map_ids"]))
    changed.extend(f"New native map {identifier}" for identifier in added)
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
            "No editor export to compare. Run uv run editor (or editor prepare) before editing the project."
        )
    session = read(path)
    current = native_values(root, session["bindings"])
    pending = new_maps(root, session)
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
            retired = set(declaration.get("retired_event_ids", []))
            reused = set(map(int, edited["events"])) & retired
            if reused:
                raise ValueError(f"{name}: retired event IDs cannot be reused: {sorted(reused)}")
            removed = session["native"][name]["events"].keys() - result["events"].keys()
            if removed:
                declaration["retired_event_ids"] = sorted(retired | set(map(int, removed)))
                pending[metadata] = declaration
        elif name.endswith("tileset.json"):
            decode(result)
        elif name.endswith("map.json"):
            result = {**pending.get(name, read(root / name)), **result}
        pending[name] = result
    # Compute every merge first. Conflicts never partially import a session.
    for name, result in pending.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".png":
            target.write_bytes(result)
        else:
            target.write_text(dump(result), encoding="utf-8")
    # Source-only additions may not have native exports yet. Keep them out of
    # this editor session until the next prepare, while tracking imported maps.
    links = {
        name: link
        for name, link in bindings(root).items()
        if name in session["bindings"] or name in pending
    }
    remember(root, links)
    print(f"Imported {len(pending)} changed map/tileset files. Review git diff; rebuild to play.")
