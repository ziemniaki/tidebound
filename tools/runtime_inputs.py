"""Restore pinned Windows inputs without downloads or tracked loose binaries."""
from pathlib import Path
import shutil
import tempfile
import zipfile

from release_tools import sha256


def unpack_pinned(root, config, key):
    relative = Path(config[key])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe runtime archive path')
    archive = root / relative
    expected = config[key + '_sha256']
    if sha256(archive) != expected:
        raise ValueError('Windows runtime archive provenance hash mismatch')
    destination = root / '.cache/runtimes' / expected
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or any(Path(n).name != n or '\\' in n for n in names):
            raise ValueError('Runtime archive must contain unique flat filenames')
        # Check cached bytes too: a partially restored or edited cache is rebuilt.
        if destination.is_dir() and all((destination / n).is_file() and
                (destination / n).read_bytes() == z.read(n) for n in names):
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent, prefix='.restore-') as temp:
            stage = Path(temp) / 'runtime'
            stage.mkdir()
            for name in names:
                (stage / name).write_bytes(z.read(name))
            if destination.exists():
                shutil.rmtree(destination)
            stage.rename(destination)
    return destination


def windows_runtime(root, config):
    return unpack_pinned(root, config, 'windows_runtime_archive')
