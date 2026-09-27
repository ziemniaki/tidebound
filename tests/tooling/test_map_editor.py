"""Editor saves survive a clean export, and concurrent authored work is never replaced."""

import json
import shutil
import struct
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from rubymarshal.classes import UserDef
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.maps import editor, tilesets
from tidebound_dev.maps.compiler import construct, BuildPaths
from tidebound_dev.maps.data import map_record, native_map, dump
from tidebound_dev.maps.model import command, obj

ROOT = Path(__file__).resolve().parents[2]


class MapEditorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "content/maps", self.root / "content/maps")
        shutil.copytree(ROOT / "content/tilesets", self.root / "content/tilesets")
        shutil.copytree(ROOT / "game/Data", self.root / "game/Data")
        shutil.copytree(ROOT / "game/Graphics/Tilesets", self.root / "game/Graphics/Tilesets")
        editor.remember(self.root)

    def test_saved_tiles_pages_routes_audio_and_collision_survive_export(self):
        path = self.root / "game/Data/Map101.rxdata"
        native = loads(path.read_bytes())
        source = map_record(native)
        self.assertNotEqual(source["data"]["rows"][0][0], source["data"]["rows"][10][6])
        source["data"]["rows"][0][0] = source["data"]["rows"][10][6]
        native = native_map(source)
        fields = native.attributes
        fields["@bgm"].attributes["@volume"] = 42
        event = fields["@events"][1].attributes
        event["@x"] += 1
        page = loads(writes(event["@pages"][0]))
        page.attributes["@condition"].attributes["@self_switch_valid"] = True
        page.attributes["@move_route"].attributes["@list"] = [
            obj("RPG::MoveCommand", code=1, parameters=[]),
            obj("RPG::MoveCommand", code=0, parameters=[]),
        ]
        tone = UserDef("Tone")
        tone._load(struct.pack("<4d", -10, 20, 30, 40))
        page.attributes["@list"] = [
            command(101, "Żółty Pokémon"),
            command(223, tone, 12),
            command(0),
        ]
        event["@pages"].append(page)
        path.write_bytes(writes(native))
        ts_path = self.root / "game/Data/Tilesets.rxdata"
        sets = loads(ts_path.read_bytes())
        ts = sets[fields["@tileset_id"]]
        record = map_record(native)
        tile = record["data"]["rows"][10][6]
        raw = bytearray(ts.attributes["@passages"]._dump())
        raw[20 + 2 * tile : 22 + 2 * tile] = (15).to_bytes(2, "little")
        ts.attributes["@passages"]._load(bytes(raw))
        ts_path.write_bytes(writes(sets))
        image_path = self.root / f"game/Graphics/Tilesets/{ts.attributes['@tileset_name']}.png"
        with Image.open(image_path) as sheet:
            image = sheet.convert("RGBA")
        image.putpixel((0, 0), (12, 34, 56, 255))
        image.save(image_path)
        with self.assertRaisesRegex(ValueError, "editor import"):
            editor.require_import(self.root)
        editor.import_changes(self.root)
        # Recreate both native records from authored inputs, not the edited binaries.
        tilesets.build(self.root)
        for export in tilesets.exports(self.root):
            export.write(self.root)
        with Image.open(image_path) as image:
            self.assertEqual(image.getpixel((0, 0)), (12, 34, 56, 255))
        saved = json.loads((self.root / "content/maps/home/layout.json").read_text())
        self.assertEqual(map_record(loads(writes(native_map(saved)))), map_record(native))
        self.assertEqual(loads(ts_path.read_bytes())[fields["@tileset_id"]], ts)
        home = construct(BuildPaths(self.root))[0]
        self.assertFalse(home.walk[10][6])
        before = (self.root / "content/maps/home/layout.json").read_bytes()
        editor.import_changes(self.root)
        self.assertEqual((self.root / "content/maps/home/layout.json").read_bytes(), before)

    def test_disjoint_edits_merge_and_same_field_conflict_writes_nothing(self):
        source_path = self.root / "content/maps/home/layout.json"
        path = self.root / "game/Data/Map101.rxdata"
        original = source_path.read_bytes()
        authored = json.loads(original)
        authored["events"]["1"]["name"] = "Source rename"
        source_path.write_text(dump(authored))
        native = loads(path.read_bytes())
        native.attributes["@events"][1].attributes["@x"] += 1
        path.write_bytes(writes(native))
        editor.import_changes(self.root)
        merged = json.loads(source_path.read_text())
        self.assertEqual(merged["events"]["1"]["name"], "Source rename")
        self.assertEqual(
            merged["events"]["1"]["x"], native.attributes["@events"][1].attributes["@x"]
        )
        # Import again without exporting the source-only rename to the editor.
        native.attributes["@bgm"].attributes["@volume"] = 31
        path.write_bytes(writes(native))
        editor.import_changes(self.root)
        merged = json.loads(source_path.read_text())
        self.assertEqual(merged["events"]["1"]["name"], "Source rename")
        self.assertEqual(merged["bgm"]["volume"], 31)
        merged["events"]["1"]["x"] += 1
        source_path.write_text(dump(merged))
        before = source_path.read_bytes()
        native.attributes["@events"][1].attributes["@x"] += 2
        path.write_bytes(writes(native))
        edited = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "conflict.*events/1/x"):
            editor.import_changes(self.root)
        self.assertEqual(source_path.read_bytes(), before)
        self.assertEqual(path.read_bytes(), edited)

    def test_new_event_keeps_its_id_and_deleted_ids_cannot_be_reused(self):
        path = self.root / "game/Data/Map101.rxdata"
        native = loads(path.read_bytes())
        events = native.attributes["@events"]
        eid = max(events) + 1
        event = loads(writes(events[1]))
        event.attributes.update({"@id": eid, "@name": "New event"})
        events[eid] = event
        path.write_bytes(writes(native))
        editor.import_changes(self.root)
        source = self.root / "content/maps/home/layout.json"
        self.assertEqual(json.loads(source.read_text())["events"][str(eid)]["id"], eid)
        del events[eid]
        path.write_bytes(writes(native))
        editor.import_changes(self.root)
        before = source.read_bytes()
        event.attributes["@name"] = "Another event"
        events[eid] = event
        path.write_bytes(writes(native))
        with self.assertRaisesRegex(ValueError, "reserved ID"):
            editor.import_changes(self.root)
        self.assertEqual(source.read_bytes(), before)

    def test_editor_scroll_changes_do_not_dirty_maps(self):
        path = self.root / "game/Data/MapInfos.rxdata"
        infos = loads(path.read_bytes())
        infos[101].attributes.update({"@scroll_x": 900, "@scroll_y": 600, "@expanded": False})
        path.write_bytes(writes(infos))
        editor.require_import(self.root)
