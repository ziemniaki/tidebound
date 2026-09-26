"""Embed the manifest's Ruby files and the explicit Essentials adaptations."""
from pathlib import Path
import zlib

from rubymarshal.reader import loads
from rubymarshal.writer import writes

from engine_patches import patch_engine
from script_archive import reject_plugin_copy, script_name, source_files, source_name
from release_tools import load_release


def rebuild(root):
    game = root / 'game'
    source_root = root / 'src'
    reject_plugin_copy(game)
    sources = source_files(source_root)
    archive = game / 'Data/Scripts.rxdata'
    stock = [entry for entry in loads(archive.read_bytes())
             if not script_name(entry[1]).startswith('Tidebound/')]
    entries = patch_engine(stock, load_release(root)['version'])
    main = next(i for i, entry in enumerate(entries) if entry[1] == 'Main')
    custom = [[260908100 + i, source_name(path, source_root),
               zlib.compress(path.read_text(encoding='utf-8').encode('utf-8'), 9)]
              for i, path in enumerate(sources)]
    entries[main:main] = custom
    archive.write_bytes(writes(entries))
    print(f'Embedded {len(custom)} Tidebound scripts into {len(entries)} entries.')


if __name__ == '__main__':
    rebuild(Path(__file__).resolve().parent.parent)
