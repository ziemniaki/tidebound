"""Nivalora: final regional Wurmple evolution. Called by branch builder."""
from pathlib import Path
import shutil,re,runpy
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S
G=Path(__file__).resolve().parent.parent
species=loads((G/'Data/species.dat').read_bytes())
clone=lambda x:loads(writes(x))
frost=species[S('FROSTCOON')]
frost.attributes['@evolutions']=[[S('NIVALORA'),S('Level'),55,False],[S('WURMPLE'),S('Cascoon'),10,True]]
stats={'HP':100,'ATTACK':45,'DEFENSE':65,'SPEED':145,'SPECIAL_ATTACK':130,'SPECIAL_DEFENSE':115}
# Retain the cocoon's non-evolution support moves for reminder access and delayed evolution.
moves=[(0,'DRAGONBREATH'),(1,'GUST'),(1,'POWDERSNOW')]
moves += [(lv,str(m).lstrip(':')) for lv,m in frost.attributes['@moves'] if lv>0]
moves += [(55,'ICEBEAM'),(58,'DRAGONDANCE'),(61,'ROOST'),(64,'DRAGONPULSE'),
          (68,'BLIZZARD'),(72,'QUIVERDANCE'),(76,'TAILWIND'),(80,'MIST')]
tutors=['PROTECT','ENDURE','SUBSTITUTE','SAFEGUARD','LIGHTSCREEN','REFLECT',
        'HAIL','RAINDANCE','HELPINGHAND','ICEBEAM','BLIZZARD','ICYWIND',
        'DRAGONPULSE','DRACOMETEOR','ROOST','TAILWIND','AERIALACE','ACROBATICS']
valid=loads((G/'Data/moves.dat').read_bytes())
assert sum(stats.values())==600
assert all(S(m) in valid for _,m in moves)
assert all(S(m) in valid for m in tutors)
assert not any('Poison' in str(valid[S(m)].attributes['@function_code']) for m in [m for _,m in moves]+tutors)
entry=('Rarely seen, it shelters lost travelers beneath its frost-white wings. '
       'Its gentle scales lull frightened creatures to sleep, and it waits beside them until they wake.')
data=clone(frost)
data.attributes.update({'@id':S('NIVALORA'),'@species':S('NIVALORA'),'@real_name':'Nivalora',
 '@real_category':'Kindly Wings','@real_pokedex_entry':entry,'@types':[S('ICE'),S('DRAGON')],
 '@base_stats':{S(k):v for k,v in stats.items()},'@evs':{S(k):(3 if k=='SPEED' else 0) for k in stats},
 '@base_exp':300,'@catch_rate':45,'@happiness':70,'@abilities':[S('SHIELDDUST')],
 '@hidden_abilities':[],'@moves':[[lv,S(m)] for lv,m in moves],'@tutor_moves':[S(m) for m in tutors],
 '@egg_moves':[],'@egg_groups':[S('Bug'),S('Dragon')], '@evolutions':[[S('FROSTCOON'),S('Level'),55,True]],
 '@height':24,'@weight':220,'@color':S('White'),'@shape':species[S('VENOMOTH')].attributes['@shape'],
 '@pbs_file_suffix':'nivalora'})
species[S('NIVALORA')]=data
(G/'Data/species.dat').write_bytes(writes(species))
p=G/'PBS/pokemon_glaciverm.txt';text=p.read_text(encoding='utf-8-sig')
text=re.sub(r'^Evolutions = NIVALORA,Level,55\n','',text,flags=re.M).rstrip()+'\nEvolutions = NIVALORA,Level,55\n'
p.write_text(text,encoding='utf-8-sig')
flat=lambda values:','.join(str(v).lstrip(':') for v in values)
lines=['[NIVALORA]','Name = Nivalora','Types = ICE,DRAGON','BaseStats = '+flat(stats.values()),
 'GenderRatio = Female50Percent','GrowthRate = Medium','BaseExp = 300','EVs = SPEED,3',
 'CatchRate = 45','Happiness = 70','Abilities = SHIELDDUST',
 'Moves = '+flat([v for pair in moves for v in pair]),'TutorMoves = '+flat(tutors),
 'EggGroups = Bug,Dragon','HatchSteps = 3840','Height = 2.4','Weight = 22.0',
 'Color = White','Shape = '+str(data.attributes['@shape']).lstrip(':'),'Habitat = Forest',
 'Category = Kindly Wings','Pokedex = '+entry,'Generation = 0','Flags = DefaultForm_0']
(G/'PBS/pokemon_nivalora.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
metrics=loads((G/'Data/species_metrics.dat').read_bytes());m=clone(metrics[S('VENOMOTH')])
m.attributes.update({'@id':S('NIVALORA'),'@species':S('NIVALORA'),'@back_sprite':[0,0],
 '@front_sprite':[0,4],'@front_sprite_altitude':8,'@shadow_x':0,'@shadow_size':1,'@pbs_file_suffix':'nivalora'})
metrics[S('NIVALORA')]=m;(G/'Data/species_metrics.dat').write_bytes(writes(metrics))
(G/'PBS/pokemon_metrics_nivalora.txt').write_text('[NIVALORA]\nBackSprite = 0,0\nFrontSprite = 0,4\nFrontSpriteAltitude = 8\nShadowX = 0\nShadowSize = 1\n')
for directory in ['Front','Back','Front shiny','Back shiny','Icons']:
 shutil.copy2(G/f'Graphics/Pokemon/{directory}/FROSTCOON_EVOLUTION.png',G/f'Graphics/Pokemon/{directory}/NIVALORA.png')
# Existing birdlike call is a declared placeholder, not a new authored cry.
shutil.copy2(G/'Audio/SE/Cries/ARTICUNO.ogg',G/'Audio/SE/Cries/NIVALORA.ogg')
print('Nivalora built: Ice/Dragon, BST 600, Shield Dust; Frostcoon evolves at 55.')
