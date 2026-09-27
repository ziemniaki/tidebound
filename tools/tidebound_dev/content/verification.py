"""Inventory consumed by disposable native checks, derived from authored content."""

from .species import SPECIES, METRICS
from .species_compiler import identity

# Regional cries deliberately use their ordinary species. New base species must
# supply their own filename (CRIES exports may copy approved existing audio there).
CRY_REUSE = {
    "SUNKERN_1": "SUNKERN",
    "WURMPLE_1": "WURMPLE",
    "LAPRAS_1": "LAPRAS",
    "PSYDUCK_1": "PSYDUCK",
    "EKANS_1": "EKANS",
    "ARBOK_1": "ARBOK",
}


def inventory():
    # Include each form's base so compiler-added family relationships are checked.
    species = sorted(set(SPECIES) | {identity(name)[0] for name in SPECIES})
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
                "cry": f"Cries/{CRY_REUSE.get(identifier, identifier)}",
            }
        )
    return {"species": species, "metrics": sorted(METRICS), "art": art}
