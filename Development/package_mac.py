"""Build the native Mac distribution with only Python's standard library.

Run: python3 Development/package_mac.py /path/to/output
The checked-in upstream template supplies Ruby, SDL and native dependencies.
No downloads, Homebrew or local compilation are needed.
"""
from pathlib import Path
import hashlib, json, os, plistlib, shutil, stat, sys, zipfile

GAME = Path(__file__).resolve().parent.parent
VERSION = '0.8.3'
TEMPLATE = GAME / 'Runtime/macOS/mkxp-z-826929e.zip'

def extract_bundle(archive, destination):
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            relative = Path(entry.filename)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe archive path')
            if '__MACOSX' in relative.parts:
                continue
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = entry.external_attr >> 16
            if entry.is_dir():
                path.mkdir(exist_ok=True)
            elif stat.S_ISLNK(mode):
                target = z.read(entry).decode()
                if not (path.parent / target).resolve().is_relative_to(destination.resolve()):
                    raise ValueError('Symlink leaves bundle')
                path.symlink_to(target)
            else:
                path.write_bytes(z.read(entry))
                path.chmod(mode & 0o777 or 0o644)

def archive_tree(folder, destination):
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(folder.rglob('*')):
            name = str(path.relative_to(folder.parent))
            if path.is_symlink():
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(info, os.readlink(path))
            elif path.is_file():
                z.write(path, name)
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None

def build(output):
    output.mkdir(parents=True, exist_ok=True)
    stage = output / ('Tidebound_Mac_' + VERSION)
    if stage.exists():
        raise FileExistsError('Choose a clean output folder; existing builds are preserved.')
    stage.mkdir()
    extract_bundle(TEMPLATE, stage)
    app = stage / 'Tidebound.app'
    (stage / 'Z-universal.app').rename(app)
    contents = app / 'Contents'
    target = contents / 'Game'
    target.mkdir(exist_ok=True)
    for name in ['Data', 'Audio', 'Graphics', 'Fonts', 'Plugins']:
        if (GAME / name).exists():
            shutil.copytree(GAME / name, target / name)
    for name in ['Game.ini', 'mkxp.json', 'soundfont.sf2']:
        shutil.copy2(GAME / name, target / name)
    # Binary and dependencies are unchanged. The Intel slice is unsigned upstream.
    plist_path = contents / 'Info.plist'
    plist = plistlib.loads(plist_path.read_bytes())
    plist.update(CFBundleName='Tidebound', CFBundleDisplayName='Tidebound',
                 CFBundleIdentifier='game.tidebound.opening',
                 CFBundleShortVersionString=VERSION, CFBundleVersion='37')
    plist_path.write_bytes(plistlib.dumps(plist))
    executable = contents / 'MacOS' / plist['CFBundleExecutable']
    executable.chmod(0o755)
    shutil.copy2(GAME / 'MAC_README.txt', stage / 'READ_ME_FIRST.txt')
    shutil.copy2(GAME / 'CREDITS.md', stage / 'CREDITS.md')
    shutil.copy2(GAME / 'Runtime/macOS/PROVENANCE.md', app / 'RUNTIME_SOURCE.md')
    # Keep the rebuild recipe and source offer with the binary distribution.
    source = GAME / 'Runtime/macOS/mkxp-z-826929e-source.tar.gz'
    if source.exists():
        shutil.copy2(source, stage / source.name)
    script_hash = hashlib.sha256((target / 'Data/Scripts.rxdata').read_bytes()).hexdigest()
    manifest = {'version': VERSION, 'runtime_commit': '826929eeb3ebc4b887c011604919217a790770f4',
                'macos_target': 'Intel Monterey 12.7.5',
                'agent_native_mac_playtest': False,
                'scripts_sha256': script_hash,
                'save_directory_name': 'Tidebound_Opening_0_2'}
    (stage / 'BUILD.json').write_text(json.dumps(manifest, indent=2) + '\n')
    archive = output / (stage.name + '.zip')
    archive_tree(stage, archive)
    print(archive)
    print('SHA256', hashlib.sha256(archive.read_bytes()).hexdigest())
    return archive

if __name__ == '__main__':
    build(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else GAME.parent / 'Mac_Build')
