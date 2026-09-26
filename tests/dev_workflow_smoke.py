"""Exercise the installed CLI's build command on a native CI host."""
from pathlib import Path
import json
import plistlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run(['uv', 'run', '--locked', 'build'], cwd=ROOT,
                            text=True, capture_output=True)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)
    match = re.search(r'^Ready: (.+)$', result.stdout, re.M)
    if not match:
        raise SystemExit('Build did not report a launcher')
    launcher = Path(match[1])
    if not launcher.exists() or not launcher.resolve().is_relative_to(ROOT / '.build/dev'):
        raise SystemExit('Missing development launcher or incorrect output location')
    mac = launcher.suffix == '.app'
    folder = launcher.parent
    game = launcher / 'Contents/Game' if mac else folder
    config = (game / 'mkxp.json').read_text(encoding='utf-8')
    if not re.search(r'"dataPathApp"\s*:\s*"Tidebound_Development"', config):
        raise SystemExit('Development build does not isolate saves')
    if not (game / 'Data/Scripts.rxdata').is_file():
        raise SystemExit('Development build is missing scripts')
    manifest = json.loads((folder / 'DEVELOPMENT.json').read_text())
    if manifest['kind'] != 'development' or (folder / 'BUILD.json').exists():
        raise SystemExit('Development copy incorrectly retains release manifest')
    if mac:
        plist = plistlib.loads((launcher / 'Contents/Info.plist').read_bytes())
        if plist['CFBundleIdentifier'] != 'game.tidebound.development':
            raise SystemExit('Development app shares release bundle identifier')
        subprocess.run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', launcher], check=True)
    if 'Tidebound_Opening_0_2' not in (ROOT / 'game/mkxp.json').read_text(encoding='utf-8'):
        raise SystemExit('Build changed the source save namespace')
    print('PASS: native developer CLI builds a complete player with isolated saves')


if __name__ == '__main__':
    main()
