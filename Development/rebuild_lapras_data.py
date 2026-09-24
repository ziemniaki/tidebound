"""Add the pier's Water/Ghost Lapras form; retain ordinary Lapras and owned forms."""
from pathlib import Path
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S

G = Path(__file__).resolve().parent.parent
species = loads((G / 'Data/species.dat').read_bytes())
form = loads(writes(species[S('LAPRAS')]))
form.attributes.update({
    '@id': S('LAPRAS_1'), '@species': S('LAPRAS'), '@form': 1,
    '@pokedex_form': 1, '@real_form_name': 'Tidebound',
    '@types': [S('WATER'), S('GHOST')], '@color': S('White'),
    '@pbs_file_suffix': 'tidebound_lapras'
})
species[S('LAPRAS_1')] = form
(G / 'Data/species.dat').write_bytes(writes(species))
(G / 'PBS/pokemon_forms_tidebound_lapras.txt').write_text(
    '# The pale pier apparition. Other fields inherit ordinary Lapras.\n'
    '[LAPRAS,1]\nFormName = Tidebound\nTypes = WATER,GHOST\nColor = White\n',
    encoding='utf-8-sig'
)
print('Built Lapras form 1: Water/Ghost; ordinary Lapras and inherited balance retained.')
