"""Run the repeatable headless gates without rebuilding tracked game assets."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE", "0") not in ("", "0"):
        raise SystemExit("Run verification without -O/PYTHONOPTIMIZE; geometry checks use assertions.")
    if not shutil.which("node"):
        raise SystemExit("Node.js is required. See Development/README.md for setup.")
    if not (ROOT / "Development/Tests/node_modules/@ruby/3.2-wasm-wasi").is_dir():
        raise SystemExit("Install test dependencies: npm ci --prefix Development/Tests --ignore-scripts")
    try:
        import rubymarshal
    except ImportError:
        raise SystemExit("Install Python dependencies: python -m pip install -r requirements-dev.txt") from None
    from release_tools import check_sources
    check_sources(ROOT)

    def run(*command, env=None):
        print("+ " + " ".join(map(str, command)), flush=True)
        subprocess.run(command, cwd=ROOT, env=env, check=True)

    with tempfile.TemporaryDirectory(prefix="tidebound-verify-") as temp:
        events = str(Path(temp) / "event_scripts.json")
        run(sys.executable, "-m", "unittest", "discover", "-s", "Development/Tests", "-p", "test_*.py")
        run(sys.executable, "Development/validate_maps.py", "--event-scripts", events)
        run(sys.executable, "Development/Tests/maze_graph.py")
        run(sys.executable, "Development/Tests/pond_geometry.py")
        run(sys.executable, "Development/Tests/prepare_reference.py")
        env = dict(os.environ, TIDEBOUND_EVENT_SCRIPTS=events)
        for script in ("run.cjs", "native_domain.cjs", "regional_snakes.cjs"):
            run("node", "Development/Tests/" + script, env=env)
    print("PASS: headless verification complete. Native graphical playtesting is separate.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
