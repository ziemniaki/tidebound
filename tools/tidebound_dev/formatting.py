"""Format Python and Ruby with pinned tools; no system Ruby installation needed."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request

from filelock import FileLock
from .paths import ROOT


def formatter_dependencies(root=ROOT):
    lock = root / "tests/formatters.lock.json"
    fingerprint = hashlib.sha256(lock.read_bytes()).hexdigest()
    cache = root / ".cache/formatters" / fingerprint
    cache.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(cache) + ".lock", timeout=60):
        if cache.is_dir():
            return cache
        with tempfile.TemporaryDirectory(dir=cache.parent) as temp:
            stage = Path(temp) / "gems"
            stage.mkdir()
            for package in json.loads(lock.read_text()):
                with urllib.request.urlopen(package["url"], timeout=30) as response:
                    data = response.read()
                if hashlib.sha256(data).hexdigest() != package["sha256"]:
                    raise ValueError("Formatter dependency hash mismatch: " + package["name"])
                if package["format"] == "ruby":
                    (stage / package["name"]).write_bytes(data)
                    continue
                with tarfile.open(fileobj=io.BytesIO(data)) as gem:
                    contents = gem.extractfile("data.tar.gz").read()
                with tarfile.open(fileobj=io.BytesIO(contents)) as archive:
                    archive.extractall(stage / package["name"], filter="data")
            stage.rename(cache)
    return cache


def format_sources(root=ROOT, check=False):
    cache = formatter_dependencies(root)
    mode = ["--check"] if check else []
    subprocess.run(["ruff", "format", *mode, "."], cwd=root, check=True)
    subprocess.run(["node", "tests/format_ruby.cjs", str(cache), *mode], cwd=root, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    from .cli import test_dependencies

    test_dependencies()
    format_sources(check=args.check)
