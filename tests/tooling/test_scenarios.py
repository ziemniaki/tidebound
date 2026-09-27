"""Invalid fixtures fail before staging; native checks own engine startup semantics."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zlib
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev import scenarios
from tidebound_dev.paths import ROOT
from tidebound_dev.packaging.pipeline import build


class ScenarioTests(unittest.TestCase):
    def test_resolves_base_state_and_rejects_broken_references(self):
        spec = scenarios.select(ROOT, "neighbor/return_necklace")
        self.assertEqual(spec["story"]["walk_state"], ":complete")
        self.assertEqual(spec["story"]["neighbor_quest"]["stage"], ":necklace")
        self.assertEqual(spec["bag"], {"TIDEBOUNDNECKLACE": 1})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            paths = {**scenarios.catalog(ROOT), "test/bad": path}
            for changes in (
                {"location": ["shop", "missing"]},
                {"party": ["missing"]},
                {"bag": {"NOT_AN_ITEM": 1}},
                {"party": [{"species": "NOT_A_SPECIES", "level": 7}]},
                {"stroy": {}},
                {"base": "neighbor/meal"},
            ):
                with self.subTest(changes=changes):
                    path.write_text(json.dumps({"base": "opening/exploration", **changes}))
                    with patch.object(scenarios, "catalog", return_value=paths):
                        with self.assertRaisesRegex(ValueError, "Scenario test/bad"):
                            scenarios.select(ROOT, "test/bad")

    def test_driver_replaces_only_main_and_cannot_be_packaged_as_release(self):
        spec = scenarios.select(ROOT, "neighbor/meal")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Data").mkdir()
            entries = [
                [1, "Engine", zlib.compress(b"engine")],
                [2, "Main", zlib.compress(b"title")],
            ]
            archive = root / "Data/Scripts.rxdata"
            archive.write_bytes(writes(entries))
            scenarios.prepare(root, spec)
            compiled = loads(archive.read_bytes())
            self.assertEqual(compiled[0], entries[0])
            self.assertIn(b"DevelopmentScenario.run", zlib.decompress(compiled[1][2]))
            self.assertEqual(
                loads((root / "Data/Scenario.rxdata").read_bytes())["arrival"], spec["arrival"]
            )
            with self.assertRaisesRegex(ValueError, "development only"):
                build("windows", root / "release", start=spec)
