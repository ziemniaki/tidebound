"""Universal Mac layout, Unicode normalization and signing."""
import plistlib
import unicodedata

from tidebound_dev.runtime.mac import inspect_runtime, sign_app, run
from .archives import copy_verified, extract_bundle, game_hashes
from .model import Player

NAME = 'Mac'
ARCHITECTURE = 'universal'
MANIFEST = 'BUILD.json'

def normalize_bundle_names(app):
    """Use decomposed names before signing, matching Finder's ZIP extraction.

    Code signatures compare filename bytes, even on normalization-insensitive
    APFS. An NFC filename such as Rout\u00e9 1.mid otherwise becomes an invalid
    sealed resource when Archive Utility extracts it as Route\u0301 1.mid.
    """
    paths = list(app.rglob('*'))
    seen = set()
    for path in paths:
        name = unicodedata.normalize('NFD', path.relative_to(app).as_posix())
        if name in seen:
            raise ValueError('Unicode-equivalent bundle paths: ' + name)
        seen.add(name)
    # Rename children before their parents so all original paths stay usable.
    for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
        name = unicodedata.normalize('NFD', path.name)
        if name != path.name:
            path.rename(path.with_name(name))


def prepare(folder, root, config, development):
    extract_bundle(root / config['runtime_archive'], folder)
    app = folder / 'Tidebound.app'
    (folder / 'Z-universal.app').rename(app)
    images = inspect_runtime(app, config['architectures'])
    contents = app / 'Contents'
    # macOS requires this upstream license inside the signed resources.
    (app / 'LICENSE.mkxp-z-with-https.txt').rename(contents / 'Resources/LICENSE.mkxp-z-with-https.txt')
    game = contents / 'Game'
    game.mkdir(exist_ok=True)
    plist_path = contents / 'Info.plist'
    plist = plistlib.loads(plist_path.read_bytes())
    plist.update(
        CFBundleName='Tidebound Dev' if development else 'Tidebound',
        CFBundleDisplayName='Tidebound Dev' if development else 'Tidebound',
        CFBundleIdentifier='game.tidebound.development' if development else 'game.tidebound.opening',
        CFBundleShortVersionString=config['version'],
        CFBundleVersion=config['mac_build'],
        LSMinimumSystemVersionByArchitecture={'x86_64': '10.13', 'arm64': '11.0'},
    )
    plist_path.write_bytes(plistlib.dumps(plist))
    (contents / 'MacOS' / plist['CFBundleExecutable']).chmod(0o755)
    copy_verified(root / 'docs/runtime/macOS.md', contents / 'Resources/RUNTIME_SOURCE.md')
    source = root / config['runtime_source']
    copy_verified(source, folder / source.name)
    return Player(folder, game, app, {
        'mac_build': config['mac_build'],
        'runtime_commit': config['runtime_commit'],
        'runtime_sha256': config['runtime_sha256'],
        'runtime_patch_sha256': config['runtime_patch_sha256'],
        'architectures': config['architectures'],
        'signing': 'ad-hoc',
        'notarized': False,
        'native_images': images,
    })


def finalize(player):
    expected = game_hashes(player.game, 'NFC')
    normalize_bundle_names(player.launcher)
    if game_hashes(player.game, 'NFC') != expected:
        raise ValueError('Filename normalization changed game files')
    sign_app(player.launcher)


def verify_roundtrip(folder):
    app = folder / 'Tidebound.app'
    normalize_bundle_names(app)
    run('codesign', '--verify', '--deep', '--strict', '--all-architectures', str(app))
