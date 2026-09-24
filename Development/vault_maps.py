# Executed by rebuild_maps.py. Preserve all original map/event identities.
home.stamp(1,237,2,2,3,11,walk=True)
home.event('Cellar stairs',3,12,'Tidebound::VaultVisit.stairs',trigger=1)
home.event('Seller at home',14,12,'pbMessage("Seller: Your mother has a better head for keys than I do.")','NPC 10',opacity=0)
# The city starts immediately beside the existing storehouse.
road.rect(37,42,8,3,tile(2,27),walk=True)
road.event('Dock city',44,43,'Tidebound::VaultVisit.city_gate',trigger=1)
road.event('Dock road sign',42,41,'pbMessage("DOCKS AND MUSEUM - EAST")')

basement=Map(110,'The Lighthouse Cellar',26,20,3)
basement.rect(3,4,20,13,tile(1,81),walk=True)
basement.rect(3,2,20,2,tile(1,13),walk=False)
for x in range(3,23,4):basement.stamp(0,0,4,2,x,1)
basement.stamp(1,237,2,2,5,13,walk=True)
basement.door(6,14,101,4,12,6)
for x,y in [(5,5),(6,5),(8,6),(20,13),(21,13),(20,14)]:
    basement.event('Crate cellar',x,y,'pbMessage("Oil tins and spare glass, wrapped carefully against the damp.")','Pokemon 01',opacity=0,blocks=True)
basement.stamp(0,140,3,2,5,9)
basement.event('Old tools',6,11,'pbMessage("A brush worn down to its wood. A spare lamp spindle. Tools repaired more often than replaced.")')
basement.event('Vault doorway',17,4,'Tidebound::VaultVisit.vault_door')
basement.event('Vault ironwork',17,3,'pbMessage("The iron door is far thicker than the cellar walls. Mother has left it open.")',blocks=True)
basement.event('Coast lamp:cellar',13,8,'pbMessage("Mother has brought a lamp down.")')

vault=Map(111,'The Lighthouse Vault',28,22,3)
vault.rect(3,3,22,16,tile(1,81),walk=True)
vault.rect(3,2,22,2,tile(1,13),walk=False)
for x in range(3,24,4):vault.stamp(0,0,4,2,x,1)
for x in [4,8,19,23]:vault.stamp(0,140,2,3,x,4)
for x,y in [(5,10),(21,10),(5,15),(21,15)]:
    vault.event('Vault pillar',x,y,'pbMessage("The stone is cold and worn smooth at shoulder height.")',blocks=True)
vault.event('Mother at vault',13,8,'pbMessage("Mother: The museum is along the quay. Keep to the lit road, love.")','NPC 11')
vault.event('Seller at vault',11,8,'pbMessage("Seller: Tell them I sent you. It will not get you a discount. Entry is free.")','NPC 10')
vault.event('Necklace drawer',12,6,'pbMessage("A shallow drawer, now locked. The seller\'s necklace rests inside, wrapped in cloth.")',blocks=True)
vault.event('Empty bays',20,6,'pbMessage("Numbered shelves. Most are empty. There is space here for much more than one household could need.")')
vault.event('Cabinet locks',6,6,'pbMessage("Small brass locks. Mother has kept the keys.")')
vault.event('Old masonry',23,17,'pbMessage("The lowest stones are darker than the rest. The mortar has been renewed around them.")')
vault.event('Arrival',3,18,'Tidebound::VaultVisit.conversation',trigger=3)
vault.door(12,18,110,17,5,2)

# Provisional dock-city outskirts: no final city name or whole-city plan is fixed.
docks=RoadMap(112,'The Docks',80,64,1,96)
docks.polygon([(9,15),(62,15),(62,39),(55,44),(16,44),(9,35)],tile(2,27))
docks.rect(9,26,47,5,tile(2,27),walk=True)
docks.rect(10,26,3,5,tile(2,13),walk=True)
docks.door(10,28,108,43,43,4)
# Museum: wider public facade with a shallow green roof and a stone forecourt.
for yy in range(4):
    for xx,sx in enumerate([4,5,5,5,5,5,6,7]):docks.rect(28+xx,18+yy,1,1,tile(sx,223+yy),z=1,walk=False)
docks.rect(31,21,1,1,tile(4,226),z=1,walk=True)
docks.event('Museum door',31,21,'Tidebound::Opening.travel(113,14,18,8)',trigger=1)
docks.event('Museum sign',35,23,'pbMessage("DOCKSIDE MUSEUM. Objects from the coast. Admission free. Please wipe your shoes.")')
for x,y in [(16,17),(43,17),(53,20)]:docks.stamp(0,227,4,4,x,y)
for x,y in [(44,30),(45,30),(48,33),(50,33),(18,33)]:
    docks.event('Crate dock',x,y,'pbMessage("Freight labels lie beneath newer freight labels. Most of the names have blurred in the salt air.")','Pokemon 01',opacity=0,blocks=True)
for x in [25,42,54]:
    docks.rect(x,41,3,10,tile(6,150),walk=True)
    docks.rect(x,51,3,1,tile(6,152),z=1,walk=False)
for x,y in [(14,27),(28,23),(37,27),(43,39),(55,34)]:docks.event('Coast lamp:dock',x,y,'pbMessage("A warm lantern in a thick glass hood.")')
docks.event('Porter',22,30,'pbMessage("Porter: Mind the ropes. We have enough things falling into the water.")','NPC 03',blocks=True)
docks.event('Mender',38,35,'pbMessage("Net mender: They bring torn nets here from every little village along the coast. Some come back with the same knot I tied last year.")','NPC 14',blocks=True)
docks.event('Warehouse notice',45,22,'pbMessage("Deliveries by arrangement. No loose goods accepted without a name and a count.")')
docks.event('Closed quay',59,28,'pbMessage("A chain closes the far quay. Work lamps glow beyond the warehouses. This part of the docks is not open yet.")')


museum=Map(113,'Dockside Museum',30,24,3)
museum.rect(3,3,24,18,tile(1,81),walk=True)
museum.rect(3,2,24,2,tile(1,13),walk=False)
for x in range(3,27,4):museum.stamp(0,0,4,2,x,1)
museum.event('Attendant',8,16,'pbMessage("Attendant: Welcome. Take your time. If you have come for the sabre, it is in the middle case.")\npbMessage("Attendant: People ask who made it. I would rather leave the label unfinished than put a guess on it.")','NPC 11',blocks=True)
museum.event('Sabre exhibit',15,8,'Tidebound::VaultVisit.sabre',blocks=True)
for x,y,name,text in [(7,7,'Harbour bell','A cracked harbour bell. The label lists the names of the people who paid to recast it.'),(22,7,'Sounding weights','Lead sounding weights and a carefully knotted line. An old way of learning how much water lies beneath a boat.'),(22,14,'Ceramic fragments','Fragments of bowls and plates from coastal households. Familiar blue reeds curve across one piece.'),(7,12,'Shipping ledger','A shipping ledger, open to a page of ordinary deliveries: lamp oil, flour, cloth.')]:
    museum.event('Museum case:'+name,x,y,f'pbMessage("{text}")',blocks=True)
museum.event('Visitor',18,12,'pbMessage("Visitor: I came in to get out of the wind. That was a while ago.")','NPC 10',blocks=True)
museum.door(14,21,112,32,23,2)

exec((DEV/'dock_details.py').read_text())
