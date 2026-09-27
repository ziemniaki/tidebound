"""Describe generated content for validation and editor ownership."""

import json
from pathlib import PurePosixPath

from .species_compiler import SPECIES, METRICS, pbs_files
from .story import ITEMS, TRAINERS
from ..maps.definitions import load

MANIFEST = "game/.generated/content.json"
TABLES = {
    "species.dat",
    "species_metrics.dat",
    "items.dat",
    "trainer_types.dat",
    "encounters.dat",
    "map_metadata.dat",
    "MapInfos.rxdata",
}


def inventory(root):
    definitions = load(root)
    maps = sorted(d.id for d in definitions.values())
    files = [f"game/PBS/{name}" for name in pbs_files(SPECIES) | pbs_files(METRICS)]
    files += [
        "game/PBS/items_tidebound_story.txt",
        "game/PBS/trainer_types_tidebound_story.txt",
        "game/PBS/encounters_tidebound.txt",
        "src/generated/wild_forms.rb",
    ]
    files += [f"game/Data/Map{i:03}.rxdata" for i in maps]
    return {
        "databases": {
            "species.dat": sorted(SPECIES),
            "species_metrics.dat": sorted(METRICS),
            "items.dat": sorted(ITEMS),
            "trainer_types.dat": sorted(TRAINERS),
            "encounters.dat": sorted(f"{d.id}_0" for d in definitions.values() if d.encounters),
            "map_metadata.dat": maps,
            "MapInfos.rxdata": maps,
        },
        "files": sorted(files),
    }


def recorded(root):
    value = json.loads((root / MANIFEST).read_text())
    if value["databases"].keys() - TABLES:
        raise ValueError("Unknown owned content database")
    for name in value["files"]:
        path = PurePosixPath(name)
        if (
            ".." in path.parts
            or "\\" in name
            or path.parts[:2]
            not in (("game", "Data"), ("game", "PBS"), ("game", ".generated"), ("src", "generated"))
        ):
            raise ValueError(f"Invalid owned content path: {name}")
    return value


def prepare(root, expected):
    path = root / MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(expected, indent=2) + "\n")


def validate(root):
    if recorded(root) != inventory(root):
        raise ValueError("Content ownership changed; run uv run build --compile-only")
