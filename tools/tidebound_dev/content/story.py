"""Compile story Key Items and trainer classes; battle rosters live in Ruby features."""

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol


def clone(value):
    return loads(writes(value))


def item_section(ident, name, description):
    return (
        f"\n#-------------------------------\n[{ident}]\nName = {name}\nNamePlural = {name}\n"
        f"Pocket = 8\nPrice = 0\nFlags = KeyItem\nConsumable = false\nDescription = {description}\n"
    )


def build_items(game):
    items = loads((game / "Data/items.dat").read_bytes())
    key = clone(items[Symbol("TOWNMAP")])
    key.attributes.update(
        {
            "@id": Symbol("TIDEBOUNDOILKEYS"),
            "@real_name": "Oil-Shop Keys",
            "@real_name_plural": "Oil-Shop Keys",
            "@real_portion_name": "",
            "@real_portion_name_plural": "",
            "@pocket": 8,
            "@price": 0,
            "@sell_price": 0,
            "@field_use": 0,
            "@battle_use": 0,
            "@flags": ["KeyItem"],
            "@consumable": False,
            "@real_description": "Old brass keys found beneath white flowers. The oil seller in Shiohama is looking for them.",
        }
    )
    items[Symbol("TIDEBOUNDOILKEYS")] = key

    path = game / "PBS/items.txt"
    stock = path.read_text(encoding="utf-8-sig").split("# TIDEBOUND OPENING ITEMS")[0].rstrip()
    path.write_text(
        stock
        + "\n\n# TIDEBOUND OPENING ITEMS"
        + item_section(
            "TIDEBOUNDOILKEYS", key.attributes["@real_name"], key.attributes["@real_description"]
        ),
        encoding="utf-8-sig",
    )
    text = "# Tidebound story items, never healing supplies.\n"
    rows = [
        (
            "TIDEBOUNDPIE",
            "Homemade Pie",
            "A homemade pie on a ceramic plate painted with two blue reeds. A thank-you for you and Mother.",
        ),
        (
            "TIDEBOUNDPLATE",
            "Blue-Reed Plate",
            "An ordinary ceramic plate, washed and dried. Two blue reeds decorate its rim. Return it to the oil seller.",
        ),
        (
            "TIDEBOUNDNECKLACE",
            "Pearl Necklace",
            "A small pearl necklace recovered from the thieves. The oil seller is waiting for it.",
        ),
        (
            "TIDEBOUNDREEDCHARM",
            "Blue-Reed Keepsake",
            "A small ceramic charm painted with two blue reeds. A gift from the oil seller, to keep.",
        ),
    ]
    for ident, name, desc in rows:
        data = clone(items[Symbol("TIDEBOUNDOILKEYS")])
        data.attributes.update(
            {
                "@id": Symbol(ident),
                "@real_name": name,
                "@real_name_plural": name,
                "@real_portion_name": name,
                "@real_portion_name_plural": name,
                "@real_description": desc,
                "@pbs_file_suffix": "tidebound_neighbor",
            }
        )
        items[Symbol(ident)] = data
        text += item_section(ident, name, desc)
    (game / "PBS/items_tidebound_neighbor.txt").write_text(text, encoding="utf-8-sig")
    (game / "Data/items.dat").write_bytes(writes(items))


def build_trainers(game):
    types = loads((game / "Data/trainer_types.dat").read_bytes())
    text = "# Temporary stock art; no final Team Abyss uniform is established.\n"
    for ident, name, base in [
        ("TBLOCALYOUTH", "Local Thief", "YOUNGSTER"),
        ("TBLOCALYOUTH2", "Local Thief", "CAMPER"),
        ("TBABYSSRUNNER", "Abyss Runner", "BURGLAR"),
    ]:
        data = clone(types[Symbol(base)])
        data.attributes.update(
            {
                "@id": Symbol(ident),
                "@real_name": name,
                "@base_money": 0,
                "@skill_level": 0,
                "@intro_BGM": None,
                "@battle_BGM": "Tidebound Stillness",
                "@victory_BGM": "Tidebound Stillness",
                "@pbs_file_suffix": "tidebound_neighbor",
            }
        )
        types[Symbol(ident)] = data
        text += f"\n#-------------------------------\n[{ident}]\nName = {name}\nGender = Male\nBaseMoney = 0\nSkillLevel = 0\nBattleBGM = Tidebound Stillness\nVictoryBGM = Tidebound Stillness\n"
    (game / "PBS/trainer_types_tidebound_neighbor.txt").write_text(text, encoding="utf-8-sig")
    (game / "Data/trainer_types.dat").write_bytes(writes(types))


def build(root):
    build_items(root / "game")
    build_trainers(root / "game")
    print("Built five story Key Items and three trainer classes.")
