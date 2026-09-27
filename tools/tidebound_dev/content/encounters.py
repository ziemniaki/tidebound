"""Map-owned encounter tables and one derived regional-form hook."""

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import RubyObject, Symbol
from ..maps.definitions import DEFINITIONS
from ..files import ruby
from .species_compiler import identity


def build(root):
    game = root / "game"
    encounters = loads((game / "Data/encounters.dat").read_bytes())
    species = loads((game / "Data/species.dat").read_bytes())
    text = "# Generated from map encounter declarations.\n"
    forms = {}
    for name, area in DEFINITIONS.items():
        selected = dict(area.wild_forms)
        chances, types = {}, {}
        if area.encounters:
            text += f"#-------------------------------\n[{area.id}]\n"
        for kind, table in area.encounters.items():
            chance, slots = table["chance"], table["slots"]
            if type(chance) is not int or not 1 <= chance <= 100 or not slots:
                raise ValueError(f"{name}/{kind}: expected chance 1..100 and nonempty slots")
            native = []
            text += f"{kind},{chance}\n"
            for weight, identifier, low, high in slots:
                if Symbol(identifier) not in species:
                    raise ValueError(f"{name}/{kind}: unknown species/form {identifier}")
                if (
                    any(type(v) is not int for v in (weight, low, high))
                    or weight <= 0
                    or not 1 <= low <= high <= 100
                ):
                    raise ValueError(f"{name}/{kind}/{identifier}: invalid weight or levels")
                base, form = identity(identifier)
                if base in selected and selected[base] != form:
                    raise ValueError(f"{name}: conflicting wild forms for {base}")
                selected[base] = form
                native.append([weight, Symbol(base), low, high])
                text += f"    {weight},{base},{low},{high}\n"
            chances[Symbol(kind)] = chance
            types[Symbol(kind)] = native
        for base, form in selected.items():
            identifier = f"{base}_{form}" if form else base
            if Symbol(identifier) not in species:
                raise ValueError(f"{name}: unknown wild form {identifier}")
        forms[area.id] = {base: form for base, form in selected.items() if form}
        if not types:
            continue
        key = Symbol(f"{area.id}_0")
        encounters[key] = RubyObject(
            "GameData::Encounter",
            {
                "@id": key,
                "@map": area.id,
                "@version": 0,
                "@step_chances": chances,
                "@types": types,
                "@pbs_file_suffix": "tidebound",
            },
        )
    (game / "Data/encounters.dat").write_bytes(writes(encounters))
    (game / "PBS/encounters_tidebound.txt").write_text(text)
    lines = [
        "# Generated from map encounters and wild_forms.",
        "module Tidebound",
        "  WILD_FORMS = {",
    ]
    lines.extend(f"    {mid} => {ruby(rows)}," for mid, rows in forms.items() if rows)
    lines += ["  }.freeze", "end", ""]
    (root / "src/generated/wild_forms.rb").write_text("\n".join(lines))
