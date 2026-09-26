"""Linux x86_64 layout, pinned ELF images and launcher permissions."""
from pathlib import Path
import struct
import tempfile

from release_tools import sha256
from .archives import copy_verified, extract_bundle
from .model import Player

NAME = 'Linux'
ARCHITECTURE = 'x86_64'
MANIFEST = 'LINUX_BUILD.json'
RUNTIME_ENTRIES = ('mkxp-z.x86_64', 'lib64', 'stdlib', 'LICENSE.mkxp-z-with-https.txt')
LAUNCHER = '#!/bin/sh\nset -eu\nlauncher=$(readlink -f -- "$0")\ncd -- "$(dirname -- "$launcher")"\nexec ./mkxp-z.x86_64 "$@"\n'


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


def prepare(folder, root, config, development):
    relative = Path(config['linux_runtime_archive'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe Linux runtime path')
    archive = root / relative
    if sha256(archive) != config['linux_runtime_sha256']:
        raise ValueError('Linux runtime provenance hash mismatch')
    if config['linux_architecture'] != 'x86_64':
        raise ValueError('The supported Linux runtime is x86_64')
    with tempfile.TemporaryDirectory(prefix='.runtime-', dir=folder.parent) as temp:
        runtime = Path(temp)
        extract_bundle(archive, runtime)
        images = inspect_runtime(runtime)
        for name in RUNTIME_ENTRIES:
            copy_verified(runtime / name, folder / name)
    copy_verified(root / 'docs/runtime/Linux.md', folder / 'RUNTIME_SOURCE.md')
    source = root / config['runtime_source']
    copy_verified(source, folder / source.name)
    (folder / 'Tidebound.sh').write_text(LAUNCHER, encoding='utf-8')
    return Player(folder, folder, folder / 'Tidebound.sh', {
        'platform': 'linux',
        'architecture': 'x86_64',
        'glibc_minimum': config['linux_glibc_minimum'],
        'runtime_commit': config['runtime_commit'],
        'runtime_sha256': config['linux_runtime_sha256'],
        'runtime_source_sha256': config['runtime_source_sha256'],
        'native_images': images,
    })


def finalize(player):
    for name in ('Tidebound.sh', 'mkxp-z.x86_64'):
        (player.folder / name).chmod(0o755)


def verify_roundtrip(folder):
    for name in ('Tidebound.sh', 'mkxp-z.x86_64'):
        if (folder / name).stat().st_mode & 0o777 != 0o755:
            raise ValueError('Linux ZIP lost executable permissions')
