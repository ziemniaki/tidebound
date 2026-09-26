"""Launch the packaged native engine, isolating fixtures and saves from players."""
from pathlib import Path
import argparse
import json
import platform
import plistlib
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
from mac_runtime import run, sign_app
from package_mac import extract_bundle


def smoke(archive, output, arch):
    if sys.platform != 'darwin' or platform.machine() != arch:
        raise ValueError(f'This smoke test requires a native {arch} macOS runner')
    if output.exists():
        raise FileExistsError('Choose a new smoke evidence directory')
    output.mkdir(parents=True)
    namespace = 'Tidebound_Build_Smoke_' + uuid.uuid4().hex
    save_dir = Path.home() / 'Library/Application Support' / namespace
    if save_dir.exists():
        raise FileExistsError('Refusing to reuse an existing save namespace')
    try:
        # mkxp-z's PhysFS loader cannot reliably resolve the macOS /var/folders
        # temporary location. Use the caller's build/evidence directory instead.
        with tempfile.TemporaryDirectory(prefix='tidebound-smoke-', dir=output.parent.resolve()) as temp:
            root = Path(temp)
            extract_bundle(archive, root)
            apps = list(root.glob('*/Tidebound.app'))
            if len(apps) != 1:
                raise ValueError('Expected one packaged Tidebound app')
            app = apps[0]
            run('codesign', '--verify', '--deep', '--strict', '--all-architectures', str(app))
            game = app / 'Contents/Game'
            # Preserve launch settings and use the normal native script loader.
            # Only this disposable copy receives a test Main and save namespace.
            config = game / 'mkxp.json'
            text = config.read_text(encoding='utf-8')
            end = text.rfind('}')
            if end < 0:
                raise ValueError('Missing launch configuration object')
            text = re.sub(r'"dataPathApp"\s*:\s*"[^"]+"', '"dataPathApp": "' + namespace + '"', text)
            config.write_text(text, encoding='utf-8')
            archive_path = game / 'Data/Scripts.rxdata'
            entries = loads(archive_path.read_bytes())
            main = [entry for entry in entries if entry[1] == 'Main']
            if len(main) != 1:
                raise ValueError('Expected exactly one Main entry')
            main[0][2] = zlib.compress(Path(__file__).with_name('native_runtime_smoke.rb').read_bytes())
            archive_path.write_bytes(writes(entries))
            sign_app(app)
            info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
            executable = app / 'Contents/MacOS' / info['CFBundleExecutable']
            # Exercise a normal installed-app launch through Launch Services.
            # Starting the executable with cwd=game hid bundle launch problems.
            command = ['open', '-n', '-W', '--arch', arch,
                       '--stdout', str(output.resolve() / 'engine.log'),
                       '--stderr', str(output.resolve() / 'engine-stderr.log'),
                       '--env', 'TIDEBOUND_SMOKE_REPORT=' + str(output.resolve() / 'native-smoke.rxdata'),
                       '--env', 'TIDEBOUND_SMOKE_SCREENSHOT=' + str(output.resolve() / 'native-smoke.png'),
                       str(app)]
            try:
                subprocess.run(command, cwd='/', timeout=60, check=True)
            finally:
                # open is a launcher; terminating it alone leaves an app with a
                # modal error alive. Match only this unique disposable bundle.
                subprocess.run(['pkill', '-KILL', '-f', '^' + re.escape(str(executable)) + '$'],
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = read_report(output)
            if not result.get('passed'):
                raise RuntimeError(result.get('error', 'Native smoke did not pass'))
            if namespace not in result['save_directory']:
                raise RuntimeError('Smoke test did not use its isolated save namespace')
            if not (output / 'native-smoke.png').is_file():
                raise RuntimeError('Native rendering evidence was not produced')
            result['architecture'] = arch
            result['launch_method'] = 'Launch Services (installed app, working directory /)'
            (output / 'native-smoke.json').write_text(json.dumps(result, indent=2) + '\n')
            print('PASS: native', arch, 'engine, game data, save roundtrip and graphics')
    finally:
        if save_dir.exists():
            shutil.rmtree(save_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    args = parser.parse_args()
    smoke(args.archive, args.output, args.arch)
