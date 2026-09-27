"""Discover authored bundles by directory identity, without registration lists."""

import json
import re

from .paths import ROOT

AUDIO = {"music": "BGM", "ambience": "BGS", "effects": "SE", "cues": "ME"}


def unique_keys(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"Duplicate declaration key: {key}")
        record[key] = value
    return record


def bundles(root, category, filename):
    records = {}
    for directory in sorted((root / "content" / category).glob("*")):
        if (
            not directory.is_dir()
            or directory.name.startswith(".")
            or directory.name == "__pycache__"
        ):
            continue
        path = directory / filename
        if not path.is_file():
            raise ValueError(f"{directory}: missing {filename}")
        record = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
        if not isinstance(record, dict):
            raise ValueError(f"{path}: expected an object")
        records[directory.name] = record
    return records


def validate_names(root):
    """Catch nonportable authoring names before writing any generated files."""
    seen = set()
    engine_ids = {"pokemon", "items", "trainers"}
    roles = {
        "pokemon": {
            "species.json",
            "front.png",
            "back.png",
            "icon.png",
            "front_shiny.png",
            "back_shiny.png",
            "cry.ogg",
        },
        "items": {"item.json", "icon.png"},
        "trainers": {"trainer.json", "portrait.png", "character.png"},
        "props": {"prop.json", "image.png"},
        "actors": {"character.png"},
    }
    categories = roles.keys() | {"maps", "audio", "ui", "effects", "tilesets"}
    for path in sorted((root / "content").rglob("*")):
        relative = path.relative_to(root / "content")
        if (
            "__pycache__" in relative.parts
            or path.name == "AGENTS.md"
            or relative.parts[0] == "overrides"
        ):
            continue
        if relative.parts[0] not in categories:
            raise ValueError(f"Unknown content category: {relative.parts[0]}")
        key = relative.as_posix().casefold()
        if key in seen:
            raise ValueError(f"Case-insensitive content collision: {relative}")
        seen.add(key)
        engine_id = len(relative.parts) == 2 and relative.parts[0] in engine_ids
        pattern = (
            r"[A-Z][A-Z0-9]*(?:_[1-9][0-9]*)?" if engine_id else r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*"
        )
        name = path.name if path.is_dir() else path.stem
        if not re.fullmatch(pattern, name) or (
            path.is_file() and path.suffix not in (".json", ".py", ".png", ".ogg")
        ):
            raise ValueError(
                f"Invalid content name: {relative}; use lower_snake_case (engine IDs keep uppercase)"
            )

        category = relative.parts[0]
        if path.is_file() and category in roles:
            if len(relative.parts) != 3 or path.name not in roles[category]:
                raise ValueError(f"{relative}: expected bundle files {sorted(roles[category])}")
        if path.is_file() and category in {"ui", "effects", "tilesets"}:
            if (
                path.suffix != ".png"
                and not (category == "tilesets" and path.name == "tileset.json")
            ) or (category != "tilesets" and len(relative.parts) != 2):
                raise ValueError(f"{relative}: expected an approved PNG in {category}/")
        if category == "audio" and len(relative.parts) > 1:
            if relative.parts[1] not in AUDIO or (
                path.is_file() and (len(relative.parts) != 3 or path.suffix != ".ogg")
            ):
                raise ValueError(
                    f"{relative}: audio requires music/ambience/effects/cues and an Ogg file"
                )
        if category == "actors" and path.is_dir() and len(relative.parts) == 2:
            if not (path / "character.png").is_file():
                raise ValueError(f"{relative}: missing character.png")


POKEMON = bundles(ROOT, "pokemon", "species.json")
ITEMS = bundles(ROOT, "items", "item.json")
TRAINERS = bundles(ROOT, "trainers", "trainer.json")
