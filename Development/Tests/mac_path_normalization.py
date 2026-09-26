"""Compile and exercise the actual patched Mac runtime path resolver."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_tools import ROOT, load_release, sha256


def test(source):
    with tempfile.TemporaryDirectory(prefix='Tidebound é 日本 ') as temp:
        root = Path(temp)
        binary = root / 'path-test'
        subprocess.run(['clang++', '-std=c++14', '-framework', 'Foundation',
                        '-I', str(source / 'src/filesystem'),
                        str(Path(__file__).with_suffix('.mm')), '-o', str(binary)], check=True)
        for folder in (root / 'Downloads', root / ('deep folder ' * 6) / ('nested é ' * 8) /
                       ('more folders ' * 6) / ('another directory ' * 5) / ('last folder ' * 5)):
            (folder / 'Data').mkdir(parents=True)
            (folder / 'Data/Scripts.rxdata').write_bytes(b'test')
            subprocess.run([str(binary), str(folder)], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', help='Patched source; defaults to the pinned source archive')
    args = parser.parse_args()
    if args.source:
        test(args.source.resolve())
    else:
        config = load_release()
        archive_path = ROOT / config['runtime_source']
        if sha256(archive_path) != config['runtime_source_sha256']:
            raise ValueError('Runtime source checksum mismatch')
        with tempfile.TemporaryDirectory(prefix='tidebound-path-source-') as temp:
            with tarfile.open(archive_path) as archive:
                archive.extractall(temp, filter='data')
                source = Path(temp) / archive.getnames()[0].split('/')[0]
            test(source)
