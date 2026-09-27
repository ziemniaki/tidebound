"""A bounded inventory of custom exports. Stock engine assets are never outputs."""

import json
from pathlib import PurePosixPath
from . import pokemon
from .files import copies

MANIFEST = "tools/generated/assets.json"
MAP_OUTPUTS = (
    "Graphics/Tilesets/TideboundLandscape.png",
    "Graphics/Tilesets/TideboundLighthouse.png",
    "Graphics/Tilesets/TideboundPond.png",
    "Graphics/Tilesets/TideboundVillage.png",
    "Graphics/Autotiles/Tidebound Shallows.png",
    "Graphics/Autotiles/Tidebound Open Sea.png",
    "Graphics/Autotiles/Tidebound Deep Sea.png",
    "Graphics/Pictures/Tidebound/window_panes.png",
)


def inventory(root):
    for directory in (root / "assets/pokemon").glob("*"):
        if directory.is_dir() and directory.name not in pokemon.POKEMON:
            raise ValueError(f"Unregistered Pokémon source: {directory.name}")
    owners = {}
    folded = set()

    def register(name, owner):
        if name.casefold() in folded:
            raise ValueError(f"Duplicate asset output: {name}")
        folded.add(name.casefold())
        owners[name] = owner

    for name in pokemon.outputs():
        register(name, "pokemon")
    for name, _ in copies(root):
        register(name, "files")
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
    sources = [source for _, source in copies(root)]
    for identifier, art in pokemon.POKEMON.items():
        sources.append(pokemon.cry_source(root, identifier, art))
        if art.stock:
            folders = (
                (*pokemon.FRAMES.values(), "Front shiny", "Back shiny")
                if art.shiny
                else pokemon.FRAMES.values()
            )
            sources.extend(
                root / f"game/Graphics/Pokemon/{folder}/{art.stock}.png" for folder in folders
            )
    for source in sources:
        if source.relative_to(root).as_posix() in owners.keys() | previous.keys():
            raise ValueError(f"Asset source is also a generated output: {source}")
        if not source.is_file():
            raise ValueError(f"Missing asset source: {source}")
    return dict(sorted(owners.items()))


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


def publish(root, owners):
    # Removed declarations must not leave obsolete images in player packages.
    for name in recorded(root).keys() - owners.keys():
        (root / name).unlink(missing_ok=True)
    path = root / MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(owners, indent=2) + "\n")


def validate(root):
    expected = inventory(root)
    if recorded(root) != expected:
        raise ValueError("Asset ownership changed; run uv run rebuild --all and stage the outputs")
    missing = [name for name in expected if not (root / name).is_file()]
    if missing:
        raise ValueError("Missing generated assets:\n" + "\n".join(missing))
