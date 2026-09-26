"""One-time hosted completion of the authorized pond recovery; no game redesign."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile,plistlib
R=Path(__file__).resolve().parent.parent

def run(*args):subprocess.run(args,cwd=R,check=True)
def edit(name,old,new):
 p=R/name;s=p.read_text();assert old in s,(name,old);p.write_text(s.replace(old,new))
def prepare():
 run(sys.executable,'Development/Recovery/pond-0.8.4/restore_source.py')
 for name in ['rebuild_maps.py','rebuild_field_data.py','rebuild_scripts.py','validate_maps.py','Tests/pond_geometry.py']:
  run(sys.executable,'Development/'+name)
 for i in range(101,117):
  if i==108:continue
  name=f'Data/Map{i:03}.rxdata'
  assert (R/name).read_bytes()==subprocess.check_output(['git','show','373239c79cb5a625a9d68264984b4046734f57e3:'+name],cwd=R),name
 note='''## 0.8.4 — southern pond, 26 September 2026

Map108 now has a substantial pond clearing. The existing level8 Psyduck moves to19,62 and retains shoreduck_gone. Local pond grass: Psyduck40% level8-11, regional Sunkern35% level8-10, Aipom25% level8-11. Northern road encounters are unchanged. Three optional fishermen remember victories and use the existing astral-loss adapter: Toma (Magikarp9/Goldeen10), Ida (Wooper10/Poliwag11), Renzo (Barboach12). An Oran tree uses existing two-berry regrowth. The hidden western path ends in a one-time Mystic Water with full-bag retry.

The central obelisk requires later Surf. Pond water has StillWater terrain and player-only Surf passage; no HM or badge is awarded. Its origin, inscription, purpose and future reward remain open. Older saves on new obstacles/water/islet move once to26,52. Map magic26092503; Mac0.8.4/build38; same runtime, font fix and save identity.

pond_map.py runs after demo_maps.py and generates024_PondGeometry.rb plus a compact road-only atlas. 025_Pond.rb handles pond encounters, optional battles, item and migration. Grass tile391 is preserved. Tests/pond_geometry.py verifies the island is unreachable on foot and reachable with Surf; validate_maps.py explicitly excludes the future-Surf obelisk. All other15 maps remain unchanged. The recovery recipe is now historical; do not apply it again. See Development/validation_pond.md.
'''
 for name in ['AGENTS.md','Development/README.md']:
  p=R/name;p.write_text(p.read_text().rstrip()+'\n\n'+note)
 edit('AGENTS.md','**Guide version:** 2.28, 25 September 2026','**Guide version:** 2.29, 26 September 2026')
 edit('AGENTS.md','**Project baseline:** Demo 1 / 0.8.3','**Project baseline:** Demo 1 / 0.8.4')
 edit('AGENTS.md','version 1.29,\n25 September 2026','version 1.30,\n26 September 2026')
 p=R/'PROJECT_STATUS.md';s=p.read_text();i=s.index('## ');s=s[:i]+note+'\n'+s[i:];p.write_text(s.replace('Demo 1 / 0.8.3 · Bible 1.29 · Guide 2.28 · 25 September 2026','Demo 1 / 0.8.4 · Bible 1.30 · Guide 2.29 · 26 September 2026',1))
 for name in ['README.md','START_HERE.md','MAC_README.txt']:edit(name,'0.8.3','0.8.4')
 p=R/'README.md';s=p.read_text();a=s.index('## Play the current demo');b=s.index('## Project navigation',a)
 s=s[:a]+'''## Play version 0.8.4

Download Tidebound_Mac_0.8.4.zip or Tidebound_Project_0.8.4.zip from release v0.8.4. The Mac package targets Intel Monterey12.7.5 using the existing native runtime. Read MAC_README.txt for first-launch help. Existing saves retain their save folder.

## Changes in 0.8.4

The southern pond adds three optional fishermen, Psyduck/Aipom/Sunkern grass, the relocated visible Psyduck, an Oran tree and a hidden Mystic Water. A central obelisk is reserved for later Surf. The refined squat and its horror minigame remain included. Psyduck Island remains the demo endpoint, not a newly implemented destination.

'''+s[b:];p.write_text(s)
 p=R/'MAC_README.txt';s=p.read_text();a=s.index('0.8.4:');b=s.index('0.8.1:',a);p.write_text(s[:a]+'0.8.4: Explore the pond at the south end of the South Coast Road, with three\noptional fishermen, Psyduck, local grass, an Oran tree and a hidden path.\nThe central obelisk is reserved for later Surf.\n\n'+s[b:])
 p=R/'Development/design_bible.md';s=p.read_text().replace('Version 1.29 | 25 September 2026','Version 1.30 | 26 September 2026').replace('Demo 1 / 0.8.2, revised youngster hideout','Demo 1 / 0.8.4, southern pond clearing')
 s+='''\n\n## 32. The pond below the South Coast Road

**Confirmed direction.** The southern road opens onto a substantial pond and an inhabited bank. The existing free-roaming Psyduck moves here; Psyduck, Aipom and Sunkern also appear in grass. Fishermen offer optional battles. A healing berry tree and an item beyond a concealed path reward exploration. An obelisk stands on an island accessible only with Surf later.

**Prototype implementation.** Toma, Ida and Renzo share ordinary observations about hooks, nets, bait stolen by Aipom and tending the tree. Their names and teams are provisional choices. They make no supernatural claims. An Oran tree provides HP-restoring berries; a waxed bundle behind the western thicket contains Mystic Water. An already captured or defeated overworld Psyduck remains gone.

**Future boundary.** Surf is not awarded here. The obelisk's origin, inscription, purpose, future quest and reward remain open. This ordinary fishing place must not explain the sea entities.

**Presentation continuity.** The youngsters' squat retains its approved colder, paler interior: boarded windows, torn pallet mattresses and broken storage. Its quest is unchanged.
''';p.write_text(s)
 p=R/'Development/render_bible.py';s=p.read_text().replace('Version 1.29','Version 1.30').replace('25 September 2026','26 September 2026')
 old="/opt/codex/runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype"
 fonts=next(p for p in [Path(old),Path('/usr/share/fonts/truetype/liberation'),Path('/usr/share/fonts/truetype/liberation2')] if (p/'LiberationSerif-Regular.ttf').exists())
 s=s.replace(old,str(fonts));p.write_text(s)
 run(sys.executable,'Development/render_bible.py')
 p=R/'Development/Recovery/pond-0.8.4/README.md';p.write_text('> Applied by hosted recovery on26 September2026. Do not rerun restore_source.py on this implemented version.\n\n'+p.read_text())
 (R/'Development/validation_pond.md').write_text('''# Pond 0.8.4 — hosted recovery validation

The durable source checkpoint was rebuilt by GitHub Actions after repeated local workspace rollbacks. Fresh CI gates: map/event reachability, pond foot/Surf geometry, all15 other map binaries identical to0.8.3, source hash manifest, Mac archive integrity/game-file equality, bundle0.8.4/build38 and executable permissions, editable project equality against its exact commit.

Historical native Linux validation before rollback passed the final pond rendering, moved Psyduck,300 native pond selections, northern table preservation, water/Surf/NPC restrictions, old-save landing, unique item, actual fisherman battle, victory persistence and native save. That evidence was recorded in the recovery checkpoint; the old screenshot/PASS files were lost, so this run does not pretend to regenerate native graphical evidence. Tests/pond_native.rb remains available for repeat native testing and is never embedded in release Scripts.

Mac execution is not tested here. The existing mkxp-z runtime, font fix and save identity are unchanged. User Mac playtest remains necessary.\n''')
 p=R/'BUILD_MANIFEST.json';d=json.loads(p.read_text());d.update(version='0.8.4',map_magic=26092503,bible='1.30',developer_guide='2.29',checks='Development/validation_pond.md',linux_rendered_smoke_baseline='Historical pond native pass documented in recovery checkpoint; fresh CI map/package gates')
 for name in ['024_PondGeometry.rb','025_Pond.rb','pond_map.py','pond_manifest.json','Tests/pond_geometry.py','Tests/pond_native.rb','validation_pond.md','render_bible.py']:d['sha256']['Development/'+name]=''
 d['sha256']['Graphics/Tilesets/TideboundPond.png']=''
 for name in d['sha256']:d['sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
 p.write_text(json.dumps(d,indent=2)+'\n')

def package():
 out=R.parent/'pond-release';out.mkdir(exist_ok=True)
 run(sys.executable,'Development/package_mac.py',str(out))
 project=out/'Tidebound_Project_0.8.4.zip'
 run('git','archive','--format=zip','--prefix=Tidebound_Prototype/','--output='+str(project),'HEAD')
 with zipfile.ZipFile(out/'Tidebound_Mac_0.8.4.zip') as z:
  assert z.testzip() is None
  prefix='Tidebound_Mac_0.8.4/Tidebound.app/Contents/'
  info=plistlib.loads(z.read(prefix+'Info.plist'));assert info['CFBundleShortVersionString']=='0.8.4' and info['CFBundleVersion']=='38'
  assert z.getinfo(prefix+'MacOS/'+info['CFBundleExecutable']).external_attr>>16 & 0o111
  for name in z.namelist():
   if name.startswith(prefix+'Game/') and not name.endswith('/'):assert z.read(name)==(R/name.removeprefix(prefix+'Game/')).read_bytes(),name
 with zipfile.ZipFile(project) as z:
  assert z.testzip() is None
  for name in subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0'):
   if name:assert z.read('Tidebound_Prototype/'+name)==(R/name).read_bytes(),name
 (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(out.glob('*.zip'))))
 (out/'RELEASE_NOTES.md').write_text('''The South Coast Road now has a pond clearing with three optional fishermen, local Psyduck/Aipom/Sunkern grass, the relocated visible Psyduck, an Oran tree and a hidden Mystic Water. An obelisk on an islet is reserved for later Surf.

Existing saves and the refined hideout remain supported. Native Mac runtime unchanged; targets Intel Monterey12.7.5. Mac playtest is still with the player. Build38. Source and archives are verified by the hosted workflow.\n''')
 print('PASS: both release archives match verified source.')
if __name__=='__main__':
 raise SystemExit('Historical pond recovery is retired. Use Development/build_release.py; see Development/RELEASING.md.')
