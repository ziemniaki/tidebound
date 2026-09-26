from pathlib import Path
from collections import deque
import json
from rubymarshal.reader import loads
R=Path(__file__).resolve().parents[2]
p=json.loads((R/'Development/pond_manifest.json').read_text())
mask=json.loads((R/'Development/collisions.json').read_text())['108']
water=set(map(tuple,p['water']));island=set(map(tuple,p['island']))
def reachable(surf=False):
 seen={(18,5)};q=deque(seen)
 while q:
  x,y=q.popleft()
  for n in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
   xx,yy=n
   if n in seen or not (0<=yy<len(mask) and 0<=xx<len(mask[0])):continue
   if mask[yy][xx]=='1' or (surf and n in water):seen.add(n);q.append(n)
 return seen
foot=reachable();surf=reachable(True)
assert not foot & island,'Island reachable on foot'
assert island-{tuple(p['obelisk'])}<=surf,'Surf cannot reach landing'
assert set(map(tuple,p['hidden_path']))<=foot,'Hidden spur blocked'
assert all(mask[y][x]=='0' for x,y in water)
m=loads((R/'Data/Map108.rxdata').read_bytes()).attributes
for e in m['@events'].values():
 a=e.attributes
 if a['@name'].startswith('Pond fisher') or a['@name'] in ['Pond hidden cache','Berry:ORANBERRY','Wild:PSYDUCK:shoreduck']:
  x,y=a['@x'],a['@y'];assert any(n in foot for n in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]),a['@name']
print('PASS: actors/rewards reachable; hidden path open; island requires Surf.')
