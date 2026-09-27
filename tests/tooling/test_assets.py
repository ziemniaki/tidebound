"""Asset exports preserve approved pixels and reject unusable engine layouts."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from tidebound_dev.art import pokemon
from tidebound_dev.art.export import validate_audio
from tidebound_dev.files import save_png


class AssetTests(unittest.TestCase):
    def test_preview_selector_matches_engine_paths_on_windows(self):
        from pathlib import PureWindowsPath

        from tidebound_dev.art import preview

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "content/actors/actor/character.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (128, 192), (1, 2, 3, 255)).save(source)
            with patch.object(preview, "Path", PureWindowsPath):
                self.assertEqual(
                    preview.select(root, "actors/actor")["path"],
                    "Graphics/Characters/actor.png",
                )

    def test_renaming_an_image_does_not_make_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            for extension, codec in (("ogg", "Ogg Vorbis"), ("wav", "PCM WAV")):
                with self.subTest(extension=extension):
                    path = Path(temp) / f"sound.{extension}"
                    Image.new("RGBA", (8, 8)).save(path, format="PNG")
                    with self.assertRaisesRegex(ValueError, codec):
                        validate_audio(path)

    def test_bundle_preserves_alpha_and_requires_distinct_shiny_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "content/pokemon/BIRD"
            source.mkdir(parents=True)
            for name, size in (("front", (160, 160)), ("back", (160, 160)), ("icon", (128, 64))):
                image = Image.new("RGBA", size, (1, 2, 3, 0))
                image.putpixel((0, 0), (40, 50, 60, 128))
                image.save(source / f"{name}.png")

            def export_images(art):
                (source / "species.json").write_text(json.dumps({"art": art}))
                for export in pokemon.exports(root):
                    if export.source.suffix == ".png":
                        export.write(root)

            export_images({"cry": "BIRD"})
            outputs = root / "game/Graphics/Pokemon"
            self.assertEqual(len(list(outputs.rglob("*.png"))), 5)
            with Image.open(outputs / "Front/BIRD.png") as image:
                self.assertEqual(image.getpixel((1, 1)), (1, 2, 3, 0))
            with Image.open(outputs / "Front shiny/BIRD.png") as image:
                self.assertEqual(image.getpixel((0, 0)), (40, 50, 60, 128))
            with self.assertRaises(FileNotFoundError):
                export_images({"cry": "BIRD", "shiny": True})
            Image.new("RGBA", (160, 160)).save(source / "front_shiny.png")
            with self.assertRaisesRegex(ValueError, "empty artwork"):
                export_images({"cry": "BIRD", "shiny": True})
            Image.new("RGBA", (80, 80), (1, 2, 3, 255)).save(source / "front_shiny.png")
            with self.assertRaisesRegex(ValueError, "shiny canvas"):
                export_images({"cry": "BIRD", "shiny": True})
            Image.new("RGBA", (64, 128), (1, 2, 3, 255)).save(source / "icon.png")
            with self.assertRaisesRegex(ValueError, "horizontal strip"):
                export_images({"cry": "BIRD"})

    def test_missing_bundle_source_is_rejected_before_any_export(self):
        from tidebound_dev.art import compiler

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "game/Graphics/Items/KEY.png"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"previous export")
            source = root / "content/items/KEY/icon.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (48, 48), (1, 2, 3, 255)).save(source)
            (source.parent / "item.json").write_text("{}")
            bird = root / "content/pokemon/BIRD/species.json"
            bird.parent.mkdir(parents=True)
            bird.write_text(json.dumps({"art": {"cry": "BIRD"}}))
            with self.assertRaisesRegex(ValueError, "Missing asset source"):
                compiler.build(root)
            self.assertEqual(target.read_bytes(), b"previous export")

    def test_prop_preview_rejects_bad_metadata_at_the_source(self):
        from tidebound_dev.art import preview

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            picture = root / "content/props/lamp/image.png"
            picture.parent.mkdir(parents=True)
            Image.new("RGBA", (16, 16), (1, 2, 3, 255)).save(picture)
            catalog = root / "content/props/lamp/prop.json"
            catalog.write_text(json.dumps({"anchor": [8, 20]}))
            self.assertEqual(preview.select(root, "props/lamp")["anchor"], [8, 20])
            for metadata, message in (
                ({"anchor": None}, "anchor"),
                ({"anchor": [8, 20], "layer": 5}, "optional z"),
                ({"image": "../lamp", "anchor": [8, 20]}, "image must name"),
            ):
                with self.subTest(metadata=metadata):
                    catalog.write_text(json.dumps(metadata))
                    with self.assertRaisesRegex(ValueError, message):
                        preview.select(root, "props/lamp")

    def test_png_encoding_changes_do_not_dirty_art_but_pixel_edits_are_saved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sprite.png"
            image = Image.new("RGBA", (32, 32), (10, 20, 30, 128))
            image.save(path, compress_level=0)
            original = path.read_bytes()
            save_png(image, path)
            self.assertEqual(path.read_bytes(), original)
            image.putpixel((0, 0), (40, 50, 60, 64))
            save_png(image, path)
            with Image.open(path) as saved:
                self.assertEqual(saved.getpixel((0, 0)), (40, 50, 60, 64))


class AssetRefreshTests(unittest.TestCase):
    def test_failed_new_export_can_be_fixed_and_rebuilt(self):
        from tidebound_dev.art import compiler

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src/generated").mkdir(parents=True)
            for name, width in (("first", 128), ("second", 127)):
                source = root / f"content/actors/{name}/character.png"
                source.parent.mkdir(parents=True)
                Image.new("RGBA", (width, 128), (1, 2, 3, 255)).save(source)
            with self.assertRaisesRegex(ValueError, "four-column"):
                compiler.build(root)
            Image.new("RGBA", (128, 128), (4, 5, 6, 255)).save(source)
            compiler.build(root)
            with Image.open(root / "game/Graphics/Characters/second.png") as image:
                self.assertEqual(image.getpixel((0, 0)), (4, 5, 6, 255))
