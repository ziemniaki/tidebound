"""The manifest is authoritative; missing and undiscovered sources must fail."""

from pathlib import Path
import tempfile
import unittest

from tidebound_dev.scripts.archive import source_files
from tidebound_dev.scripts.patches import patch_engine
import zlib


class SourceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "feature").mkdir()
        (self.root / "feature/start.rb").write_text("# start")
        (self.root / "core.rb").write_text("# core")
        self.manifest = self.root / "load_order.txt"
        self.manifest.write_text("feature/start.rb\ncore.rb\n")

    def test_explicit_order_survives_nested_paths_and_filename_sort_order(self):
        self.assertEqual(
            [p.relative_to(self.root).as_posix() for p in source_files(self.root)],
            ["feature/start.rb", "core.rb"],
        )

    def test_unlisted_source_cannot_be_omitted_from_the_game(self):
        (self.root / "forgotten.rb").write_text("# feature")
        with self.assertRaisesRegex(ValueError, "unlisted"):
            source_files(self.root)

    def test_missing_duplicate_and_escaping_entries_fail(self):
        for text in ("missing.rb\n", "core.rb\ncore.rb\n", "../outside.rb\n"):
            with self.subTest(text=text):
                self.manifest.write_text(text)
                with self.assertRaises(ValueError):
                    source_files(self.root)


class EnginePatchTests(unittest.TestCase):
    def stock(self):
        return [
            [1, name, zlib.compress(code.encode())]
            for name, code in {
                "Settings": 'GAME_VERSION = "old"\nTIME_SHADING = true',
                "Main": "return Scene_Intro.new",
                "Battler_ChangeSelf": '"{1} fainted!"',
                "Overworld": '"{1} fainted..."',
                "MKXP_Compatibility": "if !$ResizeInitialized\nend",
            }.items()
        ]

    def test_embedding_can_be_repeated_without_changing_engine_behavior(self):
        patched = patch_engine(self.stock(), "1.0.0")
        self.assertEqual(patched, patch_engine(patched, "1.0.0"))
        self.assertIn("Scene_TideboundTitle", zlib.decompress(patched[1][2]).decode())

    def test_changed_or_missing_engine_target_is_rejected(self):
        stock = self.stock()
        stock[1][2] = zlib.compress(b"return AnotherScene.new")
        with self.assertRaisesRegex(ValueError, "Unsupported engine patch target"):
            patch_engine(stock, "1.0.0")
        with self.assertRaisesRegex(ValueError, "stock engine script"):
            patch_engine(self.stock()[:-1], "1.0.0")
