"""Retiring a declaration must remove only its outputs, including after failed builds."""

import json
from pathlib import Path
import tempfile
import unittest
from rubymarshal.classes import Symbol as S
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.content import ownership


class ContentOwnershipTests(unittest.TestCase):
    def test_retirement_preserves_stock_and_retry_replaces_partial_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "game/Data").mkdir(parents=True)
            (root / "game/PBS").mkdir()
            (root / "tools/generated").mkdir(parents=True)
            database = root / "game/Data/species.dat"
            retired = root / "game/PBS/pokemon_retired.txt"
            retired.write_text("old output")
            database.write_bytes(writes({S("STOCK"): 1, S("RETIRED"): 2}))
            manifest = root / ownership.MANIFEST
            manifest.write_text(
                json.dumps(
                    {
                        "databases": {"species.dat": ["RETIRED"]},
                        "files": ["game/PBS/pokemon_retired.txt"],
                    }
                )
            )
            expected = {"databases": {"species.dat": ["NEW"]}, "files": []}
            ownership.prepare(root, expected)
            self.assertEqual(loads(database.read_bytes()), {S("STOCK"): 1})
            self.assertFalse(retired.exists())
            database.write_bytes(writes({S("STOCK"): 1, S("NEW"): "partial build"}))
            ownership.prepare(root, expected)
            self.assertEqual(loads(database.read_bytes()), {S("STOCK"): 1})
            with self.assertRaisesRegex(ValueError, "overwrite stock"):
                ownership.prepare(root, {"databases": {"species.dat": ["STOCK"]}, "files": []})
            self.assertEqual(loads(database.read_bytes()), {S("STOCK"): 1})
