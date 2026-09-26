"""Prepare a disposable native test: engine-directory, output-directory arguments."""
from pathlib import Path
import sys,shutil,zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes
ROOT=Path(__file__).resolve().parents[1]
G=ROOT / "game";R=Path(sys.argv[1]).resolve();T=Path(sys.argv[2]).resolve()
if T==ROOT or T.is_relative_to(ROOT):
 raise SystemExit('Use a disposable directory outside the project')
T.mkdir(parents=True,exist_ok=True)
for name in ['mkxp-z.x86_64','lib64','stdlib','scripts']:
 p=R/name;d=T/name
 if d.exists():continue
 if p.is_dir():shutil.copytree(p,d)
 else:shutil.copy2(p,d)
for name in ['Data','Audio','Graphics','Fonts','Plugins']:
 if (G/name).exists():shutil.copytree(G/name,T/name,dirs_exist_ok=True)
for name in ['Game.ini','mkxp.json','soundfont.sf2']:shutil.copy2(G/name,T/name)
shutil.copy2(R/'chosen-party.rxdata',T/'chosen-party.rxdata')
p=T/'mkxp.json';p.write_text(p.read_text().replace('Tidebound_Opening_0_2','Tidebound_Neighbor_Render_Test'))
es=loads((G/'Data/Scripts.rxdata').read_bytes());i=next(i for i,e in enumerate(es) if e[1]=='Main')
es.insert(i,[260910999,'Test only',zlib.compress((ROOT/'tests/rendered_neighbor.rb').read_bytes())]);(T/'Data/Scripts.rxdata').write_bytes(writes(es))
print('Prepared disposable native engine.')
