"""The installed operation package must be safe to import and share one plan."""

import importlib
from pathlib import Path
import unittest
import tempfile
import shutil
from contextlib import ExitStack
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from rubymarshal.classes import Symbol
from unittest.mock import patch

from tidebound_dev import pipeline


class PythonPackageTests(unittest.TestCase):
    def test_core_operations_import_without_game_io(self):
        with (
            patch.object(Path, "read_bytes", side_effect=AssertionError("import read")),
            patch.object(Path, "write_bytes", side_effect=AssertionError("import write")),
            patch.object(Path, "read_text", side_effect=AssertionError("import read")),
            patch.object(Path, "write_text", side_effect=AssertionError("import write")),
        ):
            for module in (
                "pipeline",
                "content.opening_items",
                "content.quest_data",
                "content.configure",
                "content.encounters",
                "checks.rebuild",
                "release.candidates",
                "packaging.pipeline",
            ):
                importlib.reload(importlib.import_module("tidebound_dev." + module))

    def test_script_only_rebuild_does_not_load_or_regenerate_maps(self):
        root = Path("/disposable/source")
        with (
            patch.object(pipeline, "maps", side_effect=AssertionError("map regeneration")),
            patch.object(pipeline, "scripts") as embed,
        ):
            pipeline.rebuild(root)
        embed.assert_called_once_with(root)


class RebuildDependenciesTests(unittest.TestCase):
    def test_new_species_and_encounter_build_together_from_clean_data(self):
        from tidebound_dev.content import species_compiler, encounters

        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp, ExitStack() as patches:
            root = Path(temp)
            (root / "game/Data").mkdir(parents=True)
            (root / "game/PBS").mkdir()
            for name in ("species", "species_metrics", "moves", "abilities", "encounters"):
                shutil.copy2(source / f"game/Data/{name}.dat", root / f"game/Data/{name}.dat")
            new_species = "NEWBIRD"
            self.assertNotIn(
                Symbol(new_species), loads((root / "game/Data/species.dat").read_bytes())
            )
            definitions = dict(species_compiler.SPECIES)
            definitions[new_species] = {
                "inherit": "NATU",
                "file": "pokemon_test",
                "fields": {"Name": "New bird"},
            }
            patches.enter_context(patch.object(species_compiler, "SPECIES", definitions))
            patches.enter_context(patch.object(species_compiler, "export_art"))
            patches.enter_context(
                patch.object(
                    encounters,
                    "ROSTERS",
                    {
                        103: [(100, new_species, 3, 5)],
                        108: [(100, "PSYDUCK", 4, 6)],
                    },
                )
            )
            for name in ("maps", "scripts", "validate"):
                patches.enter_context(patch.object(pipeline, name))
            for module in (pipeline.opening_items, pipeline.quest_data, pipeline.configure):
                patches.enter_context(patch.object(module, "build"))
            pipeline.rebuild(root, full=True)
            result = loads((root / "game/Data/encounters.dat").read_bytes())
            self.assertEqual(
                result[Symbol("103_0")].attributes["@types"][Symbol("Land")][0][1],
                Symbol(new_species),
            )
