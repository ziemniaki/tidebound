"""A clean regeneration must reproduce the complete set of tracked outputs."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import json
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev import checks


class GeneratedFileSetTests(unittest.TestCase):
    def regenerate(self, generate, output="game/Graphics/Pictures/custom.png"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input.txt").write_text("source")
            image = root / output
            image.parent.mkdir(parents=True)
            image.write_bytes(b"stale export")
            manifest = root / "tools/generated/assets.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({output: "files"}))
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(["git", "-C", root, "add", "."], check=True)
            with (
                patch.object(checks, "rebuild", side_effect=generate),
                redirect_stdout(StringIO()),
            ):
                try:
                    checks._check_regeneration(root)
                finally:
                    self.assertEqual((root / "input.txt").read_text(), "source")

    def test_new_untracked_output_cannot_pass_regeneration(self):
        def generate(root, *, full):
            (root / "new-sprite.png").write_bytes(b"new generated asset")

        with self.assertRaisesRegex(SystemExit, "new-sprite.png"):
            self.regenerate(generate)

    def test_an_exporter_that_stops_writing_cannot_pass_using_old_output(self):
        for output in ("game/Graphics/Pictures/custom.png", "src/generated/prop_assets.rb"):
            with self.subTest(output=output), self.assertRaisesRegex(SystemExit, Path(output).name):
                self.regenerate(lambda root, **kwargs: None, output)

    def test_python_import_cache_is_not_a_generated_game_asset(self):
        def generate(root, *, full):
            (root / "game/Graphics/Pictures/custom.png").write_bytes(b"stale export")
            (root / "__pycache__").mkdir()
            (root / "__pycache__/fixture.pyc").write_bytes(b"cache")

        self.regenerate(generate)

    def test_failed_isolated_generation_cannot_change_checkout(self):
        def generate(root, *, full):
            (root / "input.txt").write_text("partial output")
            raise ValueError("generation failed")

        with self.assertRaisesRegex(ValueError, "generation failed"):
            self.regenerate(generate)
