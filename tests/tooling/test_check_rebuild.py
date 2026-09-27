"""A clean regeneration must reproduce the complete set of tracked outputs."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev.checks import rebuild as check_rebuild


class GeneratedFileSetTests(unittest.TestCase):
    def regenerate(self, generate):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input.txt").write_text("source")
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(["git", "-C", root, "add", "."], check=True)
            with (
                patch.object(check_rebuild, "generate", side_effect=generate),
                redirect_stdout(StringIO()),
            ):
                try:
                    check_rebuild.main(root)
                finally:
                    self.assertEqual((root / "input.txt").read_text(), "source")

    def test_new_untracked_output_cannot_pass_regeneration(self):
        def generate(root):
            (root / "new-sprite.png").write_bytes(b"new generated asset")

        with self.assertRaisesRegex(SystemExit, "new-sprite.png"):
            self.regenerate(generate)

    def test_python_import_cache_is_not_a_generated_game_asset(self):
        def generate(root):
            (root / "__pycache__").mkdir()
            (root / "__pycache__/fixture.pyc").write_bytes(b"cache")

        self.regenerate(generate)

    def test_failed_isolated_generation_cannot_change_checkout(self):
        def generate(root):
            (root / "input.txt").write_text("partial output")
            raise ValueError("generation failed")

        with self.assertRaisesRegex(ValueError, "generation failed"):
            self.regenerate(generate)
