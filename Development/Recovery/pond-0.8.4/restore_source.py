"""Explicit, guarded recovery from verified 0.8.3. Stages source; does not build/publish."""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEV=ROOT/'Development'
changes={}
def replace(path,old,new):
    p=ROOT/path;s=changes.get(p,p.read_text())
    if s.count(old)!=1:raise RuntimeError(f'{path}: expected one exact baseline match; inspect instead of retrying')
    changes[p]=s.replace(old,new,1)
replace('Development/rebuild_maps.py',"RoadMap(108,'The South Coast Road',56,68", "RoadMap(108,'The South Coast Road',56,84")
replace('Development/rebuild_maps.py',"exec((DEV/'demo_maps.py').read_text())", "exec((DEV/'demo_maps.py').read_text())\nexec((DEV/'pond_map.py').read_text())")
replace('Development/rebuild_maps.py','26092502','26092503')
replace('Development/validate_maps.py',"if page['@trigger']!=3 and name!='Lapras':", "if page['@trigger']!=3 and name not in ['Lapras','Pond obelisk (Surf)']:")
needle="(G/'Data/encounters.dat').write_bytes(writes(enc))"
addition="""# Pond-only grass; northern road retains its original encounters.
pond=[(40,'PSYDUCK',8,11),(35,'SUNKERN',8,10),(25,'AIPOM',8,11)]
record=enc[Symbol('108_0')].attributes
record['@step_chances'][Symbol('PondGrass')]=18
record['@types'][Symbol('PondGrass')]=[[w,Symbol(n),lo,hi] for w,n,lo,hi in pond]
text+='PondGrass,18\\n'+''.join(f'    {w},{n},{lo},{hi}\\n' for w,n,lo,hi in pond)
"""
replace('Development/rebuild_field_data.py',needle,addition+needle)
for name in ['Development/001_Core.rb','Development/rebuild_scripts.py','Development/package_mac.py']:
    replace(name,'0.8.3','0.8.4')
replace('Development/package_mac.py',"CFBundleVersion='37'","CFBundleVersion='38'")
for name in ['pond_map.py','025_Pond.rb']:
    if (DEV/name).exists():raise RuntimeError(f'{name} already exists; preserve and compare it')
for p,s in changes.items():p.write_text(s)
for name in ['pond_map.py','025_Pond.rb']:shutil.copy2(HERE/name,DEV/name)
for name in ['pond_geometry.py','pond_native.rb']:shutil.copy2(HERE/name,DEV/'Tests'/name)
print('Source staged. Follow README validation/build steps. No publication has occurred.')
