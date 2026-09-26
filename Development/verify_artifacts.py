"""Verify the complete downloaded release candidate on any platform."""
from pathlib import Path
import argparse
import re

from release_tools import sha256


def verify(folder):
    expected = set()
    for line in (folder / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  ([^/\\]+)', line)
        if not match or match[2] in ('.', '..', 'SHA256SUMS.txt') or match[2] in expected:
            raise ValueError('Invalid or duplicate checksum entry')
        digest, name = match.groups()
        expected.add(name)
        if sha256(folder / name) != digest:
            raise ValueError(f'Artifact checksum mismatch: {name}')
    actual = {p.name for p in folder.iterdir() if p.name != 'SHA256SUMS.txt'}
    if not expected or actual != expected:
        raise ValueError('Checksums do not cover the complete candidate')
    print('PASS: all downloaded release artifact checksums')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    verify(parser.parse_args().folder)
