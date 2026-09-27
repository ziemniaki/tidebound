"""Species and sprite metrics come from the same authored Pokémon bundles."""

from ..catalog import POKEMON

SPECIES = {
    identifier: {
        **record["species"],
        "file": "pokemon_forms_tidebound" if "_" in identifier else "pokemon_tidebound",
    }
    for identifier, record in POKEMON.items()
}
METRICS = {
    identifier: {**record["metrics"], "file": "pokemon_metrics_tidebound"}
    for identifier, record in POKEMON.items()
    if "metrics" in record
}
