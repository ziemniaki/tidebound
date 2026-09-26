"""Exercise the shipped Linux executable in a disposable game/save directory."""
from pathlib import Path
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from smoke_report import read_report

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_mac import extract_bundle, game_hashes


def smoke(archive, output):
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise ValueError('This smoke test requires a native Linux x86_64 runner')
    if output.exists():
        raise FileExistsError('Choose a new smoke evidence directory')
    output = output.resolve()
    output.mkdir(parents=True)
    namespace = 'Tidebound_Build_Smoke_' + uuid.uuid4().hex
    save_dir = output.parent / ('.linux-save-' + namespace)
    if save_dir.exists():
        raise FileExistsError('Refusing to reuse an existing save namespace')
    try:
        with tempfile.TemporaryDirectory(prefix='Tidebound é 日本 ', dir=output.parent) as temp:
            root = Path(temp)
            extract_bundle(archive, root)
            games = list(root.glob('*/Tidebound.sh'))
            if len(games) != 1:
                raise ValueError('Expected one packaged Linux game')
            game = games[0].parent
            manifest = json.loads((game / 'BUILD.json').read_text(encoding='utf-8'))
            actual = game_hashes(game)
            actual.pop('BUILD.json')
            if actual != manifest['files_sha256']:
                raise ValueError('Extracted Linux game differs from build manifest')
            for name in manifest['native_images']:
                dependencies = subprocess.check_output(['ldd', str(game / name)], text=True, stderr=subprocess.STDOUT)
                with (output / 'dependencies.log').open('a') as log:
                    log.write(name + '\n' + dependencies + '\n')
                if 'not found' in dependencies:
                    raise RuntimeError('Missing Linux runtime dependency: ' + name)
            game = game.rename(root / 'Relocated game é 日本')
            config = game / 'mkxp.json'
            text, count = re.subn(r'"dataPathApp"\s*:\s*"[^"]+"',
                                 '"dataPathApp": "' + namespace + '"', config.read_text(encoding='utf-8'))
            if count != 1:
                raise ValueError('Expected one save namespace setting')
            config.write_text(text, encoding='utf-8')
            scripts = game / 'Data/Scripts.rxdata'
            entries = loads(scripts.read_bytes())
            main = [entry for entry in entries if entry[1] == 'Main']
            if len(main) != 1:
                raise ValueError('Expected exactly one Main entry')
            main[0][2] = zlib.compress(Path(__file__).with_name('native_runtime_smoke.rb').read_bytes())
            scripts.write_bytes(writes(entries))
            shortcut = root / 'Launch Tidebound é 日本'
            shortcut.symlink_to(game / 'Tidebound.sh')
            for path in [*game.rglob('*'), game]:
                path.chmod(path.stat().st_mode & ~0o222)
            env = dict(os.environ, HOME=str(save_dir), XDG_DATA_HOME=str(save_dir / 'data'),
                       XDG_CONFIG_HOME=str(save_dir / 'config'), TIDEBOUND_SMOKE_REPORT=str(output / 'native-smoke.rxdata'),
                       TIDEBOUND_SMOKE_SCREENSHOT=str(output / 'native-smoke.png'))
            try:
                with (output / 'engine.log').open('w') as log:
                    # Start outside the game folder to exercise the shipped launcher.
                    subprocess.run([str(shortcut)], cwd=root, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, timeout=90, check=True)
            finally:
                for directory, label in ((game, 'game'), (save_dir, 'save')):
                    for pattern in ('*.log', 'errorlog.txt'):
                        for log in directory.rglob(pattern):
                            shutil.copy2(log, output / (label + '-' + log.name))
            result = read_report(output)
            if not result.get('passed'):
                raise RuntimeError(result.get('error', 'Native smoke did not pass'))
            if result['game_directory_writable']:
                raise RuntimeError('Relocated Linux game was not read-only during the smoke')
            if not Path(result['save_directory']).resolve().is_relative_to(save_dir.resolve()) or namespace not in result['save_directory']:
                raise RuntimeError('Smoke test did not use its isolated save namespace')
            if not (output / 'native-smoke.png').is_file():
                raise RuntimeError('Native rendering evidence was not produced')
            result.update(architecture='x86_64', platform='linux',
                          audio_backend=env.get('ALSOFT_DRIVERS', 'default'),
                          graphics_driver=env.get('LIBGL_ALWAYS_SOFTWARE', 'system'))
            (output / 'native-smoke.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            print('PASS: native Linux x86_64 engine, game data, save roundtrip and graphics')
    finally:
        if save_dir.exists():
            shutil.rmtree(save_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    smoke(args.archive, args.output)
