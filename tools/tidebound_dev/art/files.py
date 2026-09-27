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
            yield f"game/{destination}/{relative.as_posix()}", source
    for target, source in ALIASES.items():
        yield f"game/{target}", root / "game" / source


def validate_image(path, destination):
    with Image.open(path) as image:
        image.load()
        if "/Characters/" in destination and (image.width % 4 or image.height % 4):
            raise ValueError(f"{path}: XP characters require a four-column, four-row sheet")
        if not image.convert("RGBA").getchannel("A").getbbox():
            raise ValueError(f"{path}: empty artwork")


def validate_audio(path):
    """Check container/codec headers, not musical quality or native decoding."""
    if path.suffix == ".wav":
        import wave

        with wave.open(str(path), "rb") as audio:
            if audio.getnchannels() not in (1, 2) or not audio.getnframes():
                raise ValueError(f"{path}: expected nonempty mono/stereo PCM WAV")
        return
    with path.open("rb") as audio:
        header = audio.read(27)
        if len(header) != 27 or header[:5] != b"OggS\x00":
            raise ValueError(f"{path}: expected Ogg Vorbis, not a renamed file")
        audio.read(header[26])  # First page's lacing table.
        identification = audio.read(30)
        if (
            len(identification) != 30
            or identification[:7] != b"\x01vorbis"
            or identification[11] not in (1, 2)
        ):
            raise ValueError(f"{path}: expected mono/stereo Ogg Vorbis")
