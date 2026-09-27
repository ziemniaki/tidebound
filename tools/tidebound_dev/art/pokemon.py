"""Approved Pokémon bundles, with explicit stock, shiny and cry reuse."""

from dataclasses import dataclass

from .export import Export
from .recolors import RECOLORS


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


def exports(root):
    for directory in (root / "assets/pokemon").glob("*"):
        if directory.is_dir() and directory.name not in POKEMON:
            raise ValueError(f"Unregistered Pokémon source: {directory.name}")
    for identifier, art in POKEMON.items():
        for name, folder in FRAMES.items():
            source = (
                root / f"game/Graphics/Pokemon/{folder}/{art.stock}.png"
                if art.stock
                else root / f"assets/pokemon/{identifier}/{name}.png"
            )
            palette = RECOLORS[identifier][folder] if identifier in RECOLORS else None
            yield Export(source, f"game/Graphics/Pokemon/{folder}/{identifier}.png", palette)
            if name == "icon":
                continue
            shiny = source
            if art.shiny:
                shiny = (
                    root / f"game/Graphics/Pokemon/{folder} shiny/{art.stock}.png"
                    if art.stock
                    else source.with_stem(f"{name}_shiny")
                )
            yield Export(
                shiny,
                f"game/Graphics/Pokemon/{folder} shiny/{identifier}.png",
                palette=None if art.shiny else palette,
                matching_canvas=source if art.shiny else None,
            )
        cry = (
            root / f"assets/pokemon/{identifier}/cry.ogg"
            if art.cry == identifier
            else root / f"game/Audio/SE/Cries/{art.cry}.ogg"
        )
        yield Export(cry, f"game/Audio/SE/Cries/{identifier}.ogg")
