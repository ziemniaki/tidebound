"""Conventional approved files and deliberate stock aliases; no map/content writes."""

from PIL import Image

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


def copies(root):
    for directory, destination in DIRECTORIES.items():
        for source in sorted((root / "assets" / directory).rglob("*")):
            if source.is_file() and source.suffix.lower() in (".png", ".ogg", ".wav"):
                yield (
                    f"game/{destination}/{source.relative_to(root / 'assets' / directory).as_posix()}",
                    source,
                )
    for target, source in ALIASES.items():
        yield f"game/{target}", root / "game" / source


def validate_image(path, destination):
    with Image.open(path) as image:
        image.load()
        if "/Characters/" in destination and (image.width % 4 or image.height % 4):
            raise ValueError(f"{path}: XP characters require a four-column, four-row sheet")
        if not image.convert("RGBA").getchannel("A").getbbox():
            raise ValueError(f"{path}: empty artwork")
