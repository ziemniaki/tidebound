"""Approved Pokémon bundles, with explicit stock, shiny and cry reuse."""

from .export import Export
from ..catalog import bundles


FRAMES = {"front": "Front", "back": "Back", "icon": "Icons"}


def exports(root):
    for identifier, record in bundles(root, "pokemon", "species.json").items():
        if not record.keys() <= {"species", "metrics", "art"}:
            raise ValueError(f"Pokémon {identifier}: expected species, metrics and art")
        art = record["art"]
        if not {"cry"} <= art.keys() <= {"cry", "stock", "shiny", "palette"}:
            raise ValueError(
                f"Pokémon {identifier}: art expects cry and optional stock/shiny/palette"
            )
        if art.get("stock") and any((root / "content/pokemon" / identifier).glob("*.png")):
            raise ValueError(f"Pokémon {identifier}: choose stock or local artwork")
        for name, folder in FRAMES.items():
            source = (
                root / f"game/Graphics/Pokemon/{folder}/{art['stock']}.png"
                if art.get("stock")
                else root / f"content/pokemon/{identifier}/{name}.png"
            )
            colors = art.get("palette", {}).get(folder)
            palette = {tuple(old): tuple(new) for old, new in colors} if colors else None
            yield Export(source, f"game/Graphics/Pokemon/{folder}/{identifier}.png", palette)
            if name == "icon":
                continue
            shiny = source
            if art.get("shiny", False):
                shiny = (
                    root / f"game/Graphics/Pokemon/{folder} shiny/{art['stock']}.png"
                    if art.get("stock")
                    else source.with_stem(f"{name}_shiny")
                )
            yield Export(
                shiny,
                f"game/Graphics/Pokemon/{folder} shiny/{identifier}.png",
                palette=None if art.get("shiny", False) else palette,
                matching_canvas=source if art.get("shiny", False) else None,
            )
        cry = (
            root / f"content/pokemon/{identifier}/cry.ogg"
            if art["cry"] == identifier
            else root / f"game/Audio/SE/Cries/{art['cry']}.ogg"
        )
        yield Export(cry, f"game/Audio/SE/Cries/{identifier}.ogg")
