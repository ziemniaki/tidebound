from pathlib import Path
from zipfile import ZipFile
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
import zlib,json,shutil,re
DEV=Path(__file__).resolve().parent;GAME=DEV.parent;ROOT=GAME
entries=[e for e in loads((GAME/'Data/Scripts.rxdata').read_bytes()) if not str(e[1]).startswith('Tidebound/')]
for entry in entries:
    code=zlib.decompress(entry[2]).decode('utf-8-sig')
    name=entry[1].decode('utf-8') if isinstance(entry[1], bytes) else str(entry[1])
    entry[1]=name
    if name=='Settings':
        code=re.sub(r'GAME_VERSION = "[^"]+"', 'GAME_VERSION = "0.8.0"', code)
        # Keep fixed story lighting rather than computer-clock tint changes.
        code=re.sub(r'TIME_SHADING\s*=\s*(?:true|false)','TIME_SHADING = false',code)
    # Keep mechanics untouched; replace only the two player-facing loss messages.
    if name=='Battler_ChangeSelf':
        code=code.replace('"{1} fainted!"', '"{1} died!"')
    if name=='Overworld':
        code=code.replace('"{1} fainted..."', '"{1} died..."')
    if name=='Main':
        code=code.replace('return Scene_Intro.new','return Scene_TideboundTitle.new')
    entry[2]=zlib.compress(code.encode('utf-8'),9)
main_index=next(i for i,e in enumerate(entries) if str(e[1])=='Main')
custom=[]
for i,p in enumerate(sorted(DEV.glob('[0-9][0-9][0-9]_*.rb'))):
    custom.append([260908100+i,'Tidebound/'+p.stem,zlib.compress(p.read_bytes(),9)])
entries[main_index:main_index]=custom
(GAME/'Data/Scripts.rxdata').write_bytes(writes(entries))
# Standalone title and a separate save directory avoid Essentials demo saves.
p=GAME/'Game.ini';s=p.read_text();s=s.replace('Title=Pokemon Essentials v21.1','Title=Tidebound Opening');p.write_text(s)
p=GAME/'mkxp.json';s=p.read_text();s=s.replace('"windowTitle": "Pokémon Essentials v21.1"','"windowTitle": "Tidebound - The Keeper\'s Light"');s=s.replace('// "dataPathApp": "Pokemon Essentials v21",','"dataPathApp": "Tidebound_Opening_0_2",');p.write_text(s)
md=loads((GAME/'Data/metadata.dat').read_bytes());md[0].attributes.update({'@start_money':0,'@start_item_storage':[],'@home':[101,6,10,2],'@wild_battle_BGM':'Tidebound Stillness','@wild_victory_BGM':'Tidebound Stillness','@trainer_battle_BGM':'Tidebound Stillness','@trainer_victory_BGM':'Tidebound Stillness'})
(GAME/'Data/metadata.dat').write_bytes(writes(md))
# Maintain PBS alongside compiled data, so editor recompilation keeps new maps.
p=GAME/'PBS/metadata.txt';s=p.read_text(encoding='utf-8-sig');s=s.replace('StartMoney = 3000','StartMoney = 0');s=s.replace('StartItemStorage = POTION','StartItemStorage = ');s=s.replace('Home = 3,7,5,8','Home = 101,6,10,2')
for kind in ['WildBattleBGM','WildVictoryBGM','TrainerBattleBGM','TrainerVictoryBGM']:
    import re
    s=re.sub(r'^'+kind+r'\s*=.*$',kind+' = Tidebound Stillness',s,flags=re.M)
p.write_text(s,encoding='utf-8-sig')
p=GAME/'PBS/map_metadata.txt';s=p.read_text(encoding='utf-8-sig')
s=s.split('# TIDEBOUND OPENING MAPS')[0].rstrip()+'\n\n# TIDEBOUND OPENING MAPS\n'
for m in json.loads((DEV/'map_manifest.json').read_text()):
    s+=f"#-------------------------------\n[{m['id']}]\nName = {m['name']}\nShowArea = true\nBattleBack = {'cave1' if m['id']==105 else 'field'}\n"
    if m['id']==103:s+='Environment = Forest\n'
    if m['id']==105:s+='Environment = Cave\n'
p.write_text(s,encoding='utf-8-sig')
# Plugin compilation is unrelated; no duplicate copy of Tidebound in Plugins.
assert not (GAME/'Plugins/Tidebound').exists()
print(f'Embedded {len(custom)} Tidebound scripts into {len(entries)} entries; updated launch/save configuration and PBS.')
