"""Platform-neutral ZIP safety, filesystem copying and content verification."""
from pathlib import Path
import os
import shutil
import stat
import unicodedata
import zipfile

from tidebound_dev.release.metadata import sha256

GAME_DIRS = ('Data', 'Audio', 'Graphics', 'Fonts', 'Plugins')
GAME_FILES = ('Game.ini', 'mkxp.json', 'soundfont.sf2')


def extract_bundle(archive, destination):
    with zipfile.ZipFile(archive) as z:
        seen = set()
        for entry in z.infolist():
            relative = Path(entry.filename)
            if relative.is_absolute() or '..' in relative.parts or '\\' in entry.filename:
                raise ValueError('Unsafe archive path')
            if '__MACOSX' in relative.parts:
                continue
            if relative in seen:
                raise ValueError('Duplicate archive path')
            seen.add(relative)
            path = destination / relative
            if not path.resolve().is_relative_to(destination.resolve()):
                raise ValueError('Archive entry leaves destination through a symlink')
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = entry.external_attr >> 16
            if entry.is_dir():
                path.mkdir(exist_ok=True)
            elif stat.S_ISLNK(mode):
                target = z.read(entry).decode('utf-8')
                if Path(target).is_absolute() or not (path.parent / target).resolve().is_relative_to(destination.resolve()):
                    raise ValueError('Symlink leaves bundle')
                path.symlink_to(target)
            else:
                path.write_bytes(z.read(entry))
                path.chmod(mode & 0o777 or 0o644)


def archive_tree(folder, destination):
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(folder.rglob('*')):
            name = path.relative_to(folder.parent).as_posix()
            if path.is_symlink():
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(info, os.readlink(path))
            elif path.is_file():
                z.write(path, name)
    with zipfile.ZipFile(destination) as z:
        if z.testzip() is not None:
            raise ValueError('Built ZIP failed its integrity check')


def game_hashes(folder, normalization=None):
    hashes = {}
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            name = path.relative_to(folder).as_posix()
            if normalization:
                name = unicodedata.normalize(normalization, name)
            if name in hashes:
                raise ValueError('Unicode-equivalent game paths: ' + name)
            hashes[name] = sha256(path)
    return hashes


def copy_verified(source, destination):
    """Compare with the source snapshot before accepting a staged copy."""
    if source.is_dir():
        expected = game_hashes(source, 'NFC')
        shutil.copytree(source, destination)
        actual = game_hashes(destination, 'NFC')
    else:
        expected = sha256(source)
        shutil.copy2(source, destination)
        actual = sha256(destination)
    if actual != expected:
        raise ValueError(f'Packaged files differ from source: {source}')


def copy_game(source, destination):
    for name in GAME_DIRS:
        if (source / name).exists():
            copy_verified(source / name, destination / name)
    for name in GAME_FILES:
        copy_verified(source / name, destination / name)
