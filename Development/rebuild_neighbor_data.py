"""Quest data. Battle rosters use Essentials NPCTrainer and live in 008."""
from pathlib import Path
import shutil
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
G=Path(__file__).resolve().parent.parent
def clone(v):return loads(writes(v))
items=loads((G/'Data/items.dat').read_bytes());text='# Tidebound story items, never healing supplies.\n'
rows=[('TIDEBOUNDPIE','Homemade Pie','A homemade pie on a ceramic plate painted with two blue reeds. A thank-you for you and Mother.','LAVACOOKIE'),('TIDEBOUNDPLATE','Blue-Reed Plate','An ordinary ceramic plate, washed and dried. Two blue reeds decorate its rim. Return it to the oil seller.','SHOALSHELL'),('TIDEBOUNDNECKLACE','Pearl Necklace','A small pearl necklace recovered from the thieves. The oil seller is waiting for it.','PEARLSTRING')]
rows.append(('TIDEBOUNDREEDCHARM','Blue-Reed Keepsake','A small ceramic charm painted with two blue reeds. A gift from the oil seller, to keep.','SHOALSHELL'))
for ident,name,desc,icon in rows:
 data=clone(items[Symbol('TIDEBOUNDOILKEYS')]);data.attributes.update({'@id':Symbol(ident),'@real_name':name,'@real_name_plural':name,'@real_portion_name':name,'@real_portion_name_plural':name,'@real_description':desc,'@pbs_file_suffix':'tidebound_neighbor'});items[Symbol(ident)]=data
 text+=f'\n#-------------------------------\n[{ident}]\nName = {name}\nNamePlural = {name}\nPocket = 8\nPrice = 0\nFlags = KeyItem\nConsumable = false\nDescription = {desc}\n'
 shutil.copy2(G/f'Graphics/Items/{icon}.png',G/f'Graphics/Items/{ident}.png')
(G/'PBS/items_tidebound_neighbor.txt').write_text(text,encoding='utf-8-sig');(G/'Data/items.dat').write_bytes(writes(items))
types=loads((G/'Data/trainer_types.dat').read_bytes());text='# Temporary stock art; no final Team Abyss uniform is established.\n'
for ident,name,base in [('TBLOCALYOUTH','Local Thief','YOUNGSTER'),('TBLOCALYOUTH2','Local Thief','CAMPER'),('TBABYSSRUNNER','Abyss Runner','BURGLAR')]:
 data=clone(types[Symbol(base)]);data.attributes.update({'@id':Symbol(ident),'@real_name':name,'@base_money':0,'@skill_level':0,'@intro_BGM':None,'@battle_BGM':'Tidebound Stillness','@victory_BGM':'Tidebound Stillness','@pbs_file_suffix':'tidebound_neighbor'});types[Symbol(ident)]=data
 text+=f'\n#-------------------------------\n[{ident}]\nName = {name}\nGender = Male\nBaseMoney = 0\nSkillLevel = 0\nBattleBGM = Tidebound Stillness\nVictoryBGM = Tidebound Stillness\n'
 shutil.copy2(G/f'Graphics/Trainers/{base}.png',G/f'Graphics/Trainers/{ident}.png');shutil.copy2(G/f'Graphics/Characters/trainer_{base}.png',G/f'Graphics/Characters/trainer_{ident}.png')
(G/'PBS/trainer_types_tidebound_neighbor.txt').write_text(text,encoding='utf-8-sig');(G/'Data/trainer_types.dat').write_bytes(writes(types))
print('Built four quest Key Items and three trainer classes.')
