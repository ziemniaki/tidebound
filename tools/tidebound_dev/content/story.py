"""Compile story Key Items and trainer classes; battle rosters live in Ruby features."""

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
from ..files import ruby
from ..maps.lighting import light


def clone(value):
    return loads(writes(value))


def item_section(ident, name, description, field_use=0):
    use = "FieldUse = Direct\n" if field_use == 2 else ""
    return (
        f"\n#-------------------------------\n[{ident}]\nName = {name}\nNamePlural = {name}\n"
        f"{use}Pocket = 8\nPrice = 0\nFlags = KeyItem\nConsumable = false\nDescription = {description}\n"
    )


from ..catalog import ITEMS, TRAINERS


def build_items(game):
    items = loads((game / "Data/items.dat").read_bytes())
    text = "# Generated story Key Items.\n"
    lights = {}
    for ident, record in ITEMS.items():
        name, description = record["name"], record["description"]
        field_use = 2 if "light" in record else 0
        if "light" in record:
            light(record["light"])
            lights[ident] = record["light"]
        data = clone(items[Symbol("TOWNMAP")])
        data.attributes.update(
            {
                "@id": Symbol(ident),
                "@real_name": name,
                "@real_name_plural": name,
                "@real_portion_name": "" if ident == "TIDEBOUNDOILKEYS" else name,
                "@real_portion_name_plural": "" if ident == "TIDEBOUNDOILKEYS" else name,
                "@pocket": 8,
                "@price": 0,
                "@sell_price": 0,
                "@field_use": field_use,
                "@battle_use": 0,
                "@flags": ["KeyItem"],
                "@consumable": False,
                "@real_description": description,
                "@pbs_file_suffix": "tidebound_story",
            }
        )
        items[Symbol(ident)] = data
        text += item_section(ident, name, description, field_use)
    (game / "PBS/items_tidebound_story.txt").write_text(text, encoding="utf-8-sig")
    (game / "Data/items.dat").write_bytes(writes(items))
    (game.parent / "src/generated/item_lights.rb").write_text(
        "module Tidebound::Lighting\n  ITEM_LIGHTS = " + ruby(lights) + ".freeze\nend\n"
    )


def build_trainers(game):
    types = loads((game / "Data/trainer_types.dat").read_bytes())
    text = "# Temporary stock art; no final Team Abyss uniform is established.\n"
    for ident, record in TRAINERS.items():
        name, base = record["name"], record.get("stock", "YOUNGSTER")
        data = clone(types[Symbol(base)])
        data.attributes.update(
            {
                "@id": Symbol(ident),
                "@real_name": name,
                "@base_money": 0,
                "@skill_level": 0,
                "@intro_BGM": None,
                "@battle_BGM": "stillness",
                "@victory_BGM": "stillness",
                "@pbs_file_suffix": "tidebound_story",
            }
        )
        types[Symbol(ident)] = data
        gender = ("Male", "Female", "Unknown")[data.attributes["@gender"]]
        text += f"\n#-------------------------------\n[{ident}]\nName = {name}\nGender = {gender}\nBaseMoney = 0\nSkillLevel = 0\nBattleBGM = stillness\nVictoryBGM = stillness\n"
    (game / "PBS/trainer_types_tidebound_story.txt").write_text(text, encoding="utf-8-sig")
    (game / "Data/trainer_types.dat").write_bytes(writes(types))


def build(root):
    build_items(root / "game")
    build_trainers(root / "game")
    print(f"Built {len(ITEMS)} story items and {len(TRAINERS)} trainer classes.")
