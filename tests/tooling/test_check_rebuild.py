"""An isolated build must not depend on local outputs or alter authored inputs."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tidebound_dev import checks


class GeneratedFileSetTests(unittest.TestCase):
    def regenerate(self, generate):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input.txt").write_text("source")
            (root / ".gitignore").write_text("game/\nsrc/generated/\n")
            image = root / "game/Graphics/Pictures/custom.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"export")
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(["git", "-C", root, "add", "."], check=True)
            with (
                patch.object(checks, "_rebuild_isolated", side_effect=generate),
                redirect_stdout(StringIO()),
            ):
                try:
                    checks._check_regeneration(root)
                finally:
                    self.assertEqual((root / "input.txt").read_text(), "source")

    def test_missing_or_extra_output_cannot_pass_a_clean_build(self):
        def extra(root):
            (root / "game").mkdir()
            (root / "game/new-sprite.png").write_bytes(b"unexpected")

        for generate in (lambda root: None, extra):
            with self.subTest(generate=generate), self.assertRaisesRegex(SystemExit, "custom.png"):
                self.regenerate(generate)

    def test_regeneration_cannot_reuse_local_output(self):
        def generate(root):
            self.assertFalse((root / "game").exists())
            image = root / "game/Graphics/Pictures/custom.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"export")

        self.regenerate(generate)

    def test_failed_isolated_generation_cannot_change_checkout(self):
        def generate(root):
            (root / "input.txt").write_text("partial output")
            raise ValueError("generation failed")

        with self.assertRaisesRegex(ValueError, "generation failed"):
            self.regenerate(generate)
