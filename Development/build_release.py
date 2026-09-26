"""Build verified release candidates from a clean commit; never publish them."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import zipfile

from package_mac import build
from package_windows import build as build_windows
from release_tools import ROOT, check_sources, sha256, source_revision


def build_release(output, root=ROOT):
    output = output.resolve()
    if output.exists():
        raise FileExistsError('Release output already exists; refusing to overwrite it')
    config = check_sources(root)
    source = source_revision(root)
    subprocess.run([sys.executable, str(root / 'Development/verify.py')], cwd=root, check=True)
    subprocess.run([sys.executable, str(root / 'Development/check_rebuild.py')], cwd=root, check=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.tidebound-release-', dir=output.parent) as temp:
        artifacts = Path(temp) / 'artifacts'
        build(artifacts, root=root)
        windows = Path(temp) / 'windows'
        build_windows(windows, root=root)
        for file in windows.iterdir():
            if file.name != 'SHA256SUMS.txt':
                file.rename(artifacts / file.name)
        project = artifacts / ('Tidebound_Project_' + config['version'] + '.zip')
        subprocess.run(['git', '-C', str(root), 'archive', '--format=zip',
                        '--prefix=Tidebound_Prototype/', '--output=' + str(project), source['commit']], check=True)
        with zipfile.ZipFile(project) as archive:
            if archive.testzip() is not None:
                raise ValueError('Project ZIP integrity failure')
            tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode().split('\0')
            for name in filter(None, tracked):
                if archive.read('Tidebound_Prototype/' + name) != (root / name).read_bytes():
                    raise ValueError(f'Project ZIP differs from checkout: {name}')
        if source_revision(root) != source:
            raise ValueError('Source changed while the release was being built')
        (artifacts / 'RELEASE_NOTES.md').write_text(
            f"Tidebound {config['version']} (Mac build {config['mac_build']})\n\n"
            f"Source commit: `{source['commit']}`.\n\n"
            "The universal Mac ZIP includes native Intel and Apple Silicon code. "
            "It is ad-hoc signed for integrity, not Developer ID signed or notarized. "
            "The Windows x64 player ZIP includes the pinned existing executable and DLLs. The editable project ZIP is available separately.\n\n"
            "Saves keep the Tidebound_Opening_0_2 directory. Read READ_ME_FIRST.txt before launching. "
            "Automated native smoke checks on Windows x64, Intel Mac and Apple Silicon are not a complete playthrough or an Intel Monterey playtest.\n",
            encoding='utf-8')
        files = sorted(p for p in artifacts.iterdir() if p.name != 'SHA256SUMS.txt')
        (artifacts / 'SHA256SUMS.txt').write_text(
            ''.join(sha256(p) + '  ' + p.name + '\n' for p in files), encoding='utf-8')
        artifacts.rename(output)
    print('PASS: release candidates from', source['commit'], 'at', output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    build_release(parser.parse_args().output)
