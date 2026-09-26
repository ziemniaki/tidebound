from tidebound_dev.paths import ROOT
from pathlib import Path
from collections import deque
from rubymarshal.reader import loads
import argparse,json,re,struct
from tidebound_dev.scripts.archive import validate_archive


def validate(root, event_scripts_output=None, check_scripts=True):
    D = root / "tools"
    G = root / "game"
    ROOT = G
    if check_scripts: validate_archive(G,D.parent / "src")
    masks=json.loads((D / 'generated' / 'collisions.json').read_text());manifest=json.loads((D / 'generated' / 'map_manifest.json').read_text())
    spawns={101:[(6,10),(10,12),(16,4),(6,4)],102:[(32,36),(48,25),(45,32),(77,40)],103:[(17,25),(11,22)],104:[(6,9)],105:[(15,21)],106:[(8,10)],107:[(6,8),(8,10)],108:[(18,5),(35,43),(26,39)],109:[(11,14)],110:[(6,13),(17,5)],111:[(12,15)],112:[(11,28),(32,23)],113:[(14,18)],114:[(5,20),(4,11),(9,17),(22,5),(16,4)],115:[(7,8),(4,7),(7,5),(9,8)],116:[(7,22),(25,7)]}
    maze_data=json.loads((D / 'generated' / 'maze_manifest.json').read_text())
    fail=[];event_scripts=[];count=0
    for spec in manifest:
     mid=spec['id'];m=loads((G/f'Data/Map{mid:03}.rxdata').read_bytes()).attributes
     mask=masks[str(mid)];w=spec['width'];h=spec['height']
     raw=m['@data']._dump()
     if (m['@width'],m['@height'])!=(w,h) or len(mask)!=h or any(len(row)!=w for row in mask):
      fail.append(f'{mid} map/mask dimensions disagree with manifest');continue
     if len(raw)<20 or struct.unpack('<5i',raw[:20])!=(3,w,h,3,w*h*3) or len(raw)!=20+w*h*3*2:
      fail.append(f'{mid} tile table dimensions disagree with manifest');continue
     def walk(x,y):return 0<=x<w and 0<=y<h and mask[y][x]=='1'
     q=deque([spawns[mid][0]]);seen=set(q)
     while q:
      x,y=q.popleft()
      for p in [(x+dx,y+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]+([(dx,dy) for sx,sy,dx,dy in maze_data['warps'] if (x,y)==(sx,sy)] if mid==114 else []):
       if p not in seen and walk(*p):seen.add(p);q.append(p)
     for spawn in spawns[mid]:
      if spawn not in seen or not walk(*spawn):fail.append(f'{mid} unreachable arrival {spawn}')
     for ev in m['@events'].values():
      e=ev.attributes;x=e['@x'];y=e['@y'];name=str(e['@name']);page=e['@pages'][0].attributes
      charset=str(page['@graphic'].attributes['@character_name'])
      if charset and not (G/'Graphics/Characters'/f'{charset}.png').exists():fail.append(f'{mid} missing charset {charset}')
      if page['@trigger']!=3 and name not in ['Lapras','Pond obelisk (Surf)']:
       reachable=(x,y) in seen if page['@trigger']==1 else any((x+dx,y+dy) in seen for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
       if not reachable:fail.append(f'{mid} unreachable event {name} at {x},{y}')
      code='\n'.join(str(c.attributes['@parameters'][0]) for c in page['@list'] if c.attributes['@code'] in (355,655))
      if code:event_scripts.append({'name':f'Map{mid}/{name}','code':code})
      for dest,tx,ty in re.findall(r'Opening.travel\((\d+), (\d+), (\d+)',code):
       if masks[dest][int(ty)][int(tx)]!='1':fail.append(f'{mid}: blocked transfer to {dest} {tx},{ty}')
      for tx,ty in re.findall(r'Opening.travel_coast\((\d+), (\d+)',code):
       if masks['102'][int(ty)+20][int(tx)+24]!='1':fail.append(f'{mid}: blocked coast transfer')
      count+=1
     bgm=str(m['@bgm'].attributes['@name'])
     if not (G/'Audio/BGM'/f'{bgm}.ogg').exists():fail.append(f'{mid} missing BGM {bgm}')
     print(f'Map {mid}: {len(seen)} connected walkable cells; {len(m["@events"])} events')
    metadata=loads((G/'Data/map_metadata.dat').read_bytes())
    for mid in spawns:
     back=str(metadata[mid].attributes['@battle_background'])
     for suffix in ['_bg','_base0','_base1','_message']:
      if not (G/'Graphics/Battlebacks'/f'{back}{suffix}.png').exists():fail.append(f'{mid} missing battleback {back}{suffix}')
    coast=masks['102']
    if len(coast)!=88 or len(coast[0])!=108:fail.append('coast dimensions must be 108x88')
    if not all(9<=x<99 and 7<=y<81 for y,row in enumerate(coast) for x,v in enumerate(row) if v=='1'):fail.append('coast camera margin')
    if not all(coast[y][x]=='0' for y in range(30,55) for x in range(80,108)):fail.append('open sea beyond pier')
    if fail:raise RuntimeError('\n'.join(fail))
    if event_scripts_output:event_scripts_output.write_text(json.dumps(event_scripts),encoding='utf-8')
    print(f'PASS: {count} map events; every arrival, door and interaction reachable.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Check maps and embedded source without rewriting game data.')
    parser.add_argument('--event-scripts',type=Path,help='Explicit destination for extracted event scripts')
    args=parser.parse_args()
    validate(ROOT, args.event_scripts)
