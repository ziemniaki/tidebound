"""Compile regional definitions into Essentials data and PBS in one pass."""

from collections import defaultdict
import shutil

from rubymarshal.classes import Symbol as S
from rubymarshal.reader import loads
from rubymarshal.writer import writes

from .species import SPECIES, METRICS, CRIES
from ..art import frostcoon, snakes, whyduck

STATS = ("HP", "ATTACK", "DEFENSE", "SPEED", "SPECIAL_ATTACK", "SPECIAL_DEFENSE")
# Each field has one native representation. The PBS writer uses the original value.
TEXT = {
    "Name": "real_name",
    "FormName": "real_form_name",
    "Category": "real_category",
    "Pokedex": "real_pokedex_entry",
}
NUMBERS = {
    "BaseExp": "base_exp",
    "CatchRate": "catch_rate",
    "Happiness": "happiness",
    "HatchSteps": "hatch_steps",
    "Generation": "generation",
    "FrontSpriteAltitude": "front_sprite_altitude",
    "ShadowX": "shadow_x",
    "ShadowSize": "shadow_size",
}
SYMBOLS = {
    "GenderRatio": "gender_ratio",
    "GrowthRate": "growth_rate",
    "Color": "color",
    "Shape": "shape",
    "Habitat": "habitat",
}
SYMBOL_LISTS = {
    "Types": "types",
    "Abilities": "abilities",
    "HiddenAbilities": "hidden_abilities",
    "TutorMoves": "tutor_moves",
    "EggMoves": "egg_moves",
    "EggGroups": "egg_groups",
    "WildItemCommon": "wild_item_common",
    "WildItemUncommon": "wild_item_uncommon",
    "WildItemRare": "wild_item_rare",
}


def native_field(name, value):
    if name in TEXT or name in NUMBERS:
        return "@" + (TEXT | NUMBERS)[name], value
    if name in SYMBOLS:
        return "@" + SYMBOLS[name], S(value)
    if name in SYMBOL_LISTS:
        return "@" + SYMBOL_LISTS[name], [S(item) for item in value]
    if name == "BaseStats":
        if len(value) != len(STATS) or any(stat <= 0 for stat in value):
            raise ValueError("BaseStats requires six positive values")
        return "@base_stats", {S(stat): number for stat, number in zip(STATS, value)}
    if name == "EVs":
        values = dict(value)
        if values.keys() - set(STATS):
            raise ValueError("Unknown EV stat")
        return "@evs", {S(stat): values.get(stat, 0) for stat in STATS}
    if name == "Moves":
        return "@moves", [[level, S(move)] for level, move in value]
    if name == "Evolutions":
        return "@evolutions", [
            [S(target), S(method), parameter, False] for target, method, parameter in value
        ]
    if name in ("Height", "Weight"):
        return "@" + name.lower(), round(value * 10)
    if name == "Flags":
        return "@flags", list(value)
    if name in ("FrontSprite", "BackSprite"):
        return "@front_sprite" if name == "FrontSprite" else "@back_sprite", list(value)
    raise ValueError("Unsupported species field: " + name)


def identity(identifier):
    name, separator, form = identifier.partition("_")
    return (name, int(form)) if separator else (name, 0)


def compile_records(database, definitions, metrics=False):
    """Resolve explicit templates topologically, independent of definition order."""
    pending = dict(definitions)
    resolved = set(database) - {S(name) for name in definitions}
    while pending:
        ready = [
            name for name, definition in pending.items() if S(definition["inherit"]) in resolved
        ]
        if not ready:
            raise ValueError("Missing or cyclic species template: " + ", ".join(pending))
        for identifier in ready:
            definition = pending.pop(identifier)
            record = loads(writes(database[S(definition["inherit"])]))
            name, form = identity(identifier)
            attrs = record.attributes
            attrs.update({"@id": S(identifier), "@species": S(name), "@form": form})
            prefix = "pokemon_metrics_" if metrics else "pokemon_forms_" if form else "pokemon_"
            attrs["@pbs_file_suffix"] = definition["file"].removeprefix(prefix)
            if not metrics:
                attrs["@pokedex_form"] = form
                if not form:
                    attrs["@evolutions"] = []
                    attrs["@real_form_name"] = None
            for field, value in definition["fields"].items():
                attribute, converted = native_field(field, value)
                attrs[attribute] = converted
            database[S(identifier)] = record
            resolved.add(S(identifier))
    if not metrics:
        # Only custom targets need backlinks; ordinary species remain untouched.
        for identifier, definition in definitions.items():
            source, form = identity(identifier)
            for target, method, parameter in definition["fields"].get("Evolutions", ()):
                target_id = (
                    f"{target}_{form}" if form and f"{target}_{form}" in definitions else target
                )
                if target_id not in definitions:
                    if S(target) not in database:
                        raise ValueError("Unknown evolution target: " + target)
                    continue
                reverse = [S(source), S(method), parameter, True]
                evolutions = database[S(target_id)].attributes["@evolutions"]
                if reverse not in evolutions:
                    evolutions.append(reverse)
    return database


def validate_species(species, moves, abilities):
    for identifier in SPECIES:
        attrs = species[S(identifier)].attributes
        learnset = (
            [move for _, move in attrs["@moves"]] + attrs["@tutor_moves"] + attrs["@egg_moves"]
        )
        for move in learnset:
            if move not in moves:
                raise ValueError(f"{identifier}: unknown move {move}")
        for ability in attrs["@abilities"] + attrs["@hidden_abilities"]:
            if ability not in abilities:
                raise ValueError(f"{identifier}: unknown ability {ability}")
        if identifier == "FROSTCOON" and any(
            moves[move].attributes["@category"] != 2 for move in learnset
        ):
            raise ValueError("Frostcoon must have only support moves")
        if identifier in ("EKANS_1", "ARBOK_1") and any(
            moves[move].attributes["@type"] == S("POISON") for move in learnset
        ):
            raise ValueError("Regional snakes must not learn Poison moves")


def pbs_value(value):
    if isinstance(value, (tuple, list)):
        return ",".join(pbs_value(item) for item in value)
    return str(value)


def pbs_files(definitions):
    sections = defaultdict(list)
    for identifier, definition in definitions.items():
        name, form = identity(identifier)
        heading = f"{name},{form}" if form else name
        lines = [f"[{heading}]"]
        lines.extend(
            f"{key} = {pbs_value(value)}"
            for key, value in definition["fields"].items()
            if value != ()
        )
        sections[definition["file"]].append("\n".join(lines))
    return {
        name + ".txt": "# Generated from tidebound_dev.content species definitions.\n"
        + "\n\n".join(parts)
        + "\n"
        for name, parts in sections.items()
    }


def export_art(root):
    game = root / "game"
    for target, source in CRIES.items():
        shutil.copy2(game / f"Audio/SE/Cries/{source}.ogg", game / f"Audio/SE/Cries/{target}.ogg")
    for folder in ("Front", "Back", "Front shiny", "Back shiny", "Icons"):
        sprites = game / "Graphics/Pokemon" / folder
        shutil.copy2(sprites / "FROSTCOON_EVOLUTION.png", sprites / "NIVALORA.png")
        shutil.copy2(sprites / "PSYDUCK.png", sprites / "PSYDUCK_1.png")
    frostcoon.generate(game)
    snakes.generate(game)
    whyduck.generate(game, root / "assets/Whyduck/pieces")


def build(root):
    game = root / "game"
    species = loads((game / "Data/species.dat").read_bytes())
    metrics = loads((game / "Data/species_metrics.dat").read_bytes())
    moves = loads((game / "Data/moves.dat").read_bytes())
    abilities = loads((game / "Data/abilities.dat").read_bytes())
    compile_records(species, SPECIES)
    compile_records(metrics, METRICS, metrics=True)
    validate_species(species, moves, abilities)
    # Construct both encodings before publishing either database.
    species_bytes, metric_bytes = writes(species), writes(metrics)
    texts = pbs_files(SPECIES) | pbs_files(METRICS)
    (game / "Data/species.dat").write_bytes(species_bytes)
    (game / "Data/species_metrics.dat").write_bytes(metric_bytes)
    for name, text in texts.items():
        (game / "PBS" / name).write_text(text, encoding="utf-8-sig")
    export_art(root)
    print(f"Built {len(SPECIES)} regional species/forms and {len(METRICS)} sprite metrics")
