"""Export approved custom assets into Essentials' filename conventions."""

import shutil
from PIL import Image
from . import ownership, props, pokemon
from ..files import save_png
from .files import copies, validate_image, validate_audio


def build(root):
    owners = ownership.inventory(root)
    for destination, source in copies(root):
        if source.suffix.lower() == ".png":
            validate_image(source, destination)
        else:
            validate_audio(source)
        target = root / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".png":
            with Image.open(source) as image:
                save_png(image, target)
        else:
            shutil.copy2(source, target)
    for identifier, art in pokemon.POKEMON.items():
        for destination, image in pokemon.frames(root, identifier, art):
            path = root / "game" / destination
            path.parent.mkdir(parents=True, exist_ok=True)
            save_png(image, path)
        source = pokemon.cry_source(root, identifier, art)
        validate_audio(source)
        target = root / f"game/Audio/SE/Cries/{identifier}.ogg"
        if source != target:
            shutil.copy2(source, target)
    props.build(root)
    ownership.publish(root, owners)
