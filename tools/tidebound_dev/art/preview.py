"""Select authored content and replace Main only in a disposable player."""

from pathlib import Path
from rubymarshal.writer import writes

from ..catalog import AUDIO, bundles
from ..scripts.archive import replace_main
from . import props
from .files import exports


def select(root, name):
    kind, separator, identifier = name.partition("/")
    if not separator or not identifier:
        raise ValueError(
            "Preview expects pokemon/ID, actors/name, items/ID, trainers/ID, props/name, ui/name, effects/name or audio/category/name"
        )
    record = {"kind": kind, "name": identifier}
    if kind == "pokemon" and identifier in bundles(root, "pokemon", "species.json"):
        species, _, form = identifier.partition("_")
        return {**record, "species": species, "form": int(form or 0)}
    if kind == "props":
        records = props.load(root)
        if identifier in records:
            return {
                **record,
                **records[identifier],
                "path": f"Graphics/Pictures/{records[identifier]['file']}.png",
            }
    destinations = {
        "actors": ("characters", "Graphics/Characters"),
        "items": ("items", "Graphics/Items"),
        "trainers": ("trainers", "Graphics/Trainers"),
        "ui": ("pictures", "Graphics/Pictures/ui"),
        "effects": ("pictures", "Graphics/Pictures/effects"),
    }
    if kind == "audio":
        category, _, identifier = identifier.partition("/")
        if category in AUDIO and identifier:
            destinations["audio"] = ("audio", f"Audio/{AUDIO[category]}")
            record["name"] = f"{AUDIO[category]}/{identifier}"
    if kind in destinations:
        viewer, folder = destinations[kind]
        stem = f"game/{folder}/{identifier}"
        matches = [
            export.destination
            for export in exports(root)
            if Path(export.destination).with_suffix("").as_posix() == stem
        ]
        if len(matches) == 1:
            return {**record, "kind": viewer, "path": matches[0].removeprefix("game/")}
    raise ValueError(f"Unknown custom asset: {name}. Use its exact content ID without extension.")


def prepare(game, record):
    driver = Path(__file__).with_suffix(".rb").read_bytes()
    driver += b'\nAssetPreview.run(load_data("Data/AssetPreview.rxdata"))\n'
    replace_main(game, driver)
    (game / "Data/AssetPreview.rxdata").write_bytes(writes(record))
