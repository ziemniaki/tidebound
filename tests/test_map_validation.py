"""Exercise the map validator against disposable compiled-map fixtures."""

from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from rubymarshal.reader import loads
from rubymarshal.writer import writes

ROOT = Path(__file__).resolve().parents[1]


class MapValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / "game"
        for name in (
            "tools/generated/collisions.json",
            "tools/generated/map_manifest.json",
            "tools/generated/maze_manifest.json",
            "game/Data/Scripts.rxdata",
            "game/Data/map_metadata.dat",
        ):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
        shutil.copytree(ROOT / "src", self.root / "src")
        for original in (ROOT / "game/Data").glob("Map1[01][0-9].rxdata"):
            shutil.copy2(original, self.game / "Data" / original.name)
            data = loads(original.read_bytes()).attributes
            self.asset("Audio/BGM/" + str(data["@bgm"].attributes["@name"]) + ".ogg")
            for event in data["@events"].values():
                for page in event.attributes["@pages"]:
                    name = str(page.attributes["@graphic"].attributes["@character_name"])
                    if name:
                        self.asset("Graphics/Characters/" + name + ".png")
        metadata = loads((self.game / "Data/map_metadata.dat").read_bytes())
        for mid in range(101, 117):
            back = str(metadata[mid].attributes["@battle_background"])
            for suffix in ("_bg", "_base0", "_base1", "_message"):
                self.asset("Graphics/Battlebacks/" + back + suffix + ".png")

    def asset(self, name):
        path = self.game / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def validate(self, optimized=False):
        return subprocess.run(
            [
                sys.executable,
                *(["-O"] if optimized else []),
                "-c",
                "import sys; from pathlib import Path; from tidebound_dev.maps.validate import validate; validate(Path(sys.argv[1]))",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )

    def test_intact_fixture_passes_with_or_without_optimization(self):
        for optimized in (False, True):
            result = self.validate(optimized)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_bgm_fails_even_when_python_is_optimized(self):
        next((self.game / "Audio/BGM").glob("*.ogg")).unlink()
        for optimized in (False, True):
            result = self.validate(optimized)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("missing BGM", result.stderr)

    def test_serialized_map_and_tile_table_dimensions_must_match_manifest(self):
        path = self.game / "Data/Map101.rxdata"
        original = path.read_bytes()
        for changed in ("width", "table", "mask"):
            with self.subTest(changed=changed):
                record = loads(original)
                if changed == "width":
                    record.attributes["@width"] -= 1
                elif changed == "table":
                    table = record.attributes["@data"]
                    raw = table._dump()
                    header = list(struct.unpack("<5i", raw[:20]))
                    header[1] -= 1
                    table._load(struct.pack("<5i", *header) + raw[20:])
                else:
                    import json

                    masks = self.root / "tools/generated/collisions.json"
                    data = json.loads(masks.read_text())
                    data["101"][0] = data["101"][0][:-1]
                    masks.write_text(json.dumps(data))
                path.write_bytes(writes(record))
                result = self.validate()
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("dimensions", result.stderr)
