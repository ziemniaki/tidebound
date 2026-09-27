"""Shared fixture isolation is checked before any platform launcher runs."""

from pathlib import Path
import tempfile
import unittest
import zlib
import json
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tests.native.native_fixture import prepare
from unittest.mock import patch
from tidebound_dev.content import verification


class NativeFixtureTests(unittest.TestCase):
    def test_invalid_main_preserves_configuration_and_archive(self):
        for entries in ([], [[1, "Main", b"x"], [2, "Main", b"y"]]):
            with self.subTest(entries=entries), tempfile.TemporaryDirectory() as temp:
                game = Path(temp)
                (game / "Data").mkdir()
                config = game / "mkxp.json"
                config.write_text('{"dataPathApp":"player"}')
                scripts = game / "Data/Scripts.rxdata"
                original = writes(entries)
                scripts.write_bytes(original)
                with self.assertRaisesRegex(ValueError, "exactly one Main"):
                    prepare(game, "Tidebound_Build_Smoke_" + "a" * 32)
                self.assertEqual(config.read_text(), '{"dataPathApp":"player"}')
                self.assertEqual(scripts.read_bytes(), original)

    def test_only_main_and_namespace_change(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp)
            (game / "Data").mkdir()
            (game / "mkxp.json").write_text('{"dataPathApp":"player", "fontHeightReporting":1}')
            scripts = game / "Data/Scripts.rxdata"
            original = [
                [1, "Engine", zlib.compress(b"engine")],
                [2, "Main", zlib.compress(b"main")],
            ]
            scripts.write_bytes(writes(original))
            prepare(game, "Tidebound_Build_Smoke_" + "a" * 32, "all")
            actual = loads(scripts.read_bytes())
            self.assertEqual(actual[0], original[0])
            self.assertTrue((game / "NativePBS/pokemon.txt").is_file())
            self.assertIn("species", loads((game / "NativeContent.rxdata").read_bytes()))
            self.assertIn(b"TIDEBOUND_NATIVE_SCENARIO = :all", zlib.decompress(actual[1][2]))
            self.assertEqual(json.loads((game / "mkxp.json").read_text())["fontHeightReporting"], 1)

    def test_player_namespace_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique test namespace"):
            prepare(Path("/unused"), "Tidebound_Development")


class ContentInventoryTests(unittest.TestCase):
    def test_new_species_derives_native_expectations(self):
        with patch.object(verification, "SPECIES", {"NEWBIRD": {}, "NEWBIRD_1": {}}):
            result = verification.inventory()
        self.assertEqual(result["species"], ["NEWBIRD", "NEWBIRD_1"])
        self.assertEqual([entry["id"] for entry in result["art"]], ["NEWBIRD", "NEWBIRD_1"])
        self.assertEqual(
            result["art"][1]["front_shiny"], "Graphics/Pokemon/Front shiny/NEWBIRD_1.png"
        )
        self.assertEqual(result["art"][1]["cry"], "Cries/NEWBIRD_1")
