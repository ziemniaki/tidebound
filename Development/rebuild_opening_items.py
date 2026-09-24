"""Keep the opening Key Item's PBS and compiled definition in agreement."""
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
G=Path(__file__).resolve().parent.parent
items=loads((G/'Data/items.dat').read_bytes())
key=loads(writes(items[Symbol('TOWNMAP')]))
key.attributes.update({'@id':Symbol('TIDEBOUNDOILKEYS'), '@real_name':'Oil-Shop Keys',
 '@real_name_plural':'Oil-Shop Keys', '@real_portion_name':'', '@real_portion_name_plural':'',
 '@pocket':8, '@price':0, '@sell_price':0, '@field_use':0, '@battle_use':0,
 '@flags':['KeyItem'], '@consumable':False,
 '@real_description':'Old brass keys found beneath white flowers. The oil seller in Shiohama is looking for them.'})
items[Symbol('TIDEBOUNDOILKEYS')]=key
(G/'Data/items.dat').write_bytes(writes(items))
p=G/'PBS/items.txt';s=p.read_text(encoding='utf-8-sig')
s=s.split('# TIDEBOUND OPENING ITEMS')[0].rstrip()+'''

# TIDEBOUND OPENING ITEMS
#-------------------------------
[TIDEBOUNDOILKEYS]
Name = Oil-Shop Keys
NamePlural = Oil-Shop Keys
Pocket = 8
Price = 0
Flags = KeyItem
Consumable = false
Description = Old brass keys found beneath white flowers. The oil seller in Shiohama is looking for them.
'''
p.write_text(s,encoding='utf-8-sig')
print('Updated Oil-Shop Keys in PBS and compiled item data.')
