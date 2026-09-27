"""Shared fixture isolation is checked before any platform launcher runs."""

from pathlib import Path
import tempfile
import unittest
import zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from native_fixture import prepare
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
            prepare(game, "Tidebound_Build_Smoke_" + "a" * 32, "world")
            actual = loads(scripts.read_bytes())
            self.assertEqual(actual[0], original[0])
            self.assertIn(b"TIDEBOUND_NATIVE_SCENARIO = :world", zlib.decompress(actual[1][2]))
            self.assertIn('"fontHeightReporting":1', (game / "mkxp.json").read_text())

    def test_player_namespace_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique test namespace"):
            prepare(Path("/unused"), "Tidebound_Development")


class ContentInventoryTests(unittest.TestCase):
    def test_new_species_is_checked_without_a_second_roster_or_existing_art(self):
        with patch.object(verification, "SPECIES", {"NEWBIRD": {}, "NEWBIRD_1": {}}):
            result = verification.inventory()
        self.assertEqual(result["species"], ["NEWBIRD", "NEWBIRD_1"])
        self.assertEqual([entry["id"] for entry in result["art"]], ["NEWBIRD", "NEWBIRD_1"])
        self.assertEqual(
            result["art"][1]["front_shiny"], "Graphics/Pokemon/Front shiny/NEWBIRD_1.png"
        )
        self.assertEqual(result["art"][1]["cry"], "Cries/NEWBIRD_1")

    def test_existing_cry_reuse_is_explicit(self):
        entry = next(
            entry for entry in verification.inventory()["art"] if entry["id"] == "SUNKERN_1"
        )
        self.assertEqual(entry["cry"], "Cries/SUNKERN")
