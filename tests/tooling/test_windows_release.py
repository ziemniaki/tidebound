from pathlib import Path
import json
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from functools import partial
from tidebound_dev.packaging.windows import RUNTIME_FILES, inspect_runtime
from tidebound_dev.packaging.pipeline import build as package

build = partial(package, "windows")
from tidebound_dev.files import sha256
from tidebound_dev.release.artifacts import verify


class WindowsReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "source"
        self.root.mkdir()
        self.output = self.base / "release"
        # Minimal PE header; these fixtures are never executed.
        pe = bytearray(160)
        pe[:2] = b"MZ"
        struct.pack_into("<I", pe, 0x3C, 64)
        pe[64:68] = b"PE\0\0"
        pe[68:70] = b"\x64\x86"
        pe[88:90] = b"\x0b\x02"
        for name in RUNTIME_FILES:
            (self.root / name).write_bytes(pe)
        self.config = {
            "version": "1.2.3",
            "windows_runtime_sha256": {name: sha256(self.root / name) for name in RUNTIME_FILES},
        }
        for name in (
            "Game.ini",
            "mkxp.json",
            "soundfont.sf2",
            "docs/credits.md",
            "docs/players/windows.txt",
            "docs/runtime/Windows.md",
            "Data/Scripts.rxdata",
            "tools/private.txt",
            ".venv/cache",
        ):
            file = self.root / (
                "game/" + name
                if name in ("Game.ini", "mkxp.json", "soundfont.sf2") or name.startswith("Data/")
                else name
            )
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b"fixture")
        for name, value in [
            ("windows_runtime", self.root),
            ("check_sources", self.config),
            ("source_revision", {"commit": "a" * 40, "dirty": False}),
        ]:
            patcher = patch(
                (
                    "tidebound_dev.packaging.windows."
                    if name == "windows_runtime"
                    else "tidebound_dev.packaging.pipeline."
                )
                + name,
                return_value=value,
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        self.enterContext(patch("tidebound_dev.packaging.pipeline.validate_assets"))
        self.enterContext(patch("tidebound_dev.packaging.pipeline.validate_content"))
        patcher = patch("tidebound_dev.packaging.pipeline.validate")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_player_zip_excludes_development_files_and_preserves_runtime(self):
        archive = build(self.output, self.root)
        with zipfile.ZipFile(archive) as z:
            prefix = "Tidebound_Windows_1.2.3_x64/"
            names = {name.removeprefix(prefix) for name in z.namelist()}
            self.assertIn("Data/Scripts.rxdata", names)
            self.assertIn("README.txt", names)
            self.assertFalse(any(name.startswith(("tools/", ".venv/")) for name in names))
            for name in RUNTIME_FILES:
                self.assertEqual(z.read(prefix + name), (self.root / name).read_bytes())
            manifest = json.loads(z.read(prefix + "BUILD.json"))
            self.assertEqual(set(manifest["files_sha256"]), names - {"BUILD.json"})
        verify(self.output)

    def test_declared_start_uses_scratch_saves_without_changing_source(self):
        from rubymarshal.writer import writes
        from tidebound_dev.runtime.config import parse_runtime_config, PLAYTEST_SAVES
        import zlib

        config = self.root / "game/mkxp.json"
        config.write_text('{"dataPathApp":"Tidebound_Opening_0_2"}')
        scripts = self.root / "game/Data/Scripts.rxdata"
        original = writes([[1, "Main", zlib.compress(b"normal title")]])
        scripts.write_bytes(original)
        spec = {"id": "test/state", "location": ["home", "start"]}
        launcher = build(self.output, self.root, development=True, start=spec)
        staged = parse_runtime_config((launcher.parent / "mkxp.json").read_text())
        self.assertEqual(staged["dataPathApp"], PLAYTEST_SAVES)
        manifest = json.loads((launcher.parent / "DEVELOPMENT.json").read_text())
        self.assertEqual(manifest["save_directory"], PLAYTEST_SAVES)
        self.assertTrue((launcher.parent / "Data/Scenario.rxdata").is_file())
        self.assertEqual(scripts.read_bytes(), original)
        self.assertEqual(
            parse_runtime_config(config.read_text())["dataPathApp"], "Tidebound_Opening_0_2"
        )

    def test_mutated_runtime_is_rejected_before_output(self):
        (self.root / "Game.exe").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "provenance hash mismatch"):
            build(self.output, self.root)
        self.assertFalse(self.output.exists())

    def test_non_x64_runtime_is_rejected_even_with_updated_hash(self):
        path = self.root / "Game.exe"
        data = bytearray(path.read_bytes())
        data[68:70] = b"\x64\xaa"  # ARM64
        path.write_bytes(data)
        self.config["windows_runtime_sha256"]["Game.exe"] = sha256(path)
        with self.assertRaisesRegex(ValueError, "x64 PE32"):
            inspect_runtime(self.root, self.config)

    def test_failed_zip_verification_cleans_staging(self):
        with patch(
            "tidebound_dev.packaging.pipeline.extract_bundle", side_effect=ValueError("bad ZIP")
        ):
            with self.assertRaisesRegex(ValueError, "bad ZIP"):
                build(self.output, self.root)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.base.glob(".tidebound-package-*")), [])

    def test_download_checksum_detects_corruption_and_unlisted_files(self):
        archive = build(self.output, self.root)
        unexpected = self.output / "unexpected.zip"
        unexpected.write_bytes(b"unknown")
        with self.assertRaisesRegex(ValueError, "complete candidate"):
            verify(self.output)
        unexpected.unlink()
        archive.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            verify(self.output)


if __name__ == "__main__":
    unittest.main()
