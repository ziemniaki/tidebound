# Dock expansion. Existing museum, quay event IDs, entrances and piers stay put.
# Streets/pavements are drawn beneath buildings, so no facade footprint is erased.
def surface(x,y,w,h,t):
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            if docks.walk[yy][xx]:docks.layers[0][yy][xx]=t
# Northern residential blocks grow from the existing town land.
for yy in range(9,18):
    for xx in range(11,65):
        if docks.layers[1][yy][xx]==0:
            docks.rect(xx,yy,1,1,tile(2,27),walk=True)
surface(10,24,54,9,tile(4,50))
surface(10,27,54,4,tile(2,27))
surface(21,12,5,30,tile(4,42))
surface(38,12,5,29,tile(4,42))
surface(49,19,4,23,tile(4,42))
surface(26,21,12,6,tile(4,50))
surface(12,14,51,3,tile(4,42))
surface(16,39,41,5,tile(4,42))
for x,y in [(13,10),(20,10),(40,9),(49,10),(58,12)]:docks.stamp(4,228,4,4,x,y)
# Narrow domestic lanes and a waterfront workshop.
docks.stamp(0,227,4,4,13,34)
docks.stamp(4,228,4,4,32,33)
# Larger customs warehouse: matching native roof and pane tiles.
for yy in range(4):
    for xx,sx in enumerate([4,5,5,5,5,5,6,7]):docks.rect(44+xx,34+yy,1,1,tile(sx,223+yy),z=1,walk=False)
docks.rect(47,37,1,1,tile(4,226),z=1) # Freight door is visibly closed, not a transfer.
# Give closed building frontages ordinary descriptions; only museum entry is live.
for x,y,text in [(14,38,'SAIL REPAIRS. A needle taps against a thimble behind the door.'),(33,37,'Rooms above the quay. Someone has left boots drying inside.'),(47,38,'CUSTOMS STORE. Sealed cargo awaiting a count.'),(54,24,'A chandler\'s window. Rope, wax and spare wicks, arranged with great care.'),(18,21,'The bakery has closed. The smell of bread lingers in the doorway.')]:
    docks.event('Dock frontage',x,y,f'pbMessage({text!r})')
for x,y in [(23,17),(40,23),(51,31),(18,40),(35,40),(57,41)]:docks.event('Coast lamp:quay',x,y,'pbMessage("The lantern hood keeps most of the rain off the wick.")')
# Mooring posts, rolled nets and two working skiffs frame the old piers.
for x,y in [(25,44),(27,49),(42,44),(44,49),(54,44),(56,49)]:
    docks.event('Dock bollard',x,y,'pbMessage("Salt has gathered around the rope. The knot is fresh.")')
for x,y in [(26,47),(43,46),(55,47),(20,40)]:
    docks.event('Dock nets',x,y,'pbMessage("Nets lie drying in careful folds. A few scales still catch the light.")')
docks.event('Dock boat',28,48,'pbMessage("A little working boat, tied close to the pier. Water knocks softly against its hull.")')
docks.event('Dock boat',45,47,'pbMessage("A mended oar rests across the seats. Someone has painted over the boat\'s old name.")')
docks.event('Dock stall',30,39,'pbMessage("An empty fish stall. The boards have been scrubbed clean.")')
docks.event('Quay worker',34,40,'pbMessage("Worker: The small boats still call. Oil out, torn nets back. There is always something to mend.")','trainer_SAILOR')
docks.event('Dock resident',24,17,'pbMessage("Resident: The windows stay lit so the crews can find the quay. Even when nobody is expected.")','NPC 14')
# Newly placed walls may overlap former walking positions in existing saves.
# Landing recovery is handled additively in 013_DockDetails.rb, not a save reset.
for e in docks.events.values():
    if e.attributes['@name']=='Closed quay':
        e.attributes['@pages'][0].attributes['@list']=script('pbMessage("A chain closes the far quay. Work lamps glow beyond it.")')+[command(0)]
