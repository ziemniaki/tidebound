"""Assemble the native editor project from a pinned base and explicit overrides."""

import json
import hashlib
import shutil
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .files import sha256
from .packaging.archives import extract_bundle

DIRECTORIES = ("Data", "PBS", "Graphics", "Audio", "Fonts", "Plugins")
FILES = ("Game.ini", "Game.rxproj", "mkxp.json", "soundfont.sf2")
OVERRIDES = "content/overrides"


def files(game):
    """Only project inputs/outputs; never player saves, logs or editor backups."""
    result = {}
    for name in DIRECTORIES:
        folder = game / name
        if folder.is_symlink():
            raise ValueError(f"Native project directory must not be a symlink: {folder}")
        for path in folder.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Native project file must not be a symlink: {path}")
            if (
                path.is_file()
                and path.name not in (".DS_Store", "Thumbs.db", "desktop.ini")
                and path.suffix.lower() not in (".bak", ".log")
            ):
                result[path.relative_to(game).as_posix()] = path
    for name in FILES:
        path = game / name
        if path.is_symlink():
            raise ValueError(f"Native project file must not be a symlink: {path}")
        if path.is_file():
            result[name] = path
    return result


def native_bytes(root, name, data, links):
    """Ignore generated records and XP's map-tree UI state when importing stock inputs."""
    if name == "Data/MapInfos.rxdata":
        value = loads(data)
        for kind, identifier in links.values():
            if kind == "map":
                value.pop(identifier, None)
        for record in value.values():
            for key in ("@expanded", "@scroll_x", "@scroll_y"):
                record.attributes[key] = False if key == "@expanded" else 0
        return writes(value)
    if name == "Data/Tilesets.rxdata":
        value = loads(data)
        for kind, identifier in links.values():
            if kind == "tileset" and identifier < len(value):
                value[identifier] = None
        while value and value[-1] is None:
            value.pop()
        return writes(value)
    if name == "Data/System.rxdata":
        value = loads(data)
        value.attributes["@magic_number"] = 0
        return writes(value)
    return data


def file_state(root, links):
    game = root / "game"
    excluded = set()
    tilesets = (
        loads((game / "Data/Tilesets.rxdata").read_bytes())
        if any(kind == "image" for kind, _ in links.values())
        else []
    )
    for kind, identifier in links.values():
        if kind == "map":
            excluded.add(f"Data/Map{identifier:03}.rxdata")
        elif kind == "image":
            excluded.add(
                f"Graphics/Tilesets/{tilesets[identifier].attributes['@tileset_name']}.png"
            )
    return {
        name: hashlib.sha256(native_bytes(root, name, path.read_bytes(), links)).hexdigest()
        for name, path in files(game).items()
        if name not in excluded
    }


def override_state(root):
    return {name: sha256(path) for name, path in overrides(root).items()}


def overrides(root):
    folder = root / OVERRIDES
    known = files(folder)
    extra = [
        p
        for p in folder.rglob("*")
        if p.is_file() and p.relative_to(folder).as_posix() not in known and p.name != "AGENTS.md"
    ]
    if extra:
        raise ValueError(f"Unsupported native override path: {extra[0]}")
    return known


def prepare(root):
    """Called only after the editor guard; old outputs can never become build inputs."""
    baseline = root / "runtime/essentials/base.zip"
    pin = json.loads((baseline.with_suffix(".json")).read_text())
    if sha256(baseline) != pin["sha256"]:
        raise ValueError("Essentials baseline hash mismatch: runtime/essentials/base.zip")
    replacements = overrides(root)
    game = root / "game"
    for path in files(game).values():
        path.unlink()
    shutil.rmtree(game / ".generated", ignore_errors=True)
    extract_bundle(baseline, game)
    for name, source in replacements.items():
        target = game / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (root / "src/generated").mkdir(parents=True, exist_ok=True)
    for path in (root / "src/generated").glob("*.rb"):
        path.unlink()


def generated_files(root):
    """Files which must be edited through their authored owner, never an opaque override."""
    from .art.ownership import inventory
    from .content.ownership import inventory as content_inventory

    assets, _ = inventory(root)
    content = content_inventory(root)
    return {
        name.removeprefix("game/")
        for name in [*assets, *content["files"]]
        if name.startswith("game/")
    } | {
        "Data/Scripts.rxdata",
        "PBS/map_metadata.txt",
        *("Data/" + name for name in content["databases"] if name != "MapInfos.rxdata"),
    }


def validate_overrides(root):
    collisions = overrides(root).keys() & generated_files(root)
    if collisions:
        raise ValueError(
            "Native override has an authored owner; edit its source instead:\n"
            + "\n".join(sorted(collisions))
        )
