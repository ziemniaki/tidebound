"""Demo 1 additions. Appended event IDs preserve old saves and story actors."""
import runpy
_art=runpy.run_path(str(DEV/'demo_art.py'))
# A separate atlas gives only Shiohama wooden homes; lighthouse pixels are exact.
tilesets=loads((GAME/'Data/Tilesets.rxdata').read_bytes())
village_id=next((i for i,t in enumerate(tilesets) if t and t.attributes.get('@name')=='Tidebound Village'),len(tilesets))
ts=loads(writes(tilesets[coast.tileset]));ts.attributes.update({'@id':village_id,'@name':'Tidebound Village','@tileset_name':'TideboundVillage'})
original=Image.open(GAME/'Graphics/Tilesets/TideboundLandscape.png').convert('RGBA')
village=_art['wooden_village'](original)
assert village.crop((5*32,444*32,8*32,452*32)).tobytes()==original.crop((5*32,444*32,8*32,452*32)).tobytes()
village.save(GAME/'Graphics/Tilesets/TideboundVillage.png')
if village_id==len(tilesets):tilesets.append(ts)
else:tilesets[village_id]=ts
coast.tileset=village_id
(GAME/'Data/Tilesets.rxdata').write_bytes(writes(tilesets))

# A visible, stationary duck at a clear roadside pool approach. Static event avoids
# wandering into grass battle triggers or hiding in existing scenery.
road.event('Wild:PSYDUCK:shoreduck',27,36,'Tidebound::DemoLaunch.psyduck','Pokemon 01',opacity=0)
for x,y in [(27,36),(26,36),(27,35),(27,37)]:
    road.layers[1][y][x]=0;road.layers[2][y][x]=0;road.walk[y][x]=True

# Keep both original little skiffs; move their anchors clear of the new hulls.
for e in docks.events.values():
    a=e.attributes
    if a['@name']=='Dock boat':
        a['@x']=24 if a['@x']==28 else 45
        a['@y']=48 if a['@x']==24 else 50
# Two moored wooden sailing ships, approached through existing three-wide piers.
# Ship art is offset from these reachable interactive mooring points.
docks.event('Demo prop:ship1',27,47,'pbMessage("The Salt Thread. Its hull smells of pine tar. A cargo list promises flour, hinges and letters.")')
docks.event('Demo prop:ship2',56,47,'pbMessage("The Little Promise. Fresh rope and carefully mended sails. A little duck is carved into the tiller.")')
for x in [28,57]:
    docks.rect(x,48,1,1,tile(6,150),walk=False)
# Work parties gather in loose groups; the middle of each pier remains open.
crew=[('ropes',24,41),('keeper',26,42),('flour',25,46),('stars',27,45),
      ('letters',30,41),('cargo',33,42),('museum',39,40),('snow',46,42),
      ('pie',53,40),('sleep',55,42),('islands',54,46),('repairs',56,45),('mate',50,40)]
for i,(key,x,y) in enumerate(crew):
    docks.event('Sailor '+key,x,y,f'Tidebound::DemoLaunch.talk(:{key})','trainer_SAILOR',blocks=True)
    docks.events[len(docks.events)].attributes['@pages'][0].attributes['@graphic'].attributes['@direction']=[2,4,6,8][i%4]
for key,x,y in [('nell',26,49),('oren',43,42)]:
    docks.event('Sailor '+key,x,y,f'Tidebound::DemoLaunch.sailor_battle(:{key})','trainer_SAILOR',blocks=True)
docks.event('Island captain',55,49,'Tidebound::DemoLaunch.voyage','trainer_SAILOR',blocks=True)
for x,y in [(35,38),(48,39),(51,41)]:
    docks.event('Demo prop:cargo',x,y,'pbMessage("Crates of lamp oil and flour. The destination is written twice: PSYDUCK ISLAND.")',blocks=True)
    # Collision follows the complete 2x2 stack, not just the interactive anchor.
    for yy in range(y,y+2):
        for xx in range(x,x+2):docks.walk[yy][xx]=False
for name,x,y,text in [
 ('board',51,38,'NEXT WATCH: The Little Promise, Psyduck Island. Passengers: ask the captain on the eastern pier.'),
 ('ledger',36,41,'Flour: twelve sacks. Oil: six tins. Letters: one sealed box. Paid in full, except for the letters.'),
 ('memorial',19,40,'A low stone bears names worn shallow by hands. Fresh knots of ribbon hang from the rail beside it.')]:
    docks.event('Demo prop:'+name,x,y,f'pbMessage("{text}")',blocks=True)
# Refresh targets after moved historical skiffs (IDs and scripts stay unchanged).
docks.targets=[(e.attributes['@name'],e.attributes['@x'],e.attributes['@y'],e.attributes['@pages'][0].attributes['@trigger'],t[4]) for e,t in zip(docks.events.values(),docks.targets)]
