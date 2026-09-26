"""Exercise the shipped Windows executable in a disposable game/save directory."""
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_mac import extract_bundle, game_hashes


def smoke(archive, output):
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise ValueError('This smoke test requires a native Windows x64 runner')
    if output.exists():
        raise FileExistsError('Choose a new smoke evidence directory')
    output = output.resolve()
    output.mkdir(parents=True)
    namespace = 'Tidebound_Build_Smoke_' + uuid.uuid4().hex
    save_dir = Path(os.environ['APPDATA']) / namespace
    if save_dir.exists():
        raise FileExistsError('Refusing to reuse an existing save namespace')
    try:
        with tempfile.TemporaryDirectory(prefix='tidebound-smoke-', dir=output.parent) as temp:
            root = Path(temp)
            extract_bundle(archive, root)
            games = list(root.glob('*/Game.exe'))
            if len(games) != 1:
                raise ValueError('Expected one packaged Windows game')
            game = games[0].parent
            manifest = json.loads((game / 'BUILD.json').read_text(encoding='utf-8'))
            actual = game_hashes(game)
            actual.pop('BUILD.json')
            if actual != manifest['files_sha256']:
                raise ValueError('Extracted Windows game differs from build manifest')
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
            env = dict(os.environ, TIDEBOUND_SMOKE_REPORT=str(output / 'native-smoke.json'),
                       TIDEBOUND_SMOKE_SCREENSHOT=str(output / 'native-smoke.png'))
            try:
                with (output / 'engine.log').open('w') as log:
                    with subprocess.Popen([str(game / 'Game.exe')], cwd=game, env=env,
                                          stdout=log, stderr=subprocess.STDOUT) as process:
                        try:
                            code = process.wait(timeout=90)
                        except subprocess.TimeoutExpired:
                            # Preserve a blocking native error dialog before terminating.
                            try:
                                from PIL import ImageGrab
                                ImageGrab.grab().save(output / 'timeout-desktop.png')
                            except Exception as error:
                                (output / 'capture-error.txt').write_text(str(error), encoding='utf-8')
                            finally:
                                process.kill()
                                process.wait()
                            raise
                        if code:
                            raise subprocess.CalledProcessError(code, process.args)
            finally:
                for directory, label in ((game, 'game'), (save_dir, 'save')):
                    for pattern in ('*.log', 'errorlog.txt'):
                        for log in directory.glob(pattern):
                            shutil.copy2(log, output / (label + '-' + log.name))
            result = json.loads((output / 'native-smoke.json').read_text(encoding='utf-8'))
            if not result.get('passed'):
                raise RuntimeError(result.get('error', 'Native smoke did not pass'))
            if Path(result['save_directory']).resolve() != save_dir.resolve():
                raise RuntimeError('Smoke test did not use its isolated save namespace')
            if not (output / 'native-smoke.png').is_file():
                raise RuntimeError('Native rendering evidence was not produced')
            result.update(architecture='x86_64', platform='windows',
                          audio_backend=env.get('ALSOFT_DRIVERS', 'default'))
            (output / 'native-smoke.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            print('PASS: native Windows x64 engine, game data, save roundtrip and graphics')
    finally:
        if save_dir.exists():
            shutil.rmtree(save_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    smoke(args.archive, args.output)
