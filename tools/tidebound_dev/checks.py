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
    rebuild(root)
    from tidebound_dev.release.metadata import check_sources

    check_sources(root)
    from .catalog import validate_names

    validate_names(root)
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
        _rebuild_isolated(stage)

        def outputs(folder):
            from .workspace import files

            return {"game/" + name for name in files(folder / "game")} | {
                p.relative_to(folder).as_posix()
                for directory in ("game/.generated", "src/generated")
                for p in (folder / directory).rglob("*")
                if p.is_file()
            }

        expected, actual = outputs(root), outputs(stage)
        differences = sorted(expected ^ actual)
        differences.extend(
            name for name in sorted(expected & actual) if not equivalent(root / name, stage / name)
        )
        differences.extend(name for name in tracked if not equivalent(root / name, stage / name))
        if differences:
            raise SystemExit("Clean builds differ:\n" + "\n".join(differences))
    print(
        "PASS: clean checkout reproduces the game and generated Ruby (including decoded PNG pixels)"
    )


def _rebuild_isolated(root):
    # Load catalogs and tooling from the isolated checkout, not this process's imports.
    subprocess.run(["uv", "run", "--locked", "build", "--compile-only"], cwd=root, check=True)
