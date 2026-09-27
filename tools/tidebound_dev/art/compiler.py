"""Export approved custom assets into Essentials' filename conventions."""

import shutil
from ..files import save_png
from .pokemon import POKEMON, frames


def build(root):
    for identifier, art in POKEMON.items():
        for destination, image in frames(root, identifier, art):
            path = root / "game" / destination
            path.parent.mkdir(parents=True, exist_ok=True)
            save_png(image, path)
        source = root / f"game/Audio/SE/Cries/{art.cry}.ogg"
        target = root / f"game/Audio/SE/Cries/{identifier}.ogg"
        if source != target:
            shutil.copy2(source, target)
