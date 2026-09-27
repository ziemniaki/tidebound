"""Format Python and Ruby with pinned tools; no system Ruby installation needed."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import shutil
import tarfile
import tempfile
import urllib.request

from filelock import FileLock
from .paths import ROOT


def node_dependencies(root=ROOT):
    node, npm = shutil.which("node"), shutil.which("npm")
    wanted = (root / ".node-version").read_text().strip()
    if not node or not npm:
        raise ValueError(
            f"Checks need Node.js {wanted}. Install it, then rerun this command. See docs/development.md."
        )
    actual = subprocess.check_output([node, "--version"], text=True).strip().lstrip("v")
    if actual != wanted:
        raise ValueError(f"Checks need Node.js {wanted}; found {actual}. See docs/development.md.")
    lock = hashlib.sha256((root / "tests/package-lock.json").read_bytes()).hexdigest()
    stamp = root / "tests/node_modules/.tidebound-lock"
    if (
        not stamp.exists()
        or stamp.read_text() != lock
        or not (stamp.parent / "@ruby/3.2-wasm-wasi/dist/ruby.wasm").is_file()
    ):
        subprocess.run([npm, "ci", "--prefix", root / "tests", "--ignore-scripts"], check=True)
        stamp.write_text(lock)


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
    node_dependencies(root)
    cache = formatter_dependencies(root)
    mode = ["--check"] if check else []
    subprocess.run(["ruff", "format", *mode, "."], cwd=root, check=True)
    subprocess.run(["node", "tests/format_ruby.cjs", str(cache), *mode], cwd=root, check=True)
