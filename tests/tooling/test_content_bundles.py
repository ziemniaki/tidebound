"""Authored bundles must not disappear silently from a build or lose data on parsing."""

import json
from pathlib import Path
import tempfile
import unittest

from tidebound_dev.catalog import bundles, validate_names
from tidebound_dev.art.ownership import inventory


class ContentBundleTests(unittest.TestCase):
    def test_missing_declaration_and_duplicate_keys_fail_at_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "content/pokemon/BIRD"
            directory.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "missing species.json"):
                bundles(root, "pokemon", "species.json")
            (directory / "species.json").write_text('{"art": {"cry": "BIRD", "cry": "OTHER"}}')
            with self.assertRaisesRegex(ValueError, "Duplicate declaration key: cry"):
                bundles(root, "pokemon", "species.json")

    def test_unexportable_names_and_audio_formats_fail_before_generation(self):
        for name in (
            "audio/music/theme.mid",
            "audio/BGM/theme.ogg",
            "audio/muisc/theme.ogg",
            "actors/ivo/walk.png",
            "pokemon/BIRD/frnot.png",
            "items/bird/item.json",
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path = root / "content" / name
                path.parent.mkdir(parents=True)
                path.touch()
                with self.assertRaises(ValueError):
                    validate_names(root)

    def test_stock_reuse_cannot_claim_a_generated_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = root / "content/items/OTHER/item.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"stock_icon": "KEY"}))
            target = root / "game/Graphics/Items/KEY.png"
            target.parent.mkdir(parents=True)
            target.touch()
            manifest = root / "game/.generated/assets.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"game/Graphics/Items/KEY.png": "files"}))
            with self.assertRaisesRegex(ValueError, "generated output"):
                inventory(root)

    def test_new_actor_cannot_overwrite_stock_art(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "content/actors/guard/character.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (128, 192), (1, 2, 3, 255)).save(source)
            target = root / "game/Graphics/Characters/guard.png"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"stock art")
            with self.assertRaisesRegex(ValueError, "overwrite an unowned file"):
                inventory(root)
            self.assertEqual(target.read_bytes(), b"stock art")
