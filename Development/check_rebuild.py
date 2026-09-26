"""Regenerate tracked assets in isolation and detect semantic source/output drift."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GENERATORS = ('rebuild_maps.py', 'rebuild_opening_items.py', 'rebuild_neighbor_data.py',
              'rebuild_field_data.py', 'rebuild_regional_data.py', 'rebuild_scripts.py')


def equivalent(before, after):
    if not after.is_file():
        return False
    if before.read_bytes() == after.read_bytes():
        return True
    if before.suffix.lower() != '.png':
        return False
    # PNG compressor bytes may differ across macOS/Linux and Pillow wheels.
    with Image.open(before) as a, Image.open(after) as b:
        return a.size == b.size and a.convert('RGBA').tobytes() == b.convert('RGBA').tobytes()


def main():
    tracked = list(filter(None, subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')))
    with tempfile.TemporaryDirectory(prefix='tidebound-rebuild-') as temp:
        stage = Path(temp)
        for name in tracked:
            dest = stage / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
        for script in GENERATORS:
            print('+ isolated rebuild:', script, flush=True)
            subprocess.run([sys.executable, str(stage / 'Development' / script)], cwd=stage, check=True)
        subprocess.run([sys.executable, str(stage / 'Development/validate_maps.py'),
                        '--event-scripts', str(stage / 'Development/event_scripts.json')], cwd=stage, check=True)
        differences = [name for name in tracked if not equivalent(ROOT / name, stage / name)]
        if differences:
            raise SystemExit('Generated assets differ from committed source:\n' + '\n'.join(differences))
    print('PASS: isolated rebuild reproduces tracked data, source and decoded PNG pixels')


if __name__ == '__main__':
    main()
