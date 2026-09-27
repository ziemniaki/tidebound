"""Editor saves survive a clean export, and concurrent authored work is never replaced."""

import json
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
from contextlib import ExitStack
from tidebound_dev import pipeline
from tidebound_dev.content import ownership
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
        saved = json.loads(
            (self.root / "content/maps/home/layout.json").read_bytes().decode("utf-8")
        )
        self.assertEqual(map_record(loads(writes(native_map(saved)))), map_record(native))
        self.assertEqual(loads(ts_path.read_bytes())[fields["@tileset_id"]], ts)
        home = construct(BuildPaths(self.root))[0]
        self.assertFalse(home.walk[10][6])
        editor.remember(self.root)  # Manual exports above complete this build.
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
        # A source-only new map must not be read as an already-exported native map.
        added = self.root / "content/maps/agent_room"
        added.mkdir()
        (added / "map.json").write_text('{"id": 118, "name": "Agent room"}')
        (added / "layout.json").write_text(dump(authored))
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

    def test_stock_map_and_tileset_edits_import_without_capturing_authored_records(self):
        path = self.root / "game/Data/Map001.rxdata"
        native = loads(path.read_bytes())
        native.attributes["@bgm"].attributes["@volume"] = 41
        path.write_bytes(writes(native))
        infos_path = self.root / "game/Data/MapInfos.rxdata"
        infos = loads(infos_path.read_bytes())
        infos[1].attributes["@name"] = "Stock map renamed"
        infos_path.write_bytes(writes(infos))
        sets_path = self.root / "game/Data/Tilesets.rxdata"
        sets = loads(sets_path.read_bytes())
        sets[1].attributes["@name"] = "Stock tileset renamed"
        sets_path.write_bytes(writes(sets))
        with self.assertRaisesRegex(ValueError, "editor import"):
            editor.require_import(self.root)
        editor.import_changes(self.root)
        overrides = self.root / "content/overrides/Data"
        self.assertEqual(loads((overrides / path.name).read_bytes()), native)
        imported_infos = loads((overrides / "MapInfos.rxdata").read_bytes())
        self.assertEqual(imported_infos[1].attributes["@name"], "Stock map renamed")
        self.assertNotIn(101, imported_infos)
        imported_sets = loads((overrides / "Tilesets.rxdata").read_bytes())
        self.assertEqual(imported_sets[1].attributes["@name"], "Stock tileset renamed")
        self.assertLessEqual(len(imported_sets), 26)
        editor.require_import(self.root)

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
        with self.assertRaisesRegex(ValueError, "retired event IDs"):
            editor.import_changes(self.root)
        self.assertEqual(source.read_bytes(), before)

    def test_editor_scroll_changes_do_not_dirty_maps(self):
        path = self.root / "game/Data/MapInfos.rxdata"
        infos = loads(path.read_bytes())
        infos[101].attributes.update({"@scroll_x": 900, "@scroll_y": 600, "@expanded": False})
        path.write_bytes(writes(infos))
        editor.require_import(self.root)

    def test_reordered_commands_conflict_with_concurrent_source_edits(self):
        path = self.root / "game/Data/Map101.rxdata"
        native = loads(path.read_bytes())
        page = native.attributes["@events"][1].attributes["@pages"][0].attributes
        page["@list"] = [command(121, 1, 1, 0), command(121, 2, 2, 0), command(0)]
        path.write_bytes(writes(native))
        source = self.root / "content/maps/home/layout.json"
        source.write_text(dump(map_record(native)))
        editor.remember(self.root)
        authored = json.loads(source.read_text())
        authored["events"]["1"]["pages"][0]["list"][1]["parameters"][2] = 1
        source.write_text(dump(authored))
        page["@list"][0], page["@list"][1] = page["@list"][1], page["@list"][0]
        path.write_bytes(writes(native))
        before = source.read_bytes()
        with self.assertRaisesRegex(ValueError, "conflict.*events/1/pages"):
            editor.import_changes(self.root)
        self.assertEqual(source.read_bytes(), before)

    def test_disjoint_tile_edits_keep_their_coordinates(self):
        path = self.root / "game/Data/Map101.rxdata"
        source = self.root / "content/maps/home/layout.json"
        authored = json.loads(source.read_text())
        native = map_record(loads(path.read_bytes()))
        authored["data"]["rows"][0][0] = 384
        native["data"]["rows"][0][1] = 385
        source.write_text(dump(authored))
        path.write_bytes(writes(native_map(native)))
        editor.import_changes(self.root)
        self.assertEqual(json.loads(source.read_text())["data"]["rows"][0][:2], [384, 385])

    def test_editor_created_map_becomes_authored_content_with_its_native_id(self):
        path = self.root / "game/Data/Map117.rxdata"
        record = json.loads((self.root / "content/maps/home/layout.json").read_text())
        record["events"] = {}
        path.write_bytes(writes(native_map(record)))
        info_path = self.root / "game/Data/MapInfos.rxdata"
        infos = loads(info_path.read_bytes())
        infos[117] = obj(
            "RPG::MapInfo",
            name="New room!",
            parent_id=101,
            order=17,
            expanded=False,
            scroll_x=0,
            scroll_y=0,
        )
        info_path.write_bytes(writes(infos))
        with self.assertRaisesRegex(ValueError, "New native map 117"):
            editor.require_import(self.root)
        editor.import_changes(self.root)
        bundle = self.root / "content/maps/new_room"
        self.assertEqual(
            json.loads((bundle / "map.json").read_text()),
            {"id": 117, "name": "New room!", "entrances": {}, "parent_id": 101, "order": 17},
        )
        shutil.copytree(ROOT / "game/.generated", self.root / "game/.generated")
        ownership.prepare(self.root, ownership.inventory(self.root))
        area = next(a for a in construct(BuildPaths(self.root)) if a.id == 117)
        self.assertEqual(map_record(loads(area.serialize())), record)
        editor.require_import(self.root)
        # A simultaneous source addition must not be silently assigned a second bundle.
        infos[118] = infos[117]
        info_path.write_bytes(writes(infos))
        (self.root / "game/Data/Map118.rxdata").write_bytes(path.read_bytes())
        source = self.root / "content/maps/agent_room"
        source.mkdir()
        (source / "map.json").write_text('{"id": 118, "name": "Agent room"}')
        before = (bundle / "layout.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "ID already used"):
            editor.import_changes(self.root)
        self.assertEqual((bundle / "layout.json").read_bytes(), before)
        self.assertFalse((self.root / "content/maps/new_room_118").exists())

    @patch.object(pipeline.workspace, "prepare")
    @patch.object(pipeline.workspace, "validate_overrides")
    def test_pending_edits_are_guarded_but_failed_exports_do_not_block_retry(self, *_):
        path = self.root / "game/Data/Map101.rxdata"
        native = loads(path.read_bytes())
        native.attributes["@bgm"].attributes["@volume"] = 42
        path.write_bytes(writes(native))
        with self.assertRaisesRegex(ValueError, "editor import"):
            pipeline.rebuild(self.root)
        editor.import_changes(self.root)
        saved = (self.root / "content/maps/home/layout.json").read_bytes()

        def failed_export(root):
            native.attributes["@bgm"].attributes["@volume"] = 12
            path.write_bytes(writes(native))
            raise RuntimeError("export failed")

        with patch.object(pipeline.art, "build", side_effect=failed_export):
            for _ in range(2):
                with self.assertRaisesRegex(RuntimeError, "export failed"):
                    pipeline.rebuild(self.root)
        self.assertEqual((self.root / "content/maps/home/layout.json").read_bytes(), saved)

        # Even a failure at the last validation step must leave no checkpoint.
        path.write_bytes(writes(native_map(json.loads(saved))))
        with ExitStack() as stages:
            for module in (
                pipeline.art,
                pipeline.map_features,
                pipeline.story,
                pipeline.species_compiler,
                pipeline.encounters,
                pipeline.configure,
            ):
                stages.enter_context(patch.object(module, "build"))
            stages.enter_context(patch.object(pipeline.ownership, "prepare"))
            for name in ("maps", "scripts"):
                stages.enter_context(patch.object(pipeline, name))
            validate = stages.enter_context(
                patch.object(pipeline, "validate", side_effect=RuntimeError("invalid compiled map"))
            )
            with self.assertRaisesRegex(RuntimeError, "invalid compiled map"):
                pipeline.rebuild(self.root)
            self.assertFalse((self.root / editor.SESSION).exists())
            validate.side_effect = None
            pipeline.rebuild(self.root)
        editor.require_import(self.root)
        native = loads(path.read_bytes())
        native.attributes["@bgm"].attributes["@volume"] = 31
        path.write_bytes(writes(native))
        with self.assertRaisesRegex(ValueError, "editor import"):
            pipeline.rebuild(self.root)
        editor.import_changes(self.root)
        self.assertEqual(
            json.loads((self.root / "content/maps/home/layout.json").read_text())["bgm"]["volume"],
            31,
        )
