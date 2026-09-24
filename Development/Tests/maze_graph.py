from pathlib import Path
import json
from collections import deque
D=Path(__file__).resolve().parents[1];q=json.loads((D/'maze_manifest.json').read_text());mask=json.loads((D/'collisions.json').read_text())['114']
a={(x,y):d for x,y,d in q['pushers']};stops={tuple(p) for p in q['stops']};warps={(x,y):(u,v) for x,y,u,v in q['warps']};goal=tuple(q['goal']);start=tuple(q['start']);dirs={2:(0,1),4:(-1,0),6:(1,0),8:(0,-1)}
def walk(p):
 x,y=p;return 0<=y<len(mask) and 0<=x<len(mask[0]) and mask[y][x]=='1' and p!=goal
for p in warps.values():assert walk(p) and p not in warps and p not in a

def resolve(p):
 if p in warps:return warps[p]
 if p not in a:return p
 d=a[p];seen=set()
 while True:
  d=a.get(p,d);k=(*p,d);assert k not in seen,'slide cycle';seen.add(k);dx,dy=dirs[d];n=p[0]+dx,p[1]+dy
  if not walk(n):return p
  p=n
  if p in stops:return p

def edges(p):return [resolve((p[0]+dx,p[1]+dy)) for dx,dy in dirs.values() if walk((p[0]+dx,p[1]+dy))]
seen={start};todo=deque([start])
while todo:
 for n in edges(todo.popleft()):
  if n not in seen:seen.add(n);todo.append(n)
good={p for p in seen if abs(p[0]-goal[0])+abs(p[1]-goal[1])==1};assert good
while True:
 new={p for p in seen if any(n in good for n in edges(p))}-good
 if not new:break
 good|=new
assert good==seen,'softlock'
assert resolve((3,9))==(17,11) and resolve((7,20))==(7,16) and resolve((17,5))==(17,3)
print(f'PASS: all {len(seen)} reachable resting positions can reach Natu; all slides terminate; warp landings avoid triggers.')
