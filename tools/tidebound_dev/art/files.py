"""Conventional approved files and deliberate stock aliases; no map/content writes."""

from .export import Export

# Paths are relative to game/. Stock kit files remain inputs, never cleanup targets.
ALIASES = {
    "Graphics/Items/TIDEBOUNDPIE.png": "Graphics/Items/LAVACOOKIE.png",
    "Graphics/Items/TIDEBOUNDPLATE.png": "Graphics/Items/SHOALSHELL.png",
    "Graphics/Items/TIDEBOUNDNECKLACE.png": "Graphics/Items/PEARLSTRING.png",
    "Graphics/Items/TIDEBOUNDREEDCHARM.png": "Graphics/Items/SHOALSHELL.png",
}
for target, source in {
    "TBLOCALYOUTH": "YOUNGSTER",
    "TBLOCALYOUTH2": "CAMPER",
    "TBABYSSRUNNER": "BURGLAR",
}.items():
    ALIASES[f"Graphics/Trainers/{target}.png"] = f"Graphics/Trainers/{source}.png"
    ALIASES[f"Graphics/Characters/trainer_{target}.png"] = (
        f"Graphics/Characters/trainer_{source}.png"
    )

DIRECTORIES = {
    "characters": "Graphics/Characters",
    "trainers": "Graphics/Trainers",
    "items": "Graphics/Items",
    "pictures": "Graphics/Pictures",
    "audio": "Audio",
}


def exports(root):
    for directory, destination in DIRECTORIES.items():
        for source in sorted((root / "assets" / directory).rglob("*")):
            if not source.is_file() or source.name.startswith(".") or source.suffix == ".md":
                continue
            relative = source.relative_to(root / "assets" / directory)
            allowed = (".ogg", ".wav") if directory == "audio" else (".png",)
            if source.suffix not in allowed:
                raise ValueError(
                    f"{source}: expected {allowed}; keep working references in assets/references"
                )
            if directory == "audio" and (
                len(relative.parts) < 2 or relative.parts[0] not in ("BGM", "BGS", "ME", "SE")
            ):
                raise ValueError(f"{source}: audio requires a BGM, BGS, ME or SE category")
            yield Export(source, f"game/{destination}/{relative.as_posix()}")
    for target, source in ALIASES.items():
        yield Export(root / "game" / source, f"game/{target}")
