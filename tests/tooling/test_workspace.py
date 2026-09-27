"""Clean assembly removes stale output; native editor changes remain authored inputs."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev import workspace
from tidebound_dev.art import compiler
from tidebound_dev.maps import editor
from tidebound_dev.maps.model import obj
from PIL import Image


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        baseline = self.root / "runtime/essentials/base.zip"
        baseline.parent.mkdir(parents=True)
        with zipfile.ZipFile(baseline, "w") as archive:
            archive.writestr("Data/MapInfos.rxdata", writes({}))
            archive.writestr("Data/Tilesets.rxdata", writes([None]))
            archive.writestr(
                "Data/System.rxdata",
                writes(
                    obj("RPG::System", magic_number=0, start_map_id=1, switches=[None, "Original"])
                ),
            )
            archive.writestr("Audio/BGM/stock.ogg", b"stock")
        baseline.with_suffix(".json").write_text(
            json.dumps({"sha256": hashlib.sha256(baseline.read_bytes()).hexdigest()})
        )
        workspace.prepare(self.root)
        editor.remember(self.root)

    def test_native_edit_import_survives_fresh_build_and_concurrent_override_conflicts(self):
        target = self.root / "game/Data/System.rxdata"
        system = loads(target.read_bytes())
        system.attributes["@switches"][1] = "Quest switch"
        target.write_bytes(writes(system))
        with self.assertRaisesRegex(ValueError, "editor import"):
            editor.require_import(self.root)
        editor.import_changes(self.root)
        workspace.prepare(self.root)
        self.assertEqual(loads(target.read_bytes()).attributes["@switches"][1], "Quest switch")
        editor.remember(self.root)
        source = self.root / "content/overrides/Data/System.rxdata"
        system.attributes["@switches"][1] = "Source edit"
        source.write_bytes(writes(system))
        before = source.read_bytes()
        system.attributes["@switches"][1] = "Editor edit"
        target.write_bytes(writes(system))
        with self.assertRaisesRegex(ValueError, "conflict"):
            editor.import_changes(self.root)
        self.assertEqual(source.read_bytes(), before)

    def test_removed_asset_and_partial_outputs_do_not_survive_a_fresh_assembly(self):
        source = self.root / "content/actors/guard/character.png"
        source.parent.mkdir(parents=True)
        Image.new("RGBA", (128, 192), (1, 2, 3, 255)).save(source)
        compiler.build(self.root)
        target = self.root / "game/Graphics/Characters/guard.png"
        self.assertTrue(target.exists())
        source.parent.rename(source.parent.with_name("keeper"))
        workspace.prepare(self.root)
        compiler.build(self.root)
        self.assertFalse(target.exists())
        self.assertTrue(target.with_name("keeper.png").exists())
        partial = self.root / "game/Data/partial.dat"
        partial.write_bytes(b"interrupted export")
        workspace.prepare(self.root)
        self.assertFalse(partial.exists())
        self.assertEqual((self.root / "game/Audio/BGM/stock.ogg").read_bytes(), b"stock")

    def test_editor_edit_to_a_removed_bundle_cannot_resurrect_it_as_an_override(self):
        source = self.root / "content/actors/guard/character.png"
        source.parent.mkdir(parents=True)
        Image.new("RGBA", (128, 192), (1, 2, 3, 255)).save(source)
        compiler.build(self.root)
        editor.remember(self.root)
        target = self.root / "game/Graphics/Characters/guard.png"
        Image.new("RGBA", (128, 192), (4, 5, 6, 255)).save(target)
        source.unlink()
        source.parent.rmdir()
        with self.assertRaisesRegex(ValueError, "generated"):
            editor.import_changes(self.root)
        self.assertFalse((self.root / "content/overrides/Graphics/Characters/guard.png").exists())

    def test_hash_failure_does_not_clear_project_and_saves_are_not_build_outputs(self):
        game = self.root / "game"
        save = game / "Game.rxdata"
        save.write_bytes(b"legacy save")
        backup = game / "Data/System.rxdata.bak"
        backup.write_bytes(b"editor backup")
        workspace.prepare(self.root)
        self.assertEqual(save.read_bytes(), b"legacy save")
        self.assertEqual(backup.read_bytes(), b"editor backup")
        (self.root / "runtime/essentials/base.zip").write_bytes(b"damaged archive")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            workspace.prepare(self.root)
        self.assertTrue((game / "Data/System.rxdata").exists())

    def test_missing_checkpoint_cannot_silently_discard_an_existing_project(self):
        editor.close(self.root)
        with self.assertRaisesRegex(ValueError, "no build checkpoint"):
            editor.require_import(self.root)
        self.assertTrue((self.root / "game/Data/System.rxdata").exists())
