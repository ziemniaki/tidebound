"""Package all players from a clean commit; verification belongs to `check --all` and CI."""

from pathlib import Path
import argparse
import subprocess
import tempfile
import zipfile

from tidebound_dev.packaging.pipeline import build
from tidebound_dev.paths import ROOT
from tidebound_dev.release.metadata import check_sources, source_revision
from tidebound_dev.release.artifacts import write_checksums


def build_release(output, root=ROOT):
    output = output.resolve()
    if output.exists():
        raise FileExistsError("Release output already exists; refusing to overwrite it")
    config = check_sources(root)
    source = source_revision(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tidebound-release-", dir=output.parent) as temp:
        artifacts = Path(temp) / "artifacts"
        artifacts.mkdir()
        for platform in ("mac", "windows", "linux"):
            package = Path(temp) / platform
            build(platform, package, root=root)
            for file in package.iterdir():
                if file.name != "SHA256SUMS.txt":
                    file.rename(artifacts / file.name)
        project = artifacts / ("Tidebound_Project_" + config["version"] + ".zip")
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "archive",
                "--format=zip",
                "--prefix=Tidebound_Prototype/",
                "--output=" + str(project),
                source["commit"],
            ],
            check=True,
        )
        with zipfile.ZipFile(project) as archive:
            if archive.testzip() is not None:
                raise ValueError("Project ZIP integrity failure")
            tracked = (
                subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
                .decode()
                .split("\0")
            )
            for name in filter(None, tracked):
                if archive.read("Tidebound_Prototype/" + name) != (root / name).read_bytes():
                    raise ValueError(f"Project ZIP differs from checkout: {name}")
        if source_revision(root) != source:
            raise ValueError("Source changed while the release was being built")
        notes = (root / "docs/release-notes.md").read_text(encoding="utf-8")
        if not notes.startswith("# Tidebound " + config["version"] + "\n"):
            raise ValueError("Player-facing release notes must match release.json")
        (artifacts / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
        write_checksums(artifacts)
        artifacts.rename(output)
    print("PASS: release candidates from", source["commit"], "at", output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build_release(parser.parse_args().output)
