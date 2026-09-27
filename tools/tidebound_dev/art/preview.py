"""Select an asset and replace Main only in a disposable development player."""

import json
import zlib
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .pokemon import POKEMON
from .files import copies


def select(root, name):
    kind, separator, identifier = name.partition("/")
    if not separator or not identifier:
        raise ValueError(
            "Preview expects pokemon/ID, characters/NAME, items/ID, trainers/ID, props/NAME, pictures/PATH or audio/CATEGORY/NAME"
        )
    record = {"kind": kind, "name": identifier}
    if kind == "pokemon" and identifier in POKEMON:
        species, _, form = identifier.partition("_")
        return {**record, "species": species, "form": int(form or 0)}
    if kind == "props":
        props = json.loads((root / "assets/props.json").read_text())
        if identifier in props:
            return {
                **record,
                **props[identifier],
                "path": f"Graphics/Pictures/{props[identifier]['file']}.png",
            }
    categories = {
        "characters": "Graphics/Characters",
        "items": "Graphics/Items",
        "trainers": "Graphics/Trainers",
        "pictures": "Graphics/Pictures",
        "audio": "Audio",
    }
    if kind in categories:
        stem = f"game/{categories[kind]}/{identifier}"
        matches = [path for path, _ in copies(root) if str(Path(path).with_suffix("")) == stem]
        if len(matches) == 1:
            return {**record, "path": matches[0].removeprefix("game/")}
    raise ValueError(
        f"Unknown custom asset: {name}. Use its exact source filename without extension."
    )


def prepare(game, record):
    path = game / "Data/Scripts.rxdata"
    entries = loads(path.read_bytes())
    mains = [entry for entry in entries if entry[1] == "Main"]
    if len(mains) != 1:
        raise ValueError("Asset preview requires exactly one Main entry")
    driver = Path(__file__).with_suffix(".rb").read_bytes()
    driver += b'\nAssetPreview.run(load_data("Data/AssetPreview.rxdata"))\n'
    mains[0][2] = zlib.compress(driver)
    path.write_bytes(writes(entries))
    (game / "Data/AssetPreview.rxdata").write_bytes(writes(record))
