"""Export approved custom assets into Essentials' filename conventions."""

import shutil
from ..files import save_png
from .pokemon import POKEMON, frames
from .files import copies, validate_image


def build(root):
    for destination, source in copies(root):
        if source.suffix.lower() == ".png":
            validate_image(source, destination)
        target = root / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".png":
            from PIL import Image

            with Image.open(source) as image:
                save_png(image, target)
        else:
            shutil.copy2(source, target)
    for identifier, art in POKEMON.items():
        for destination, image in frames(root, identifier, art):
            path = root / "game" / destination
            path.parent.mkdir(parents=True, exist_ok=True)
            save_png(image, path)
        source = root / f"game/Audio/SE/Cries/{art.cry}.ogg"
        target = root / f"game/Audio/SE/Cries/{identifier}.ogg"
        if source != target:
            shutil.copy2(source, target)
