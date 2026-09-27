"""A new species must compile before its encounter roster in the same rebuild."""

from pathlib import Path
import json
import unittest
import tempfile
import shutil
from contextlib import ExitStack
from rubymarshal.reader import loads
from rubymarshal.classes import Symbol
from unittest.mock import patch

from tidebound_dev import pipeline


class RebuildDependenciesTests(unittest.TestCase):
    def test_new_species_and_encounter_build_together_from_clean_data(self):
        from tidebound_dev.content import species_compiler

        source = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp, ExitStack() as patches:
            root = Path(temp)
            (root / "game/Data").mkdir(parents=True)
            (root / "game/PBS").mkdir()
            (root / "src/generated").mkdir(parents=True)
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
            patches.enter_context(patch.object(pipeline.workspace, "prepare"))
            patches.enter_context(patch.object(pipeline.workspace, "validate_overrides"))
            patches.enter_context(patch.object(pipeline.editor, "require_import"))
            patches.enter_context(patch.object(pipeline.art, "build"))
            patches.enter_context(patch.object(pipeline.editor, "remember"))
            bundle = root / "content/maps/forest"
            bundle.mkdir(parents=True)
            (bundle / "map.json").write_text(
                json.dumps(
                    {
                        "id": 103,
                        "encounters": {"Land": {"chance": 18, "slots": [[100, new_species, 3, 5]]}},
                    }
                )
            )
            patches.enter_context(patch.object(pipeline.ownership, "prepare"))
            for name in ("maps", "scripts", "validate"):
                patches.enter_context(patch.object(pipeline, name))
            for module in (pipeline.story, pipeline.configure, pipeline.map_features):
                patches.enter_context(patch.object(module, "build"))
            pipeline.rebuild(root)
            result = loads((root / "game/Data/encounters.dat").read_bytes())
            self.assertEqual(
                result[Symbol("103_0")].attributes["@types"][Symbol("Land")][0][1],
                Symbol(new_species),
            )
