"""Update generated launch/metadata defaults during an explicit full rebuild."""

from ..maps import definitions
import json
from rubymarshal.reader import loads
from rubymarshal.writer import writes


def build(root):
    DEV = root / "tools"
    GAME = DEV.parent / "game"
    # Read required generator output before changing editor metadata.
    manifest = json.loads((DEV / "generated/map_manifest.json").read_text())
    # Standalone title and a separate save directory avoid Essentials demo saves.
    p = GAME / "Game.ini"
    s = p.read_text()
    s = s.replace("Title=Pokemon Essentials v21.1", "Title=Tidebound Opening")
    p.write_text(s)
    p = GAME / "mkxp.json"
    s = p.read_text()
    s = s.replace(
        '"windowTitle": "Pokémon Essentials v21.1"',
        '"windowTitle": "Tidebound - The Keeper\'s Light"',
    )
    s = s.replace(
        '// "dataPathApp": "Pokemon Essentials v21",', '"dataPathApp": "Tidebound_Opening_0_2",'
    )
    p.write_text(s)
    md = loads((GAME / "Data/metadata.dat").read_bytes())
    md[0].attributes.update(
        {
            "@start_money": 0,
            "@start_item_storage": [],
            "@home": [101, 6, 10, 2],
            "@wild_battle_BGM": "Tidebound Stillness",
            "@wild_victory_BGM": "Tidebound Stillness",
            "@trainer_battle_BGM": "Tidebound Stillness",
            "@trainer_victory_BGM": "Tidebound Stillness",
        }
    )
    (GAME / "Data/metadata.dat").write_bytes(writes(md))
    # Maintain PBS alongside compiled data, so editor recompilation keeps new maps.
    p = GAME / "PBS/metadata.txt"
    s = p.read_text(encoding="utf-8-sig")
    s = s.replace("StartMoney = 3000", "StartMoney = 0")
    s = s.replace("StartItemStorage = POTION", "StartItemStorage = ")
    s = s.replace("Home = 3,7,5,8", "Home = 101,6,10,2")
    for kind in ["WildBattleBGM", "WildVictoryBGM", "TrainerBattleBGM", "TrainerVictoryBGM"]:
        import re

        s = re.sub(r"^" + kind + r"\s*=.*$", kind + " = Tidebound Stillness", s, flags=re.M)
    p.write_text(s, encoding="utf-8-sig")
    p = GAME / "PBS/map_metadata.txt"
    s = p.read_text(encoding="utf-8-sig")
    s = s.split("# TIDEBOUND OPENING MAPS")[0].rstrip() + "\n\n# TIDEBOUND OPENING MAPS\n"
    for m in manifest:
        s += f"#-------------------------------\n[{m['id']}]\n"
        for key, value in definitions.BY_ID[m["id"]].pbs_metadata(m["name"]).items():
            value = str(value).lower() if isinstance(value, bool) else value
            s += f"{key} = {value}\n"
    p.write_text(s, encoding="utf-8-sig")
    print("Updated generated launch configuration and game metadata.")
