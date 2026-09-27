"""Inventory consumed by disposable native checks, derived from authored content."""

from .species import SPECIES, METRICS
from .species_compiler import identity

from ..art.pokemon import POKEMON


def inventory():
    # Include each form's base so compiler-added family relationships are checked.
    species = sorted(set(SPECIES) | {identity(name)[0] for name in SPECIES})
    if SPECIES.keys() != POKEMON.keys():
        raise ValueError(f"Species/art ownership mismatch: {SPECIES.keys() ^ POKEMON.keys()}")
    art = []
    for identifier in SPECIES:
        name, form = identity(identifier)
        art.append(
            {
                "id": identifier,
                "species": name,
                "form": form,
                "front": f"Graphics/Pokemon/Front/{identifier}.png",
                "back": f"Graphics/Pokemon/Back/{identifier}.png",
                "front_shiny": f"Graphics/Pokemon/Front shiny/{identifier}.png",
                "back_shiny": f"Graphics/Pokemon/Back shiny/{identifier}.png",
                # The current art direction shares normal and shiny party icons.
                "icon": f"Graphics/Pokemon/Icons/{identifier}.png",
                "icon_shiny": f"Graphics/Pokemon/Icons/{identifier}.png",
                "cry": f"Cries/{identifier}",
            }
        )
    return {"species": species, "metrics": sorted(METRICS), "art": art}
