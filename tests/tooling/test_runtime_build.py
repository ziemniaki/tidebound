from pathlib import Path
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev.runtime.build_mac import SOURCE, PATCH, run, fetch
from tidebound_dev.paths import ROOT
from tidebound_dev.release.metadata import load_release


class RuntimeBuildTests(unittest.TestCase):
    def test_interrupted_dependency_fetch_resumes_in_the_same_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            upstream = Path(temp) / "upstream"
            cached = Path(temp) / "cached"
            run("git", "init", "-q", upstream)
            (upstream / "source.txt").write_text("pinned dependency")
            run("git", "add", ".", cwd=upstream)
            run(
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "-qm",
                "source",
                cwd=upstream,
            )
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=upstream, text=True
            ).strip()
            info = {"url": str(upstream), "commit": commit}

            def interrupted(*args, **kwargs):
                if "fetch" in args:
                    raise subprocess.CalledProcessError(1, args)
                run(*args, **kwargs)

            with patch("tidebound_dev.runtime.build_mac.run", side_effect=interrupted):
                with self.assertRaises(subprocess.CalledProcessError):
                    fetch(cached, info, None)
            fetch(cached, info, None)
            self.assertEqual((cached / "source.txt").read_text(), "pinned dependency")
            with self.assertRaisesRegex(ValueError, "differs from lock"):
                fetch(cached, {**info, "commit": "0" * 40}, None)

    def test_make_pwd_matches_subprocess_working_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            run(
                sys.executable,
                "-c",
                'import os; from pathlib import Path; assert os.environ["PWD"] == str(Path.cwd())',
                cwd=Path(temp),
                env=dict(os.environ, PWD="/unrelated/caller"),
            )

    def test_patch_reconstructs_the_shipped_engine_sources(self):
        config = load_release()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with tarfile.open(SOURCE) as original:
                original.extractall(folder, filter="data")
                top = original.getnames()[0].split("/")[0]
            subprocess.run(["git", "apply", str(PATCH)], cwd=folder / top, check=True)
            with tarfile.open(ROOT / config["runtime_source"]) as patched:
                prefix = patched.getnames()[0].split("/")[0]
                for name in (
                    "src/main.cpp",
                    "src/filesystem/filesystemImplApple.mm",
                    "src/filesystem/portablePathApple.h",
                ):
                    self.assertEqual(
                        (folder / top / name).read_bytes(),
                        patched.extractfile(prefix + "/" + name).read(),
                    )


if __name__ == "__main__":
    unittest.main()
