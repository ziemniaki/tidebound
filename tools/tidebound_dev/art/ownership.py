"""A bounded inventory of custom exports. Stock engine assets are never outputs."""

import json
from pathlib import PurePosixPath

from . import files, pokemon
from ..maps import tilesets

MANIFEST = "game/.generated/assets.json"
MAP_OUTPUTS = ("Graphics/Pictures/Tidebound/window_panes.png",)


def inventory(root):
    exports = []
    owners = {}
    folded = set()

    def register(name, owner):
        if name.casefold() in folded:
            raise ValueError(f"Duplicate asset output: {name}")
        folded.add(name.casefold())
        owners[name] = owner

    for owner, producer in (
        ("files", files.exports),
        ("pokemon", pokemon.exports),
        ("tilesets", tilesets.exports),
    ):
        for export in producer(root):
            register(export.destination, owner)
            exports.append(export)
    for name in MAP_OUTPUTS:
        register(f"game/{name}", "maps")
    register("src/generated/prop_assets.rb", "props")
    register("src/generated/window_lights.rb", "maps")
    previous = recorded(root)
    audio_stems = set()
    for name in owners:
        if not name.startswith("game/Audio/"):
            continue
        stem = str(PurePosixPath(name).with_suffix("")).casefold()
        if stem in audio_stems:
            raise ValueError(f"Ambiguous audio extensions: {name}")
        audio_stems.add(stem)
        for other in (root / name).parent.glob("*"):
            relative = other.relative_to(root).as_posix()
            if (
                other.stem.casefold() == PurePosixPath(name).stem.casefold()
                and relative != name
                and relative not in previous
            ):
                raise ValueError(f"Audio shadows an existing asset: {name} / {relative}")
    # Recipes must read stock/source art, never last build's custom output.
    sources = {export.source for export in exports}
    sources.update(export.matching_canvas for export in exports if export.matching_canvas)
    generated = {name.casefold() for name in owners.keys() | previous.keys()}
    for source in sources:
        if source.relative_to(root).as_posix().casefold() in generated:
            raise ValueError(f"Asset source is also a generated output: {source}")
        if not source.is_file():
            raise ValueError(f"Missing asset source: {source}")
    previous_names = {name.casefold() for name in previous}
    for name in owners:
        if name.casefold() not in previous_names and (root / name).exists():
            raise ValueError(f"Custom asset would overwrite an unowned file: {name}")
    return dict(sorted(owners.items())), exports


def recorded(root):
    path = root / MANIFEST
    if not path.exists():
        return {}
    entries = json.loads(path.read_text())
    for name in entries:
        path = PurePosixPath(name)
        if (
            ".." in path.parts
            or "\\" in name
            or path.parts[:2] not in (("game", "Graphics"), ("game", "Audio"), ("src", "generated"))
        ):
            raise ValueError(f"Invalid generated asset path: {name}")
    return entries


def remove_retired(root, owners):
    # Remove before export: a case-only rename aliases the new file on macOS/Windows.
    for name in recorded(root).keys() - owners.keys():
        (root / name).unlink(missing_ok=True)


def publish(root, owners):
    path = root / MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(owners, indent=2) + "\n")


def validate(root):
    expected, _ = inventory(root)
    if recorded(root) != expected:
        raise ValueError("Asset ownership changed; run uv run rebuild --all and stage the outputs")
    missing = [name for name in expected if not (root / name).is_file()]
    if missing:
        raise ValueError("Missing generated assets:\n" + "\n".join(missing))
