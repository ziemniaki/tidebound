"""Verify the complete downloaded release candidate on any platform."""

from pathlib import Path
import argparse
import json
import re

from tidebound_dev.files import sha256


def verify(folder):
    expected = set()
    for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if not match or match[2] in (".", "..", "SHA256SUMS.txt") or match[2] in expected:
            raise ValueError("Invalid or duplicate checksum entry")
        digest, name = match.groups()
        expected.add(name)
        if sha256(folder / name) != digest:
            raise ValueError(f"Artifact checksum mismatch: {name}")
    actual = {p.name for p in folder.iterdir() if p.name != "SHA256SUMS.txt"}
    if not expected or actual != expected:
        raise ValueError("Checksums do not cover the complete candidate")
    print("PASS: all downloaded release artifact checksums")


def validate_candidate(folder, version, commit, mac_build):
    verify(folder)
    expected = {
        f"Tidebound_Mac_{version}_universal.zip",
        f"Tidebound_Windows_{version}_x64.zip",
        f"Tidebound_Linux_{version}_x86_64.zip",
        "BUILD.json",
        "WINDOWS_BUILD.json",
        "LINUX_BUILD.json",
        "SHA256SUMS.txt",
        "RELEASE_NOTES.md",
    }
    if {p.name for p in folder.iterdir()} != expected:
        raise ValueError("Expected the complete three-platform candidate set")
    for name in ("BUILD.json", "WINDOWS_BUILD.json", "LINUX_BUILD.json"):
        manifest = json.loads((folder / name).read_text())
        if manifest["version"] != version or manifest["source"] != {
            "commit": commit,
            "dirty": False,
        }:
            raise ValueError("Candidate source/version does not match verified workflow commit")
    if json.loads((folder / "BUILD.json").read_text())["mac_build"] != mac_build:
        raise ValueError("Candidate Mac build does not match release metadata")


def write_checksums(folder):
    files = sorted(path for path in folder.iterdir() if path.name != "SHA256SUMS.txt")
    (folder / "SHA256SUMS.txt").write_text(
        "".join(sha256(path) + "  " + path.name + "\n" for path in files), encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    verify(parser.parse_args().folder)
