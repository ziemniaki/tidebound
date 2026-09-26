"""Windows x64 layout and pinned PE image verification."""
import struct

from release_tools import sha256
from runtime_inputs import windows_runtime
from .archives import copy_verified
from .model import Player

NAME = 'Windows'
ARCHITECTURE = 'x64'
MANIFEST = 'WINDOWS_BUILD.json'
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


def prepare(folder, root, config, development):
    runtime = windows_runtime(root, config)
    hashes = inspect_runtime(runtime, config)
    for name in RUNTIME_FILES:
        copy_verified(runtime / name, folder / name)
    copy_verified(root / 'docs/runtime/Windows.md', folder / 'RUNTIME_SOURCE.md')
    return Player(folder, folder, folder / 'Game.exe', {
        'platform': 'windows',
        'architecture': 'x86_64',
        'runtime_sha256': hashes,
        'signing': 'unchanged upstream binaries',
    })


def finalize(player):
    pass


def verify_roundtrip(folder):
    pass
