"""Exercise the map validator against disposable compiled-map fixtures."""

from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.maps.validate import validate
from tidebound_dev.maps.data import map_record, native_map
from tidebound_dev.maps.model import command, obj, table
import json

ROOT = Path(__file__).resolve().parents[2]


class MapValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / "game"
        for name in (
            "game/.generated/collisions.json",
            "game/.generated/map_manifest.json",
            "game/.generated/maze_manifest.json",
            "game/Data/Scripts.rxdata",
            "game/Data/map_metadata.dat",
            "game/Data/Tilesets.rxdata",
        ):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
        shutil.copytree(ROOT / "content/maps", self.root / "content/maps")
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

    def test_missing_bgm_is_rejected(self):
        next((self.game / "Audio/BGM").glob("*.ogg")).unlink()
        with self.assertRaisesRegex(RuntimeError, "missing BGM"):
            validate(self.root)

    def test_directional_corridor_accepts_arrivals_but_blocks_forbidden_edges(self):
        path = self.game / "Data/Map101.rxdata"
        native = loads(path.read_bytes())
        event = native.attributes["@events"][1]
        event.attributes.update({"@x": 1, "@y": 4, "@name": "Corridor exit"})
        page = event.attributes["@pages"][0]
        event.attributes["@pages"] = [page]
        page.attributes.update(
            {"@trigger": 1, "@list": [command(201, 0, 101, 1, 1, 2, 0), command(0)]}
        )
        native.attributes["@events"] = {1: event}
        record = map_record(native)
        record.update(width=3, height=5, tileset_id=1)
        record["data"] = {
            "$type": "Table",
            "shape": [3, 5, 3],
            "rows": [[384, 385, 384] for _ in range(5)] + [[0, 0, 0] for _ in range(10)],
        }
        path.write_bytes(writes(native_map(record)))
        declaration = self.root / "content/maps/home/map.json"
        metadata = json.loads(declaration.read_text())
        metadata["entrances"] = {}
        declaration.write_text(json.dumps(metadata))
        (self.game / ".generated/map_manifest.json").write_text(
            json.dumps([{"id": 101, "width": 3, "height": 5}])
        )
        # Scripted movement masks are deliberately conservative: this corridor
        # is not fully passable, but normal north/south movement is legal.
        (self.game / ".generated/collisions.json").write_text(json.dumps({"101": ["000"] * 5}))
        passages = [0] * 386
        passages[384], passages[385] = 15, 4
        tileset = obj(
            "RPG::Tileset",
            id=1,
            passages=table(passages, 386),
            priorities=table([0] * 386, 386),
            terrain_tags=table([0] * 386, 386),
        )
        tilesets = self.game / "Data/Tilesets.rxdata"
        tilesets.write_bytes(writes([None, tileset]))
        validate(self.root)
        # Blocking southward movement must not turn into a false successful flood fill.
        passages[385] = 1
        tileset.attributes["@passages"] = table(passages, 386)
        tilesets.write_bytes(writes([None, tileset]))
        with self.assertRaisesRegex(RuntimeError, "Corridor exit/page1 unreachable event"):
            validate(self.root)

    def test_wma_cannot_satisfy_native_map_audio(self):
        path = self.game / "Data/Map101.rxdata"
        native = loads(path.read_bytes())
        native.attributes["@autoplay_bgm"] = True
        self.asset("Audio/BGM/Unsupported.wma")
        for name in ("Unsupported", "Unsupported.wma"):
            native.attributes["@bgm"].attributes["@name"] = name
            path.write_bytes(writes(native))
            with self.assertRaisesRegex(RuntimeError, "missing BGM"):
                validate(self.root)
        native.attributes["@bgm"].attributes["@name"] = "Unsupported"
        path.write_bytes(writes(native))
        self.asset("Audio/BGM/Unsupported.ogg")
        validate(self.root)

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

                    masks = self.root / "game/.generated/collisions.json"
                    data = json.loads(masks.read_text())
                    data["101"][0] = data["101"][0][:-1]
                    masks.write_text(json.dumps(data))
                path.write_bytes(writes(record))
                with self.assertRaisesRegex(RuntimeError, "dimensions"):
                    validate(self.root)

    def test_editor_map_can_be_silent_or_use_native_audio_without_named_entrances(self):
        path = self.game / "Data/Map101.rxdata"
        native = loads(path.read_bytes())
        native.attributes["@autoplay_bgm"] = False
        native.attributes["@bgm"].attributes["@name"] = ""
        native.attributes["@events"] = {}
        path.write_bytes(writes(native))
        import json

        manifest = self.game / ".generated/map_manifest.json"
        manifest.write_text(
            json.dumps([m for m in json.loads(manifest.read_text()) if m["id"] == 101])
        )
        declaration = self.root / "content/maps/home/map.json"
        data = json.loads(declaration.read_text())
        data["entrances"] = {}
        declaration.write_text(json.dumps(data))
        validate(self.root)
        native.attributes["@autoplay_bgm"] = True
        native.attributes["@bgm"].attributes["@name"] = "Editor track"
        path.write_bytes(writes(native))
        self.asset("Audio/BGM/Editor track.mid")
        validate(self.root)
