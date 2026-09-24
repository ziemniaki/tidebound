"""Called after rebuilding regional Sunkern/Moonkern. Adds the final evolution."""
from pathlib import Path
import re,shutil
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S
G=Path(__file__).resolve().parent.parent
species=loads((G/'Data/species.dat').read_bytes())
moon=species[S('MOONKERN')]
moon.attributes['@evolutions']=[[S('SUNKERN'),S('Level'),14,True],[S('MOONFLORA'),S('Level'),20,False]]
f=loads(writes(moon));stats={'HP':75,'ATTACK':50,'DEFENSE':80,'SPEED':60,'SPECIAL_ATTACK':115,'SPECIAL_DEFENSE':110}
moves=[(0,'SHADOWBALL'),(1,'HEX')]+[(lv,str(m).lstrip(':')) for lv,m in moon.attributes['@moves'] if lv!=0]
moves=sorted([(23 if m=='WILLOWISP' else lv,'NASTYPLOT' if lv==31 else m) for lv,m in moves])
valid=loads((G/'Data/moves.dat').read_bytes())
assert all(S(m) in valid for _,m in moves)
entry='The flower it longed to become appears only as a spirit. Its hollow face turns towards an absent sun, weary eyes burning with a quiet resentment.'
f.attributes.update({'@id':S('MOONFLORA'),'@species':S('MOONFLORA'),'@real_name':'Moonflora','@real_category':'Phantom Bloom','@real_pokedex_entry':entry,'@base_stats':{S(k):v for k,v in stats.items()},'@base_exp':210,'@catch_rate':45,'@evs':{S(k):(3 if k=='SPECIAL_ATTACK' else 0) for k in stats},'@moves':[[lv,S(m)] for lv,m in moves],'@evolutions':[[S('MOONKERN'),S('Level'),20,True]],'@height':11,'@shape':species[S('SUNFLORA')].attributes['@shape']})
species[S('MOONFLORA')]=f
(G/'Data/species.dat').write_bytes(writes(species))
p=G/'PBS/pokemon_tidebound.txt'
text=p.read_text(encoding='utf-8-sig').split('# MOONFLORA GENERATED')[0]
text=re.sub(r'^Evolutions = MOONFLORA,Level,20\n','',text,flags=re.M).rstrip()+'\nEvolutions = MOONFLORA,Level,20\n'
text+='\n# MOONFLORA GENERATED\n[MOONFLORA]\nName = Moonflora\nTypes = GRASS,GHOST\nBaseStats = 75,50,80,60,115,110\nGenderRatio = Female50Percent\nGrowthRate = Parabolic\nBaseExp = 210\nEVs = SPECIAL_ATTACK,3\nCatchRate = 45\nHappiness = 50\nAbilities = INSOMNIA,INFILTRATOR\nHiddenAbilities = CURSEDBODY\n'
text+='Moves = '+','.join(str(x) for pair in moves for x in pair)+'\nTutorMoves = '+','.join(str(m).lstrip(':') for m in f.attributes['@tutor_moves'])+'\nEggGroups = Grass\nHatchSteps = 5120\nHeight = 1.1\nWeight = 0.1\nColor = Gray\nShape = '+str(f.attributes['@shape']).lstrip(':')+'\nHabitat = Grassland\nCategory = Phantom Bloom\nPokedex = '+entry+'\nGeneration = 0\nFlags = DefaultForm_0\n'
p.write_text(text,encoding='utf-8-sig')
metrics=loads((G/'Data/species_metrics.dat').read_bytes());fm=loads(writes(metrics[S('MOONKERN')]))
fm.attributes.update({'@id':S('MOONFLORA'),'@species':S('MOONFLORA'),'@front_sprite':[0,18],'@back_sprite':[0,0]})
metrics[S('MOONFLORA')]=fm;(G/'Data/species_metrics.dat').write_bytes(writes(metrics))
p=G/'PBS/pokemon_metrics_tidebound.txt';text=p.read_text().split('[MOONFLORA]')[0].rstrip()+'\n\n[MOONFLORA]\nBackSprite = 0,0\nFrontSprite = 0,18\nFrontSpriteAltitude = 6\nShadowX = 0\nShadowSize = 0\n';p.write_text(text)
shutil.copy2(G/'Audio/SE/Cries/SUNFLORA.ogg',G/'Audio/SE/Cries/MOONFLORA.ogg')
print('Moonflora built: regional Sunkern -> 14 Moonkern -> 20 Moonflora; BST 490.')
