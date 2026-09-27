"""Select an asset and replace Main only in a disposable development player."""

import zlib
from pathlib import Path

from rubymarshal.reader import loads
from rubymarshal.writer import writes

from . import props
from .files import DIRECTORIES, exports
from .pokemon import POKEMON


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
        records = props.load(root)
        if identifier in records:
            return {
                **record,
                **records[identifier],
                "path": f"Graphics/Pictures/{records[identifier]['file']}.png",
            }
    if kind in DIRECTORIES:
        stem = f"game/{DIRECTORIES[kind]}/{identifier}"
        matches = [
            export.destination
            for export in exports(root)
            if Path(export.destination).with_suffix("").as_posix() == stem
        ]
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
