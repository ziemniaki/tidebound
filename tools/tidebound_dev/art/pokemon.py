"""Approved Pokémon bundles, with explicit stock, shiny and cry reuse."""

from dataclasses import dataclass
from PIL import Image

from .recolors import RECOLORS, recolor


@dataclass(frozen=True)
class PokemonArt:
    cry: str
    shiny: bool = False  # True requires separate approved front/back PNGs.
    stock: str | None = None


POKEMON = {
    "SUNKERN_1": PokemonArt("SUNKERN"),
    "MOONKERN": PokemonArt("SUNKERN"),
    "MOONFLORA": PokemonArt("SUNFLORA"),
    "GLACIVERM": PokemonArt("WURMPLE"),
    "WURMPLE_1": PokemonArt("WURMPLE", stock="WURMPLE"),
    "FROSTCOON": PokemonArt("SILCOON", stock="SILCOON"),
    "NIVALORA": PokemonArt("ARTICUNO"),
    "LAPRAS_1": PokemonArt("LAPRAS"),
    "WHYDUCK": PokemonArt("PSYDUCK", shiny=True),
    "PSYDUCK_1": PokemonArt("PSYDUCK", stock="PSYDUCK", shiny=True),
    "EKANS_1": PokemonArt("EKANS", stock="EKANS"),
    "ARBOK_1": PokemonArt("ARBOK", stock="ARBOK"),
}
FRAMES = {"front": "Front", "back": "Back", "icon": "Icons"}


def frames(root, identifier, art):
    """Yield the engine destination and image; no resizing or alpha compositing."""
    for name, folder in FRAMES.items():
        if art.stock:
            source = root / f"game/Graphics/Pokemon/{folder}/{art.stock}.png"
        else:
            source = root / f"assets/pokemon/{identifier}/{name}.png"
        if identifier in RECOLORS:
            stock, palettes = RECOLORS[identifier]
            if art.stock != stock:
                raise ValueError(f"{identifier}: recolor source disagrees with stock source")
            frame = recolor(source, palettes[folder])
        else:
            with Image.open(source) as image:
                frame = image.convert("RGBA")
        validate_frame(source, frame, name)
        yield f"Graphics/Pokemon/{folder}/{identifier}.png", frame
        if name == "icon":
            continue
        if art.shiny:
            source = (
                root / f"game/Graphics/Pokemon/{folder} shiny/{art.stock}.png"
                if art.stock
                else root / f"assets/pokemon/{identifier}/{name}_shiny.png"
            )
            with Image.open(source) as image:
                shiny = image.convert("RGBA")
            if shiny.size != frame.size:
                raise ValueError(f"{source}: shiny canvas must match normal canvas {frame.size}")
        else:
            shiny = frame
        yield f"Graphics/Pokemon/{folder} shiny/{identifier}.png", shiny


def validate_frame(path, image, name):
    width, height = image.size
    if name == "icon" and (width < height or width % height):
        raise ValueError(f"{path}: icon must be a horizontal strip of square frames")
    if not image.getchannel("A").getbbox():
        raise ValueError(f"{path}: empty artwork")


def outputs():
    for identifier in POKEMON:
        for folder in (*FRAMES.values(), "Front shiny", "Back shiny"):
            yield f"game/Graphics/Pokemon/{folder}/{identifier}.png"
        yield f"game/Audio/SE/Cries/{identifier}.ogg"
