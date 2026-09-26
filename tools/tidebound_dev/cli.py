"""Small, shared command surface for humans, agents and CI."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
GENERATORS = ('rebuild_maps.py', 'rebuild_opening_items.py', 'rebuild_neighbor_data.py',
              'rebuild_field_data.py', 'rebuild_regional_data.py', 'rebuild_scripts.py', 'configure_game.py')


def run(*args, cwd=ROOT):
    print('+ ' + ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def python(script, *args):
    run(sys.executable, ROOT / script, *args)


def test_dependencies():
    node, npm = shutil.which('node'), shutil.which('npm')
    wanted = (ROOT / '.node-version').read_text().strip()
    if not node or not npm:
        raise ValueError(f'Checks need Node.js {wanted}. Install it, then rerun this command. See docs/development.md.')
    actual = subprocess.check_output([node, '--version'], text=True).strip().lstrip('v')
    if actual != wanted:
        raise ValueError(f'Checks need Node.js {wanted}; found {actual}. See docs/development.md.')
    lock = hashlib.sha256((ROOT / 'tests/package-lock.json').read_bytes()).hexdigest()
    stamp = ROOT / 'tests/node_modules/.tidebound-lock'
    if not stamp.exists() or stamp.read_text() != lock or not (stamp.parent / '@ruby/3.2-wasm-wasi/dist/ruby.wasm').is_file():
        run(npm, 'ci', '--prefix', ROOT / 'tests', '--ignore-scripts')
        stamp.write_text(lock)


def host_platform():
    if sys.platform == 'darwin':
        return 'mac'
    if sys.platform == 'win32':
        return 'windows'
    if sys.platform.startswith('linux') and platform.machine().lower() in ('x86_64', 'amd64'):
        return 'linux'
    raise ValueError('Playable builds support macOS Intel/ARM, Windows x64 and Linux x86_64.')


def development_build(target):
    if target == 'mac' and sys.platform != 'darwin':
        raise ValueError('Mac builds require macOS and Xcode command-line tools.')
    python('tools/rebuild_scripts.py')
    sys.path.insert(0, str(ROOT / 'tools'))
    from .packaging.pipeline import build, DEV_SAVES
    output = ROOT / '.build/dev' / (time.strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
    launcher = build(target, output, allow_dirty=True, development=True)
    print(f'\nReady: {launcher}\nDevelopment saves: {DEV_SAVES}', flush=True)
    return launcher


def open_editor():
    if sys.platform != 'win32':
        raise ValueError('RPG Maker XP requires Windows. Use uv run play for native Mac/Linux playtesting.')
    sys.path.insert(0, str(ROOT / 'tools'))
    from release_tools import load_release, sha256
    from runtime_inputs import windows_runtime, unpack_pinned
    config = load_release()
    sources = [windows_runtime(ROOT, config), unpack_pinned(ROOT, config, 'windows_editor_archive')]
    for source in sources:
        for path in source.iterdir():
            dest = ROOT / 'game' / path.name
            if dest.exists() and sha256(dest) != sha256(path):
                raise ValueError(f'Preserving modified local file: {dest}. Move it aside before restoring the editor runtime.')
            shutil.copy2(path, dest)
    os.startfile(ROOT / 'game/Game.rxproj')


def dispatch(command, argv):
    parser = argparse.ArgumentParser(prog='uv run ' + command)
    if command in ('build', 'play'):
        if command == 'build':
            parser.add_argument('--platform', choices=('mac', 'windows', 'linux'), help='Defaults to this computer')
    elif command == 'package':
        parser.add_argument('platform', choices=('mac', 'windows', 'linux'))
        parser.add_argument('output', type=Path)
        parser.add_argument('--allow-dirty', action='store_true')
    elif command in ('check', 'rebuild'):
        parser.add_argument('--all', action='store_true', help='Also regenerate maps/data' if command == 'rebuild' else 'Also verify isolated regeneration')
    args = parser.parse_args(argv)
    if command in ('build', 'play'):
        target = getattr(args, 'platform', None) or host_platform()
        launcher = development_build(target)
        if command == 'play':
            if target == 'mac':
                run('open', '-n', '-W', launcher)
            else:
                run(launcher, cwd=launcher.parent)
    elif command == 'package':
        sys.path.insert(0, str(ROOT / 'tools'))
        from .packaging.pipeline import build
        build(args.platform, args.output, allow_dirty=args.allow_dirty)
    elif command == 'check':
        test_dependencies()
        python('tools/verify.py')
        if args.all:
            python('tools/check_rebuild.py')
    elif command == 'rebuild':
        for script in GENERATORS if args.all else ('rebuild_scripts.py',):
            python('tools/' + script)
        if args.all:
            python('tools/validate_maps.py', '--event-scripts', ROOT / 'tools/generated/event_scripts.json')
    elif command == 'doctor':
        print('Checkout:', ROOT)
        print('Python:', platform.python_version())
        print('Native player:', host_platform())
        for name in ('git', 'node', 'npm', *(['codesign', 'xcrun'] if sys.platform == 'darwin' else [])):
            print(name + ':', shutil.which(name) or 'not installed')
        print('Checks require Node:', (ROOT / '.node-version').read_text().strip())
        print('Development guide: docs/development.md')
    elif command == 'editor':
        open_editor()


def entry(command):
    try:
        dispatch(command, sys.argv[1:])
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from None
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None


def build(): entry('build')
def play(): entry('play')
def check(): entry('check')
def rebuild(): entry('rebuild')
def doctor(): entry('doctor')
def editor(): entry('editor')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'play', 'check', 'rebuild', 'doctor', 'editor', 'package'))
    args, rest = parser.parse_known_args()
    sys.argv = [sys.argv[0], *rest]
    entry(args.command)
