"""Package the pinned Linux x86_64 runtime without executing it on the host."""
from pathlib import Path
import argparse
import json
import shutil
import struct
import subprocess
import sys
import tempfile

from package_mac import GAME_DIRS, GAME_FILES, archive_tree, extract_bundle, game_hashes
from release_tools import ROOT, SAVE_DIRECTORY, check_sources, sha256, source_revision

RUNTIME_ENTRIES = ('mkxp-z.x86_64', 'lib64', 'stdlib', 'LICENSE.mkxp-z-with-https.txt')
LAUNCHER = '#!/bin/sh\nset -eu\ncd -- "$(dirname -- "$0")"\nexec ./mkxp-z.x86_64 "$@"\n'


def inspect_runtime(runtime):
    images = []
    for path in sorted(runtime.rglob('*')):
        if not path.is_file():
            continue
        with path.open('rb') as stream:
            header = stream.read(64)
        if header[:4] != b'\x7fELF':
            continue
        if (len(header) < 64 or header[4:7] != b'\x02\x01\x01' or
                struct.unpack_from('<H', header, 18)[0] != 62):
            raise ValueError('Expected Linux x86_64 ELF image: ' + str(path))
        images.append(path.relative_to(runtime).as_posix())
    required = {'mkxp-z.x86_64', 'lib64/libruby.so.3.1', 'lib64/libcrypt.so.1', 'lib64/libbsd.so.0'}
    if set(images) != required:
        raise ValueError('Expected the four pinned Linux ELF images')
    return images


def build(output, root=ROOT, allow_dirty=False):
    output = output.resolve()
    if output.exists():
        raise FileExistsError('Choose a new output directory; existing builds are never overwritten')
    config = check_sources(root)
    revision = source_revision(root, allow_dirty)
    relative = Path(config['linux_runtime_archive'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe Linux runtime path')
    runtime_archive = root / relative
    if sha256(runtime_archive) != config['linux_runtime_sha256']:
        raise ValueError('Linux runtime provenance hash mismatch')
    if config['linux_architecture'] != 'x86_64':
        raise ValueError('The supported Linux runtime is x86_64')
    subprocess.run([sys.executable, str(root / 'Development/validate_maps.py')], cwd=root, check=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.tidebound-linux-', dir=output.parent) as temp:
        artifacts = Path(temp) / 'artifacts'
        artifacts.mkdir()
        runtime = Path(temp) / 'runtime'
        runtime.mkdir()
        extract_bundle(runtime_archive, runtime)
        images = inspect_runtime(runtime)
        stage = artifacts / ('Tidebound_Linux_' + config['version'] + '_x86_64')
        stage.mkdir()
        expected = {}

        def copy(source, name):
            if source.is_dir():
                expected.update({name + '/' + p: h for p, h in game_hashes(source).items()})
                shutil.copytree(source, stage / name)
            else:
                expected[name] = sha256(source)
                shutil.copy2(source, stage / name)

        for name in RUNTIME_ENTRIES:
            copy(runtime / name, name)
        for name in GAME_DIRS:
            if (root / name).exists():
                copy(root / name, name)
        for name in (*GAME_FILES, 'CREDITS.md'):
            copy(root / name, name)
        copy(root / 'LINUX_README.txt', 'READ_ME_FIRST.txt')
        copy(root / 'Runtime/Linux/PROVENANCE.md', 'RUNTIME_SOURCE.md')
        copy(root / config['runtime_source'], Path(config['runtime_source']).name)
        (stage / 'Tidebound.sh').write_text(LAUNCHER, encoding='utf-8')
        expected['Tidebound.sh'] = sha256(stage / 'Tidebound.sh')
        for name in ('Tidebound.sh', 'mkxp-z.x86_64'):
            (stage / name).chmod(0o755)
        if game_hashes(stage) != expected:
            raise ValueError('Packaged Linux files differ from source')
        manifest = {'version': config['version'], 'platform': 'linux', 'architecture': 'x86_64',
                    'glibc_minimum': config['linux_glibc_minimum'], 'source': revision,
                    'runtime_commit': config['runtime_commit'], 'runtime_sha256': config['linux_runtime_sha256'],
                    'runtime_source_sha256': config['runtime_source_sha256'], 'native_images': images,
                    'save_directory_name': SAVE_DIRECTORY, 'files_sha256': dict(expected)}
        text = json.dumps(manifest, indent=2) + '\n'
        (stage / 'BUILD.json').write_text(text, encoding='utf-8')
        expected['BUILD.json'] = sha256(stage / 'BUILD.json')
        archive = artifacts / (stage.name + '.zip')
        archive_tree(stage, archive)
        unpacked = Path(temp) / 'roundtrip'
        unpacked.mkdir()
        extract_bundle(archive, unpacked)
        restored = unpacked / stage.name
        if game_hashes(restored) != expected:
            raise ValueError('Linux ZIP roundtrip changed packaged files')
        for name in ('Tidebound.sh', 'mkxp-z.x86_64'):
            if restored.joinpath(name).stat().st_mode & 0o777 != 0o755:
                raise ValueError('Linux ZIP lost executable permissions')
        if source_revision(root, allow_dirty) != revision:
            raise ValueError('Source changed while the Linux package was being built')
        shutil.rmtree(stage)
        (artifacts / 'LINUX_BUILD.json').write_text(text, encoding='utf-8')
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
