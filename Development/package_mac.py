"""Stage, verify and atomically expose a universal Mac development build.

Requires macOS and Xcode command-line tools. Use --allow-dirty only for previews;
release CI always packages a clean commit. Ad-hoc signing is not notarization.
"""
from pathlib import Path
import argparse
import json
import os
import plistlib
import shutil
import stat
import tempfile
import zipfile

from mac_runtime import inspect_runtime, sign_app
from release_tools import ROOT, SAVE_DIRECTORY, check_sources, sha256, source_revision

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


def game_hashes(folder):
    return {p.relative_to(folder).as_posix(): sha256(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def build(output, root=ROOT, allow_dirty=False):
    output = output.resolve()
    if output.exists():
        raise FileExistsError('Choose a new output directory; existing builds are never overwritten')
    config = check_sources(root)
    revision = source_revision(root, allow_dirty)
    # Validate maps as well as the embedded Ruby before packaging any game files.
    import subprocess
    import sys
    subprocess.run([sys.executable, str(root / 'Development/validate_maps.py')], cwd=root, check=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.tidebound-package-', dir=output.parent) as temp:
        artifacts = Path(temp) / 'artifacts'
        artifacts.mkdir()
        stage = artifacts / ('Tidebound_Mac_' + config['version'] + '_universal')
        stage.mkdir()
        extract_bundle(root / config['runtime_archive'], stage)
        app = stage / 'Tidebound.app'
        (stage / 'Z-universal.app').rename(app)
        report = inspect_runtime(app, config['architectures'])
        contents = app / 'Contents'
        # The upstream ZIP places this license at the bundle root, where macOS
        # rejects it as unsealed content. Preserve it in the signed resources.
        (app / 'LICENSE.mkxp-z-with-https.txt').rename(contents / 'Resources/LICENSE.mkxp-z-with-https.txt')
        target = contents / 'Game'
        target.mkdir(exist_ok=True)
        expected = {}
        for name in GAME_DIRS:
            if (root / name).exists():
                expected.update({name + '/' + p: h for p, h in game_hashes(root / name).items()})
                shutil.copytree(root / name, target / name)
        for name in GAME_FILES:
            expected[name] = sha256(root / name)
            shutil.copy2(root / name, target / name)
        if game_hashes(target) != expected:
            raise ValueError('Packaged game files differ from source')
        plist_path = contents / 'Info.plist'
        plist = plistlib.loads(plist_path.read_bytes())
        plist.update(CFBundleName='Tidebound', CFBundleDisplayName='Tidebound',
                     CFBundleIdentifier='game.tidebound.opening',
                     CFBundleShortVersionString=config['version'], CFBundleVersion=config['mac_build'],
                     LSMinimumSystemVersionByArchitecture={'x86_64': '10.13', 'arm64': '11.0'})
        plist_path.write_bytes(plistlib.dumps(plist))
        (contents / 'MacOS' / plist['CFBundleExecutable']).chmod(0o755)
        shutil.copy2(root / 'MAC_README.txt', stage / 'READ_ME_FIRST.txt')
        shutil.copy2(root / 'CREDITS.md', stage / 'CREDITS.md')
        shutil.copy2(root / 'Runtime/macOS/PROVENANCE.md', contents / 'Resources/RUNTIME_SOURCE.md')
        source = root / config['runtime_source']
        shutil.copy2(source, stage / source.name)
        sign_app(app)
        manifest = {'version': config['version'], 'mac_build': config['mac_build'],
                    'source': revision, 'runtime_commit': config['runtime_commit'],
                    'runtime_sha256': config['runtime_sha256'],
                    'architectures': config['architectures'], 'signing': 'ad-hoc', 'notarized': False,
                    'save_directory_name': SAVE_DIRECTORY, 'game_sha256': expected,
                    'native_images': report}
        (stage / 'BUILD.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        archive = artifacts / (stage.name + '.zip')
        archive_tree(stage, archive)
        # The ZIP must preserve signed bundle bytes, links and executable bits.
        unpacked = Path(temp) / 'roundtrip'
        unpacked.mkdir()
        extract_bundle(archive, unpacked)
        roundtrip_app = unpacked / stage.name / 'Tidebound.app'
        if game_hashes(roundtrip_app / 'Contents/Game') != expected:
            raise ValueError('ZIP roundtrip changed game files')
        from mac_runtime import run
        run('codesign', '--verify', '--deep', '--strict', '--all-architectures', str(roundtrip_app))
        shutil.rmtree(stage)
        (artifacts / 'BUILD.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        (artifacts / 'SHA256SUMS.txt').write_text(sha256(archive) + '  ' + archive.name + '\n', encoding='utf-8')
        artifacts.rename(output)
    result = output / archive.name
    print(result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New output directory, exposed only after validation succeeds')
    parser.add_argument('--allow-dirty', action='store_true', help='Local preview only; records source.dirty=true')
    args = parser.parse_args()
    build(args.output, allow_dirty=args.allow_dirty)
