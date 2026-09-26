import copy
from .model import NEIGHBORS, tile

def shoreline(m):
    old=copy.deepcopy(m.layers[0])
    def water(x,y):
        v=old[max(0,min(m.h-1,y))][max(0,min(m.w-1,x))]
        return 48<=v<192 or v==tile(1,151)
    for y in range(m.h):
        for x in range(m.w):
            if not 48<=old[y][x]<192:continue
            mask=sum(1<<i for i,(dx,dy) in enumerate([(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]) if water(x+dx,y+dy))
            m.layers[0][y][x]=48+NEIGHBORS[mask]
def coastal_shoreline(m):
    old=copy.deepcopy(m.layers[0])
    def land(x,y):
        if not (0<=x<m.w and 0<=y<m.h):return False
        v=old[y][x]
        return v==192 or (v>=384 and v not in [tile(6,150),tile(6,151)])
    offsets=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
    for y in range(m.h):
        for x in range(m.w):
            v=old[y][x]
            if v==192:
                mask=sum(1<<i for i,(dx,dy) in enumerate(offsets) if land(x+dx,y+dy))
                m.layers[0][y][x]=192+NEIGHBORS[mask]
            elif 48<=v<192:
                if any(0<=y+dy<m.h and 0<=x+dx<m.w and old[y+dy][x+dx]==192 for dx,dy in offsets):m.layers[0][y][x]=96
                else:
                    mask=sum(1<<i for i,(dx,dy) in enumerate(offsets) if not land(x+dx,y+dy))
                    m.layers[0][y][x]=48+NEIGHBORS[mask]
