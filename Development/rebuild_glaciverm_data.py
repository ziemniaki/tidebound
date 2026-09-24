"""Build Glaciverm and Frostcoon, the two regional Wurmple branches.

Called by rebuild_wurmple_data.py. Includes Nivalora, the level-55 Ice/Dragon final evolution.
"""
from pathlib import Path
import shutil
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S

G = Path(__file__).resolve().parent.parent
species = loads((G / 'Data/species.dat').read_bytes())
clone = lambda value: loads(writes(value))
stats = {'HP':75, 'ATTACK':105, 'DEFENSE':110, 'SPEED':40,
         'SPECIAL_ATTACK':40, 'SPECIAL_DEFENSE':65}
moves = [(0,'BUGBITE'), (1,'TACKLE'), (1,'STRINGSHOT'), (1,'POWDERSNOW'),
         (10,'ICESHARD'), (13,'BIND'), (16,'ICEFANG'), (20,'FIRSTIMPRESSION'),
         (24,'COIL'), (28,'PINMISSILE'), (32,'IRONDEFENSE'), (36,'ICICLESPEAR'),
         (40,'XSCISSOR'), (44,'ICICLECRASH'), (48,'LUNGE')]
tutors = ['BUGBITE','ICEFANG','IRONDEFENSE','PROTECT','ENDURE',
          'FACADE','SUBSTITUTE','SLEEPTALK','SNORE','ICEBEAM','BLIZZARD','XSCISSOR']
valid_moves = loads((G / 'Data/moves.dat').read_bytes())
assert all(S(m) in valid_moves for _,m in moves)
assert all(S(m) in valid_moves for m in tutors)
entry = ('It coils its long body beneath roots. Overlapping plates of frozen '
         'chitin protect it while it waits to strike at anything that steps too close.')
glaci = clone(species[S('WURMPLE')])
glaci.attributes.update({
    '@id':S('GLACIVERM'), '@species':S('GLACIVERM'), '@form':0, '@pokedex_form':0,
    '@real_name':'Glaciverm', '@real_form_name':None, '@real_category':'Frost Coil',
    '@real_pokedex_entry':entry, '@types':[S('ICE'),S('BUG')],
    '@base_stats':{S(k):v for k,v in stats.items()}, '@base_exp':145,
    '@evs':{S(k):(2 if k=='DEFENSE' else 0) for k in stats}, '@catch_rate':75,
    '@abilities':[S('TECHNICIAN')], '@hidden_abilities':[],
    '@moves':[[lv,S(m)] for lv,m in moves], '@tutor_moves':[S(m) for m in tutors],
    '@egg_moves':[], '@wild_item_common':[], '@wild_item_uncommon':[], '@wild_item_rare':[],
    '@evolutions':[[S('WURMPLE'),S('Silcoon'),10,True]],
    '@height':18, '@weight':240, '@color':S('Blue'),
    '@shape':species[S('SEVIPER')].attributes['@shape'], '@generation':0,
    '@flags':['DefaultForm_0'], '@pbs_file_suffix':'glaciverm'
})
species[S('GLACIVERM')] = glaci

# Authored support cocoon; the final builder appends its level-55 evolution.
cocoon = clone(species[S('SILCOON')])
cocoon_entry = ('It seals itself in silk glazed with frost. Even when its shell lies '
                'perfectly still, a faint scratching can be heard from within.')
cocoon_stats = {'HP':65,'ATTACK':35,'DEFENSE':95,'SPEED':15,
                'SPECIAL_ATTACK':55,'SPECIAL_DEFENSE':85}
cocoon_moves = [(0,'SPIKES'),(1,'HARDEN'),(1,'STRINGSHOT'),(10,'WISH'),
                (13,'STUNSPORE'),(16,'RAINDANCE'),(19,'PROTECT'),(22,'LIFEDEW'),
                (25,'STICKYWEB'),(28,'SLEEPPOWDER'),(31,'HAIL'),(34,'AURORAVEIL'),
                (38,'REFLECT'),(42,'LIGHTSCREEN'),(46,'SAFEGUARD'),
                (50,'BATONPASS'),(54,'WIDEGUARD')]
cocoon_tutors = ['PROTECT','ENDURE','SUBSTITUTE','SAFEGUARD','LIGHTSCREEN',
                 'REFLECT','HAIL','RAINDANCE','IRONDEFENSE','HELPINGHAND']
assert all(S(m) in valid_moves for _,m in cocoon_moves)
assert all(S(m) in valid_moves for m in cocoon_tutors)
assert all(valid_moves[S(m)].attributes['@category'] == 2
           for m in [m for _,m in cocoon_moves] + cocoon_tutors)
assert S('SHELLARMOR') in loads((G/'Data/abilities.dat').read_bytes())
cocoon.attributes.update({
    '@id':S('FROSTCOON'), '@species':S('FROSTCOON'), '@form':0, '@pokedex_form':0,
    '@real_name':'Frostcoon', '@real_form_name':None, '@real_category':'Frozen Silk',
    '@real_pokedex_entry':cocoon_entry, '@types':[S('BUG'),S('ICE')],
    '@base_stats':{S(k):v for k,v in cocoon_stats.items()},
    '@evs':{S(k):(2 if k=='DEFENSE' else 0) for k in cocoon_stats},
    '@base_exp':95, '@catch_rate':120, '@abilities':[S('SHELLARMOR')],
    '@hidden_abilities':[], '@moves':[[lv,S(m)] for lv,m in cocoon_moves],
    '@tutor_moves':[S(m) for m in cocoon_tutors], '@egg_moves':[],
    '@wild_item_common':[], '@wild_item_uncommon':[], '@wild_item_rare':[],
    '@height':7, '@weight':120, '@color':S('Blue'),
    '@evolutions':[[S('WURMPLE'),S('Cascoon'),10,True]],
    '@flags':['DefaultForm_0'], '@generation':0, '@pbs_file_suffix':'glaciverm'
})
species[S('FROSTCOON')] = cocoon
(G / 'Data/species.dat').write_bytes(writes(species))

def flat(values):
    return ','.join(str(v).lstrip(':') for v in values)

def pbs(data):
    a = data.attributes
    stat_order = ['HP','ATTACK','DEFENSE','SPEED','SPECIAL_ATTACK','SPECIAL_DEFENSE']
    lines = [f"[{str(a['@id']).lstrip(':')}]", f"Name = {a['@real_name']}",
             'Types = '+flat(a['@types']),
             'BaseStats = '+flat([a['@base_stats'][S(k)] for k in stat_order]),
             'GenderRatio = Female50Percent', 'GrowthRate = Medium',
             f"BaseExp = {a['@base_exp']}", 'EVs = DEFENSE,2',
             f"CatchRate = {a['@catch_rate']}", 'Happiness = 50',
             'Abilities = '+flat(a['@abilities']),
             'Moves = '+flat([v for pair in a['@moves'] for v in pair]),
             'TutorMoves = '+flat(a['@tutor_moves']), 'EggGroups = Bug', 'HatchSteps = 3840',
             f"Height = {a['@height']/10:.1f}", f"Weight = {a['@weight']/10:.1f}",
             'Color = '+str(a['@color']).lstrip(':'), 'Shape = '+str(a['@shape']).lstrip(':'),
             'Habitat = Forest', 'Category = '+a['@real_category'],
             'Pokedex = '+a['@real_pokedex_entry'], 'Generation = 0', 'Flags = DefaultForm_0']
    return '\n'.join(lines)+'\n'

(G / 'PBS/pokemon_glaciverm.txt').write_text(
    '# Regional Wurmple branches. Nivalora final evolution is appended below.\n'
    +pbs(glaci)+'\n'+pbs(cocoon), encoding='utf-8-sig')
metrics = loads((G / 'Data/species_metrics.dat').read_bytes())
metric_text = ''
for name,source in [('GLACIVERM','WURMPLE'), ('FROSTCOON','SILCOON')]:
    m = clone(metrics[S(source)])
    m.attributes.update({'@id':S(name),'@species':S(name),'@form':0,'@pbs_file_suffix':'glaciverm'})
    metrics[S(name)] = m
    a=m.attributes
    metric_text += f'[{name}]\nBackSprite = '+flat(a['@back_sprite'])+'\nFrontSprite = '+flat(a['@front_sprite'])+f"\nFrontSpriteAltitude = {a['@front_sprite_altitude']}\nShadowX = {a['@shadow_x']}\nShadowSize = {a['@shadow_size']}\n\n"
    shutil.copy2(G/f'Audio/SE/Cries/{source}.ogg', G/f'Audio/SE/Cries/{name}.ogg')
(G / 'Data/species_metrics.dat').write_bytes(writes(metrics))
(G / 'PBS/pokemon_metrics_glaciverm.txt').write_text(metric_text)
import runpy
runpy.run_path(str(G/'Development/Art/Frostcoon/recolour.py'))
print('Glaciverm retained; Frostcoon built: Bug/Ice, BST 350, Shell Armor; Nivalora follows.')

runpy.run_path(str(G/'Development/rebuild_nivalora_data.py'))
