"""Run the repeatable headless gates without rebuilding tracked game assets."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from tidebound_dev.paths import ROOT


def main(root=ROOT):
    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE", "0") not in ("", "0"):
        raise SystemExit("Run verification without -O/PYTHONOPTIMIZE; geometry checks use assertions.")
    if not shutil.which("node"):
        raise SystemExit("Node.js is required. See docs/development.md for setup.")
    if not (root / "tests/node_modules/@ruby/3.2-wasm-wasi").is_dir():
        raise SystemExit("Install test dependencies: npm ci --prefix tests --ignore-scripts")
    try:
        import rubymarshal
    except ImportError:
        raise SystemExit("Install Python dependencies: uv sync --locked") from None
    from tidebound_dev.formatting import format_sources
    format_sources(root, check=True)
    from tidebound_dev.release.metadata import check_sources
    check_sources(root)

    def run(*command, env=None):
        print("+ " + " ".join(map(str, command)), flush=True)
        subprocess.run(command, cwd=root, env=env, check=True)

    with tempfile.TemporaryDirectory(prefix="tidebound-verify-") as temp:
        events = str(Path(temp) / "event_scripts.json")
        run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py")
        if sys.platform == 'darwin':
            run(sys.executable, 'tests/mac_path_normalization.py')
        from tidebound_dev.maps.validate import validate
        validate(root, Path(events))
        run(sys.executable, "tests/maze_graph.py")
        run(sys.executable, "tests/pond_geometry.py")
        run(sys.executable, "tests/prepare_reference.py")
        env = dict(os.environ, TIDEBOUND_EVENT_SCRIPTS=events)
        for script in ("run.cjs", "native_domain.cjs", "regional_snakes.cjs", "presentation_support.cjs"):
            run("node", "tests/" + script, env=env)
    print("PASS: headless verification complete. Native graphical playtesting is separate.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
