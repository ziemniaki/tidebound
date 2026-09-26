from pathlib import Path
from zipfile import ZipFile
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
import zlib,json,shutil,re
from script_archive import reject_plugin_copy, script_name, source_files
from release_tools import load_release
DEV=Path(__file__).resolve().parent;GAME=DEV.parent / "game";ROOT=GAME
version=load_release(DEV.parent)['version']
reject_plugin_copy(GAME)
sources=source_files(DEV.parent / "src")
entries=[e for e in loads((GAME/'Data/Scripts.rxdata').read_bytes()) if not script_name(e[1]).startswith('Tidebound/')]
if sum(script_name(e[1])=='Main' for e in entries)!=1:
    raise ValueError('Script archive must contain exactly one Main entry')
for entry in entries:
    code=zlib.decompress(entry[2]).decode('utf-8-sig')
    name=entry[1].decode('utf-8') if isinstance(entry[1], bytes) else str(entry[1])
    entry[1]=name
    if name=='Settings':
        code=re.sub(r'GAME_VERSION = "[^"]+"', f'GAME_VERSION = "{version}"', code)
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
for i,p in enumerate(sources):
    custom.append([260908100+i,'Tidebound/'+p.stem,zlib.compress(p.read_text(encoding="utf-8").encode("utf-8"),9)])
entries[main_index:main_index]=custom
(GAME/'Data/Scripts.rxdata').write_bytes(writes(entries))
print(f'Embedded {len(custom)} Tidebound scripts into {len(entries)} entries.')
