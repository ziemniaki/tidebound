"""Regression coverage for regional template resolution and family relationships."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import importlib

from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol as S

from tidebound_dev.content.species import SPECIES
from tidebound_dev.content.species_compiler import compile_records, native_field

ROOT = Path(__file__).resolve().parents[1]


class SpeciesCompilerTests(unittest.TestCase):
    def test_imports_do_not_export_art_or_read_game_data(self):
        with (
            patch("PIL.Image.open", side_effect=AssertionError("asset import read")),
            patch.object(Path, "write_bytes", side_effect=AssertionError("import write")),
            patch.object(Path, "read_bytes", side_effect=AssertionError("import read")),
        ):
            for module in (
                "content.species",
                "content.species_compiler",
                "art.frostcoon",
                "art.snakes",
                "art.whyduck",
            ):
                importlib.reload(importlib.import_module("tidebound_dev." + module))

    def test_templates_resolve_without_depending_on_definition_order(self):
        database = loads((ROOT / "game/Data/species.dat").read_bytes())
        originals = {
            key: writes(value)
            for key, value in database.items()
            if str(key).lstrip(":") not in SPECIES
        }
        # Remove compiled custom records; deriving from stale output must not be necessary.
        for name in SPECIES:
            del database[S(name)]
        compile_records(database, dict(reversed(SPECIES.items())))
        for key, original in originals.items():
            self.assertEqual(writes(database[key]), original)
        self.assertIn(
            [S("MOONFLORA"), S("Level"), 20, False],
            database[S("MOONKERN")].attributes["@evolutions"],
        )
        self.assertIn(
            [S("SUNKERN"), S("Level"), 14, True], database[S("MOONKERN")].attributes["@evolutions"]
        )
        self.assertEqual(
            database[S("FROSTCOON")].attributes["@evolutions"],
            [[S("NIVALORA"), S("Level"), 55, False], [S("WURMPLE"), S("Cascoon"), 10, True]],
        )

    def test_missing_template_and_cycles_have_explicit_errors(self):
        with self.assertRaisesRegex(ValueError, "Missing or cyclic"):
            compile_records({}, {"A": {"inherit": "B"}, "B": {"inherit": "A"}})

    def test_unknown_fields_and_invalid_stat_counts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported species field"):
            native_field("BaseStat", (1, 2, 3))
        with self.assertRaisesRegex(ValueError, "six positive values"):
            native_field("BaseStats", (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
