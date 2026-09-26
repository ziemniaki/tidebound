"""Shared, fail-closed release metadata and source checks."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

from script_archive import validate_archive

ROOT = Path(__file__).resolve().parent.parent
SAVE_DIRECTORY = "Tidebound_Opening_0_2"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_release(root=ROOT):
    config = json.loads((root / "release.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", config["version"]):
        raise ValueError("release.json: invalid version")
    if not re.fullmatch(r"[1-9]\d*", config["mac_build"]):
        raise ValueError("release.json: mac_build must be a positive integer string")
    if config["architectures"] != ["x86_64", "arm64"]:
        raise ValueError("The supported Mac artifact is universal: x86_64 and arm64")
    for key in ("runtime_archive", "runtime_source"):
        path = Path(config[key])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe runtime path: {path}")
    return config


def check_sources(root=ROOT):
    config = load_release(root)
    recorded = json.loads((root / 'BUILD_MANIFEST.json').read_text(encoding='utf-8'))
    if recorded['version'] != config['version']:
        raise ValueError('Version mismatch: BUILD_MANIFEST.json versus release.json')
    scripts = validate_archive(root, root / "Development")
    for name, pattern in (("Tidebound/001_Core", r'VERSION\s*=\s*"([^"]+)"'),
                          ("Settings", r'GAME_VERSION\s*=\s*"([^"]+)"')):
        match = re.search(pattern, scripts[name])
        if not match or match[1] != config["version"]:
            raise ValueError(f"Version mismatch: {name} versus release.json; rebuild scripts")
    launch = (root / "mkxp.json").read_text(encoding="utf-8")
    if not re.search(r'"dataPathApp"\s*:\s*"' + SAVE_DIRECTORY + r'"', launch):
        raise ValueError("The established save-directory identity must be preserved")
    if not re.search(r'"fontHeightReporting"\s*:\s*1\b', launch):
        raise ValueError("The native font height fix must remain enabled")
    for path_key, hash_key in (("runtime_archive", "runtime_sha256"),
                              ("runtime_source", "runtime_source_sha256")):
        if sha256(root / config[path_key]) != config[hash_key]:
            raise ValueError(f"Runtime provenance hash mismatch: {config[path_key]}")
    return config


def source_revision(root=ROOT, allow_dirty=False):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    dirty = bool(git("status", "--porcelain", "--untracked-files=normal"))
    if dirty and not allow_dirty:
        raise ValueError("Release packaging requires a clean checkout; commit changes or use --allow-dirty for a local preview")
    return {"commit": git("rev-parse", "HEAD"), "dirty": dirty}
