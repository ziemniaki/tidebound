"""Headless checks, optionally including regeneration in a disposable checkout."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from .files import equivalent
from .pipeline import rebuild
from .art import ownership


def verify(root, *, full=False):
    from tidebound_dev.formatting import format_sources

    format_sources(root, check=True)
    from tidebound_dev.release.metadata import check_sources

    check_sources(root)
    ownership.validate(root)
    from tidebound_dev.content.ownership import validate as validate_content

    validate_content(root)
    from .content.verification import inventory

    inventory()
    from .scenarios import catalog, select

    for name in catalog(root):
        select(root, name)

    def run(*command, env=None):
        print("+ " + " ".join(map(str, command)), flush=True)
        subprocess.run(command, cwd=root, env=env, check=True)

    with tempfile.TemporaryDirectory(prefix="tidebound-verify-") as temp:
        events = str(Path(temp) / "event_scripts.json")
        run(
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests/tooling",
            "-t",
            ".",
            "--buffer",
            "--durations",
            "5",
        )
        from tidebound_dev.maps.validate import validate

        validate(root, Path(events))
        run(sys.executable, "tests/prepare_reference.py")
        env = dict(os.environ, TIDEBOUND_EVENT_SCRIPTS=events)
        run("node", "tests/run.cjs", env=env)
    if full:
        _check_regeneration(root)
    print("PASS: headless verification complete. Native graphical playtesting is separate.")


def _check_regeneration(root):
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
        # Remove file outputs only in this disposable regeneration check. Native
        # databases mix stock inputs with custom records; their compilers replace
        # declared records, and ownership removes retired records.
        from .content.ownership import recorded as content_outputs

        for name in [*ownership.recorded(stage), *content_outputs(stage)["files"]]:
            (stage / name).unlink(missing_ok=True)
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
