"""Regional forest Wurmple and its native, personality-based level-10 split."""
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S

G = Path(__file__).resolve().parent.parent
species = loads((G / 'Data/species.dat').read_bytes())
form = loads(writes(species[S('WURMPLE')]))
form.attributes.update({
    '@id': S('WURMPLE_1'), '@species': S('WURMPLE'), '@form': 1,
    '@pokedex_form': 1, '@real_form_name': 'Tidebound',
    '@types': [S('BUG'), S('ICE')], '@color': S('Blue'),
    '@pbs_file_suffix': 'tidebound_wurmple',
    '@evolutions': [[S('GLACIVERM'), S('Silcoon'), 10, False],
                    [S('FROSTCOON'), S('Cascoon'), 10, False]]
})
species[S('WURMPLE_1')] = form
(G / 'Data/species.dat').write_bytes(writes(species))
(G / 'PBS/pokemon_forms_tidebound_wurmple.txt').write_text(
    '# Regional Wurmple. Native personality split, both branches at level 10.\n'
    '[WURMPLE,1]\nFormName = Tidebound\nTypes = BUG,ICE\nColor = Blue\n'
    'Evolutions = GLACIVERM,Silcoon,10,FROSTCOON,Cascoon,10\n',
    encoding='utf-8-sig'
)
import runpy
runpy.run_path(str(G / 'Development/rebuild_glaciverm_data.py'))
print('Wurmple form 1 built: native level-10 split to Glaciverm or provisional Frostcoon.')
