"""Update generated launch/metadata defaults during rebuilding."""

from ..maps import definitions
import json
import re
from rubymarshal.reader import loads
from rubymarshal.writer import writes


def build(root):
    GAME = root / "game"
    by_id = {d.id: d for d in definitions.load(root).values()}
    # Read required generator output before changing editor metadata.
    manifest = json.loads((GAME / ".generated/map_manifest.json").read_text())
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
            "@wild_battle_BGM": "stillness",
            "@wild_victory_BGM": "stillness",
            "@trainer_battle_BGM": "stillness",
            "@trainer_victory_BGM": "stillness",
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
        s = re.sub(r"^" + kind + r"\s*=.*$", kind + " = stillness", s, flags=re.M)
    p.write_text(s, encoding="utf-8-sig")
    p = GAME / "PBS/map_metadata.txt"
    s = p.read_text(encoding="utf-8-sig")
    s = s.split("# TIDEBOUND OPENING MAPS")[0]
    # Adopting a native map also replaces its existing PBS section. Essentials
    # rejects duplicate IDs when it recompiles the editor project.
    s = re.sub(
        r"(?ms)^\[(\d+)\][^\n]*\n.*?(?=^\[|\Z)",
        lambda section: "" if int(section[1]) in by_id else section[0],
        s,
    )
    s = s.rstrip() + "\n\n# TIDEBOUND OPENING MAPS\n"
    for m in manifest:
        s += f"#-------------------------------\n[{m['id']}]\n"
        for key, value in by_id[m["id"]].pbs_metadata(m["name"]).items():
            value = str(value).lower() if isinstance(value, bool) else value
            s += f"{key} = {value}\n"
    p.write_text(s, encoding="utf-8-sig")
    print("Updated generated launch configuration and game metadata.")
