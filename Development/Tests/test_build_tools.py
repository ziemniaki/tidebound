"""Regression checks for build failures that can hide drift or alter a checkout."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib

from rubymarshal.writer import writes

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))
from script_archive import validate_archive


def entry(name, code=""):
    return [1, name, zlib.compress(code.encode("utf-8"))]


class ArchiveChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.game = Path(self.temp.name)
        self.dev = self.game / "Development"
        self.dev.mkdir()
        (self.game / "Data").mkdir()
        (self.dev / "001_Core.rb").write_text("module Tidebound; end\n")
        (self.dev / "002_Adapter.rb").write_text("# adapter\n")
        self.entries = [entry("Settings"), entry("Tidebound/001_Core", "module Tidebound; end\n"),
                        entry("Tidebound/002_Adapter", "# adapter\n"),
                        entry("Main", "return Scene_TideboundTitle.new")]

    def validate(self):
        (self.game / "Data/Scripts.rxdata").write_bytes(writes(self.entries))
        return validate_archive(self.game, self.dev)

    def test_valid_archive(self):
        self.assertIn("Tidebound/001_Core", self.validate())

    def test_duplicate_custom_entry_is_rejected(self):
        self.entries.insert(1, entry("Tidebound/001_Core", "module Tidebound; end\n"))
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.validate()

    def test_custom_entries_after_main_are_rejected(self):
        self.entries.append(self.entries.pop(2))
        with self.assertRaisesRegex(ValueError, "immediately before Main"):
            self.validate()

    def test_wrong_order_is_rejected(self):
        self.entries[1], self.entries[2] = self.entries[2], self.entries[1]
        with self.assertRaisesRegex(ValueError, "filename order"):
            self.validate()

    def test_stale_source_is_rejected(self):
        (self.dev / "001_Core.rb").write_text("# edited but not embedded\n")
        with self.assertRaisesRegex(ValueError, "001_Core.rb"):
            self.validate()

    def test_missing_source_is_rejected(self):
        (self.dev / "002_Adapter.rb").unlink()
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.validate()

    def test_duplicate_main_is_rejected(self):
        self.entries.append(entry("Main", "return Scene_TideboundTitle.new"))
        with self.assertRaisesRegex(ValueError, "exactly one Main"):
            self.validate()

    def test_plugin_loading_path_is_rejected(self):
        (self.game / "Plugins/Tidebound").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "Plugins/Tidebound"):
            self.validate()


class CommandChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.game = Path(self.temp.name)
        self.dev = self.game / "Development"
        (self.dev / "Tests").mkdir(parents=True)
        (self.game / "Data").mkdir()

    def command(self, script, *flags):
        return subprocess.run([sys.executable, *flags, str(self.dev / script)],
                              cwd=self.game, capture_output=True, text=True)

    def test_rebuild_rejects_plugin_before_writing_even_with_optimization(self):
        for name in ("rebuild_scripts.py", "script_archive.py", "release_tools.py", "map_manifest.json"):
            shutil.copy2(DEV / name, self.dev / name)
        shutil.copy2(DEV.parent / "release.json", self.game / "release.json")
        for path in DEV.glob("[0-9][0-9][0-9]_*.rb"):
            shutil.copy2(path, self.dev / path.name)
        paths = ["Data/Scripts.rxdata", "Data/metadata.dat", "Game.ini", "mkxp.json",
                 "PBS/metadata.txt", "PBS/map_metadata.txt"]
        for name in paths:
            dest = self.game / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DEV.parent / name, dest)
        # Make a rebuild observable instead of relying on serializer differences.
        with (self.dev / "001_Core.rb").open("a") as source:
            source.write("\n# unembedded edit\n")
        before = {name: (self.game / name).read_bytes() for name in paths}
        (self.game / "Plugins/Tidebound").mkdir(parents=True)
        result = self.command("rebuild_scripts.py", "-O")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Plugins/Tidebound", result.stderr)
        self.assertEqual(before, {name: (self.game / name).read_bytes() for name in paths})

    def test_reference_refresh_removes_stale_indices(self):
        shutil.copy2(DEV / "Tests/prepare_reference.py", self.dev / "Tests/prepare_reference.py")
        ref = self.dev / "Tests/engine_reference"
        ref.mkdir()
        (ref / "000_Old.rb").write_text("# stale engine script")
        (self.game / "Data/Scripts.rxdata").write_bytes(writes([entry("New", "# current")]))
        result = self.command("Tests/prepare_reference.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([path.name for path in ref.iterdir()], ["000_New.rb"])
        self.assertEqual((ref / "000_New.rb").read_text(), "# current")

    def test_failed_reference_decode_preserves_previous_extraction(self):
        shutil.copy2(DEV / "Tests/prepare_reference.py", self.dev / "Tests/prepare_reference.py")
        ref = self.dev / "Tests/engine_reference"
        ref.mkdir()
        (ref / "000_Old.rb").write_text("# previous")
        (self.game / "Data/Scripts.rxdata").write_bytes(writes([[1, "Broken", b"not zlib"]]))
        result = self.command("Tests/prepare_reference.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((ref / "000_Old.rb").read_text(), "# previous")


if __name__ == "__main__":
    unittest.main()
