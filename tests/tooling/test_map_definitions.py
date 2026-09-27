"""An ordinary new map must not need independent metadata/atmosphere tables."""

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from rubymarshal.reader import loads
from rubymarshal.classes import Symbol

from tidebound_dev.maps import registry, model, serialization, definitions
from tidebound_dev.maps.compiler import AuthoredMap
from tidebound_dev.maps.definitions import MapDefinition
from tidebound_dev.maps.compiler import BuildPaths
from tidebound_dev.content import configure

ROOT = Path(__file__).resolve().parents[2]


class MapDefinitionTests(unittest.TestCase):
    def test_new_indoor_map_has_consistent_native_pbs_audio_and_runtime_settings(self):
        definition = MapDefinition(
            117, {"entry": [1, 1, 2]}, name="New room", battleback="cave1", environment="Cave"
        )
        import json

        record = json.loads((ROOT / "content/maps/home/layout.json").read_text())
        record.update(width=3, height=3, tileset_id=1, events={})
        record["data"] = {"$type": "Table", "shape": [3, 3, 3], "rows": [[0] * 3 for _ in range(9)]}
        record["bgm"]["name"] = "New room"
        tileset = loads((ROOT / "game/Data/Tilesets.rxdata").read_bytes())[1]
        area = AuthoredMap(definition, record, tileset)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (
                "game/Data/System.rxdata",
                "game/Data/Tilesets.rxdata",
                "game/Data/MapInfos.rxdata",
                "game/Data/map_metadata.dat",
                "game/Data/metadata.dat",
                "game/Game.ini",
                "game/mkxp.json",
                "game/PBS/metadata.txt",
                "game/PBS/map_metadata.txt",
            ):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, target)
            (root / "src/generated").mkdir(parents=True)
            (root / "game/.generated").mkdir(parents=True)
            with (
                patch.dict(registry.DEFINITIONS, {"new_room": definition}, clear=True),
                patch.dict(registry.MAPS, {"new_room": 117}, clear=True),
                patch.dict(registry.ACTORS, {}, clear=True),
                patch.dict(definitions.BY_ID, {117: definition}, clear=True),
            ):
                serialization.serialize(BuildPaths(root), [area])
                configure.build(root)
            system = loads((root / "game/Data/System.rxdata").read_bytes())
            revision = system.attributes["@magic_number"]
            self.assertEqual(revision, serialization.map_revision(root / "game"))
            tilesets = root / "game/Data/Tilesets.rxdata"
            original = tilesets.read_bytes()
            tilesets.write_bytes(original + b"changed packing")
            self.assertNotEqual(revision, serialization.map_revision(root / "game"))
            tilesets.write_bytes(original)
            area_file = root / "game/Data/Map117.rxdata"
            original = area_file.read_bytes()
            area_file.write_bytes(original + b"changed layout")
            self.assertNotEqual(revision, serialization.map_revision(root / "game"))
            area_file.write_bytes(original)
            native = loads((root / "game/Data/map_metadata.dat").read_bytes())[117].attributes
            self.assertEqual(native["@battle_environment"], Symbol("Cave"))
            self.assertEqual(native["@battle_background"], "cave1")
            self.assertFalse(native["@outdoor_map"])
            pbs = (root / "game/PBS/map_metadata.txt").read_text()
            self.assertIn(
                "[117]\nName = New room\nShowArea = true\nBattleBack = cave1\nEnvironment = Cave",
                pbs,
            )
            compiled_map = loads((root / "game/Data/Map117.rxdata").read_bytes())
            self.assertEqual(compiled_map.attributes["@bgm"].attributes["@name"], "New room")
            runtime = (root / "src/generated/world_registry.rb").read_text()
            self.assertIn('117 => {tone: [-8, -14, -25, 12], fog: "", opacity: 0', runtime)
            self.assertEqual(definition.arrivals, ((1, 1),))

    def test_unknown_atmosphere_and_missing_arrivals_fail_at_definition(self):
        with self.assertRaisesRegex(ValueError, "arrival"):
            MapDefinition(117, {})
        with self.assertRaisesRegex(ValueError, "atmosphere"):
            MapDefinition(117, {"entry": [1, 1, 2]}, atmosphere="unregistered")
