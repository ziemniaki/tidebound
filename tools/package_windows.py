"""Package the pinned Windows x64 runtime and game into a verified player ZIP."""
from pathlib import Path
import argparse
import json
import shutil
import struct
import subprocess
import sys
import tempfile

from package_mac import GAME_DIRS, GAME_FILES, archive_tree, extract_bundle, game_hashes
from runtime_inputs import windows_runtime
from release_tools import ROOT, SAVE_DIRECTORY, check_sources, sha256, source_revision

RUNTIME_FILES = ('Game.exe', 'x64-msvcrt-ruby310.dll', 'zlib1.dll')


def inspect_runtime(root, config):
    hashes = config['windows_runtime_sha256']
    if set(hashes) != set(RUNTIME_FILES):
        raise ValueError('Windows runtime manifest must pin the executable and both DLLs')
    for name in RUNTIME_FILES:
        path = root / name
        if sha256(path) != hashes[name]:
            raise ValueError(f'Windows runtime provenance hash mismatch: {name}')
        data = path.read_bytes()
        if len(data) < 64 or data[:2] != b'MZ':
            raise ValueError(f'Invalid Windows executable: {name}')
        offset = struct.unpack_from('<I', data, 0x3c)[0]
        if (data[offset:offset + 4] != b'PE\0\0' or
                data[offset + 4:offset + 6] != b'\x64\x86' or
                data[offset + 24:offset + 26] != b'\x0b\x02'):
            raise ValueError(f'Expected a Windows x64 PE32+ image: {name}')
    return hashes


def build(output, root=ROOT, allow_dirty=False):
    output = output.resolve()
    if output.exists():
        raise FileExistsError('Choose a new output directory; existing builds are never overwritten')
    game = root / "game"
    config = check_sources(root)
    revision = source_revision(root, allow_dirty)
    runtime_dir = windows_runtime(root, config)
    runtime = inspect_runtime(runtime_dir, config)
    subprocess.run([sys.executable, str(root / 'tools/validate_maps.py')], cwd=root, check=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.tidebound-windows-', dir=output.parent) as temp:
        artifacts = Path(temp) / 'artifacts'
        artifacts.mkdir()
        stage = artifacts / ('Tidebound_Windows_' + config['version'] + '_x64')
        stage.mkdir()
        expected = {}
        for name in GAME_DIRS:
            if (game / name).exists():
                expected.update({name + '/' + p: h for p, h in game_hashes(game / name).items()})
                shutil.copytree(game / name, stage / name)
        for name in GAME_FILES:
            expected[name] = sha256(game / name)
            shutil.copy2(game / name, stage / name)
        for name in RUNTIME_FILES:
            expected[name] = sha256(runtime_dir / name)
            shutil.copy2(runtime_dir / name, stage / name)
        for source, dest in (( 'docs/credits.md', 'CREDITS.md'), ('docs/players/windows.txt', 'README.txt'),
                             ('docs/runtime/Windows.md', 'RUNTIME_SOURCE.md')):
            expected[dest] = sha256(root / source)
            shutil.copy2(root / source, stage / dest)
        if game_hashes(stage) != expected:
            raise ValueError('Packaged Windows files differ from source')
        manifest = {'version': config['version'], 'platform': 'windows', 'architecture': 'x86_64',
                    'source': revision, 'runtime_sha256': runtime, 'signing': 'unchanged upstream binaries',
                    'save_directory_name': SAVE_DIRECTORY, 'files_sha256': expected}
        manifest_text = json.dumps(manifest, indent=2) + '\n'
        (stage / 'BUILD.json').write_text(manifest_text, encoding='utf-8')
        expected['BUILD.json'] = sha256(stage / 'BUILD.json')
        archive = artifacts / (stage.name + '.zip')
        archive_tree(stage, archive)
        unpacked = Path(temp) / 'roundtrip'
        unpacked.mkdir()
        extract_bundle(archive, unpacked)
        if game_hashes(unpacked / stage.name) != expected:
            raise ValueError('Windows ZIP roundtrip changed packaged files')
        if source_revision(root, allow_dirty) != revision:
            raise ValueError('Source changed while the Windows package was being built')
        shutil.rmtree(stage)
        (artifacts / 'WINDOWS_BUILD.json').write_text(manifest_text, encoding='utf-8')
        (artifacts / 'SHA256SUMS.txt').write_text(
            ''.join(sha256(p) + '  ' + p.name + '\n' for p in sorted(artifacts.iterdir())), encoding='utf-8')
        artifacts.rename(output)
    result = output / archive.name
    print(result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--allow-dirty', action='store_true', help='Local preview only')
    args = parser.parse_args()
    build(args.output, allow_dirty=args.allow_dirty)
