"""Prepare disposable native fixtures without touching player data or source archives."""
from pathlib import Path
import re
import shutil
import zlib

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.release.metadata import parse_runtime_config

SCENARIOS = ('runtime', 'world', 'species', 'all')


def prepare(game, namespace, scenario='all'):
    if scenario not in SCENARIOS:
        raise ValueError(f'Unknown native scenario: {scenario}')
    if not re.fullmatch(r'Tidebound_Build_Smoke_[a-f0-9]{32}', namespace):
        raise ValueError('Native fixtures require a unique test namespace')
    config = game / 'mkxp.json'
    text, count = re.subn(r'"dataPathApp"\s*:\s*"[^"]+"',
                         '"dataPathApp": "' + namespace + '"', config.read_text(encoding='utf-8'))
    if count != 1:
        raise ValueError('Expected exactly one save namespace setting before launch')
    if parse_runtime_config(text).get('dataPathApp') != namespace:
        raise ValueError('Save namespace was not isolated before launch')
    scripts = game / 'Data/Scripts.rxdata'
    entries = loads(scripts.read_bytes())
    main = [entry for entry in entries if entry[1] == 'Main']
    if len(main) != 1:
        raise ValueError('Expected exactly one Main entry')
    tests = Path(__file__).parent
    driver = f'TIDEBOUND_NATIVE_SCENARIO = :{scenario}\n'.encode()
    driver += (tests / 'native_scenarios.rb').read_bytes()
    driver += b'\n' + (tests / 'native_runtime_smoke.rb').read_bytes()
    main[0][2] = zlib.compress(driver)
    # Validate both files before publishing either change in this disposable copy.
    encoded = writes(entries)
    if scenario in ('species', 'all'):
        shutil.copytree(tests.parent / 'game/PBS', game / 'NativePBS')
    config.write_text(text, encoding='utf-8')
    scripts.write_bytes(encoded)
