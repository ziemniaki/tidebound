"""Regenerate tracked assets in isolation and detect semantic source/output drift."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

from tidebound_dev.paths import ROOT
from tidebound_dev.files import equivalent
from tidebound_dev.pipeline import rebuild


def main(root=ROOT):
    tracked = list(
        filter(
            None, subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
        )
    )
    with tempfile.TemporaryDirectory(prefix="tidebound-rebuild-") as temp:
        stage = Path(temp)
        for name in tracked:
            dest = stage / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, dest)
        rebuild(stage, full=True)
        differences = [name for name in tracked if not equivalent(root / name, stage / name)]
        generated = {
            p.relative_to(stage).as_posix()
            for p in stage.rglob("*")
            if p.is_file() and "__pycache__" not in p.relative_to(stage).parts
        }
        differences.extend(sorted(generated - set(tracked)))
        if differences:
            raise SystemExit(
                "Generated assets differ from committed source:\n" + "\n".join(differences)
            )
    print("PASS: isolated rebuild reproduces tracked data, source and decoded PNG pixels")


if __name__ == "__main__":
    main()
