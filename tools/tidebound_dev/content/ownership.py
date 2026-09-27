"""Own only declared custom records; stock databases remain rebuild inputs."""

import json
from pathlib import PurePosixPath
from rubymarshal.classes import Symbol
from rubymarshal.reader import loads
from rubymarshal.writer import writes

from .species import SPECIES, METRICS
from .species_compiler import pbs_files
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
    previous = recorded(root)
    cleaned = {}
    for name, identifiers in expected["databases"].items():
        database = loads((root / "game/Data" / name).read_bytes())
        old = previous["databases"].get(name, [])
        key = lambda value: Symbol(value) if isinstance(value, str) else value
        for identifier in set(identifiers) - set(old):
            if name not in ("MapInfos.rxdata", "map_metadata.dat") and key(identifier) in database:
                raise ValueError(f"Custom content would overwrite stock {name}: {identifier}")
        retired = set(old) - set(identifiers)
        if retired:
            for identifier in retired:
                database.pop(key(identifier), None)
            cleaned[name] = writes(database)
    # A map declaration explicitly adopts its native editor ID and file.
    map_files = {
        f"game/Data/Map{i:03}.rxdata" for i in expected["databases"].get("MapInfos.rxdata", [])
    }
    for name in set(expected["files"]) - set(previous["files"]) - map_files:
        if (root / name).exists():
            raise ValueError(f"Custom content would overwrite an unowned file: {name}")
    # Record claims before generation so a failed build can be fixed and rerun.
    # Retired outputs are removed first; only our recorded paths can be deleted.
    for name in set(previous["files"]) - set(expected["files"]):
        (root / name).unlink(missing_ok=True)
    for name, data in cleaned.items():
        (root / "game/Data" / name).write_bytes(data)
    (root / MANIFEST).write_text(json.dumps(expected, indent=2) + "\n")


def validate(root):
    if recorded(root) != inventory(root):
        raise ValueError("Content ownership changed; run uv run rebuild")
