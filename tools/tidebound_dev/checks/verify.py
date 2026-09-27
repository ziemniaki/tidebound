"""Run the repeatable headless gates without rebuilding tracked game assets."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile

from tidebound_dev.paths import ROOT


def main(root=ROOT):
    from tidebound_dev.formatting import format_sources

    format_sources(root, check=True)
    from tidebound_dev.release.metadata import check_sources

    check_sources(root)

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
    print("PASS: headless verification complete. Native graphical playtesting is separate.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
