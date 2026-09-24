"""Regional Psyduck and its original Water/Psychic evolution, Whyduck.

Keep ordinary Psyduck/Golduck and owned Pokémon untouched. This builder can
also be run on its own after the main regional data rebuild.
"""
from pathlib import Path
import runpy, shutil
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S

G=Path(__file__).resolve().parent.parent
species=loads((G/'Data/species.dat').read_bytes())
clone=lambda obj:loads(writes(obj))
form=clone(species[S('PSYDUCK')])
form.attributes.update({'@id':S('PSYDUCK_1'),'@species':S('PSYDUCK'),
    '@form':1,'@pokedex_form':1,'@real_form_name':'Tidebound',
    '@types':[S('WATER'),S('PSYCHIC')],
    '@evolutions':[[S('WHYDUCK'),S('Level'),16,False]],
    '@pbs_file_suffix':'tidebound_psyduck'})
species[S('PSYDUCK_1')]=form
(G/'PBS/pokemon_forms_tidebound_psyduck.txt').write_text(
    '# Regional shore Psyduck. All other fields inherit the ordinary form.\n'
    '[PSYDUCK,1]\nFormName = Tidebound\nTypes = WATER,PSYCHIC\n'
    'Evolutions = WHYDUCK,Level,16\n',encoding='utf-8-sig')

stats={'HP':75,'ATTACK':55,'DEFENSE':70,'SPEED':75,
       'SPECIAL_ATTACK':130,'SPECIAL_DEFENSE':115}
moves=[(0,'PSYCHIC'),(1,'AQUAJET'),(1,'WATERGUN'),(1,'CONFUSION'),
       (1,'TAILWHIP'),(9,'PSYBEAM'),(13,'WATERPULSE'),(17,'DISABLE'),
       (21,'MIST'),(25,'PSYCHUP'),(29,'AQUARING'),(35,'CALMMIND'),
       (40,'PSYSHOCK'),(44,'BRINE'),(48,'FUTURESIGHT'),(52,'HYDROPUMP'),
       (56,'PSYCHICTERRAIN'),(60,'RECOVER'),(65,'STOREDPOWER')]
tutors=['PSYCHIC','PSYSHOCK','FUTURESIGHT','CALMMIND','LIGHTSCREEN',
        'REFLECT','TRICKROOM','PSYCHICTERRAIN','SURF','SCALD','ICEBEAM',
        'BLIZZARD','RAINDANCE','PROTECT','REST','DIVE','ENCORE',
        'AMNESIA','SUBSTITUTE','WATERPULSE','WONDERROOM']
valid=loads((G/'Data/moves.dat').read_bytes())
abilities=loads((G/'Data/abilities.dat').read_bytes())
assert all(S(m) in valid for _,m in moves)
assert all(S(m) in valid for m in tutors)
assert all(S(a) in abilities for a in ['OWNTEMPO','CLOUDNINE','INNERFOCUS'])
assert sum(stats.values())==520
entry=('Its headaches ceased when the folds on its head opened. It stands '
       'quietly by the tide for hours, as if considering a question it cannot ask.')
duck=clone(species[S('PSYDUCK')])
duck.attributes.update({'@id':S('WHYDUCK'),'@species':S('WHYDUCK'),
    '@form':0,'@pokedex_form':0,'@real_name':'Whyduck',
    '@real_form_name':None,'@real_category':'Still Mind',
    '@real_pokedex_entry':entry,'@types':[S('WATER'),S('PSYCHIC')],
    '@base_stats':{S(k):v for k,v in stats.items()},
    '@base_exp':190,'@catch_rate':75,'@happiness':70,
    '@evs':{S(k):(2 if k=='SPECIAL_ATTACK' else 0) for k in stats},
    '@abilities':[S('OWNTEMPO'),S('CLOUDNINE')],
    '@hidden_abilities':[S('INNERFOCUS')],
    '@moves':[[lv,S(m)] for lv,m in moves],
    '@tutor_moves':[S(m) for m in tutors],
    '@egg_moves':[],
    '@evolutions':[[S('PSYDUCK'),S('Level'),16,True]],
    '@height':11,'@weight':260,'@color':S('Yellow'),
    '@generation':0,'@flags':['DefaultForm_0'],
    '@pbs_file_suffix':'whyduck'})
species[S('WHYDUCK')]=duck
(G/'Data/species.dat').write_bytes(writes(species))

flat=lambda seq:','.join(str(item).lstrip(':') for item in seq)
shape=str(duck.attributes['@shape']).lstrip(':')
pbs=['# Regional Psyduck evolution. Build via Development/rebuild_whyduck_data.py.',
     '[WHYDUCK]','Name = Whyduck','Types = WATER,PSYCHIC',
     'BaseStats = '+flat(stats.values()),'GenderRatio = Female50Percent',
     'GrowthRate = Medium','BaseExp = 190','EVs = SPECIAL_ATTACK,2',
     'CatchRate = 75','Happiness = 70','Abilities = OWNTEMPO,CLOUDNINE',
     'HiddenAbilities = INNERFOCUS',
     'Moves = '+flat(v for pair in moves for v in pair),
     'TutorMoves = '+flat(tutors),'EggGroups = Water1,Field',
     'HatchSteps = 5120','Height = 1.1','Weight = 26.0',
     'Color = Yellow','Shape = '+shape,'Habitat = WatersEdge',
     'Category = Still Mind','Pokedex = '+entry,'Generation = 0',
     'Flags = DefaultForm_0']
(G/'PBS/pokemon_whyduck.txt').write_text('\n'.join(pbs)+'\n',encoding='utf-8-sig')

metrics=loads((G/'Data/species_metrics.dat').read_bytes())
metric=clone(metrics[S('PSYDUCK')])
metric.attributes.update({'@id':S('WHYDUCK'),'@species':S('WHYDUCK'),
    '@form':0,'@front_sprite':[1,13],'@back_sprite':[0,5],
    '@shadow_x':0,'@shadow_size':2,'@pbs_file_suffix':'whyduck'})
metrics[S('WHYDUCK')]=metric
(G/'Data/species_metrics.dat').write_bytes(writes(metrics))
(G/'PBS/pokemon_metrics_whyduck.txt').write_text(
    '[WHYDUCK]\nBackSprite = 0,5\nFrontSprite = 1,13\n'
    'ShadowX = 0\nShadowSize = 2\n')
for folder in ('Front','Back','Front shiny','Back shiny','Icons'):
    shutil.copy2(G/f'Graphics/Pokemon/{folder}/PSYDUCK.png',
                 G/f'Graphics/Pokemon/{folder}/PSYDUCK_1.png')
shutil.copy2(G/'Audio/SE/Cries/PSYDUCK.ogg',
             G/'Audio/SE/Cries/WHYDUCK.ogg')
runpy.run_path(str(G/'Development/Art/Whyduck/draw_sprites.py'))
print('Psyduck form 1 Water/Psychic evolves at 16 into Whyduck (BST 520).')
