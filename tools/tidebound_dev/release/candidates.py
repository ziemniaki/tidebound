"""Package all players from a clean commit; verification belongs to `check --all` and CI."""

from pathlib import Path
import argparse
import tempfile

from tidebound_dev.packaging.pipeline import build
from tidebound_dev.paths import ROOT
from tidebound_dev.release.metadata import check_sources, source_revision
from tidebound_dev.release.artifacts import write_checksums


def build_release(output, root=ROOT):
    output = output.resolve()
    if output.exists():
        raise FileExistsError("Release output already exists; refusing to overwrite it")
    from tidebound_dev.pipeline import rebuild

    source_revision(root)
    rebuild(root)
    config = check_sources(root)
    source = source_revision(root)
    notes = (root / "docs/release-notes.md").read_text(encoding="utf-8")
    if not notes.startswith("# Tidebound " + config["version"] + "\n"):
        raise ValueError("Player-facing release notes must match release.json")
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
        if source_revision(root) != source:
            raise ValueError("Source changed while the release was being built")
        (artifacts / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
        write_checksums(artifacts)
        artifacts.rename(output)
    print("PASS: release candidates from", source["commit"], "at", output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build_release(parser.parse_args().output)
