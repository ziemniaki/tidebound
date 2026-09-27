"""Asset exports preserve approved pixels and reject unusable engine layouts."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from tidebound_dev.art import pokemon
from tidebound_dev.art.export import validate_audio
from tidebound_dev.art.pokemon import PokemonArt
from tidebound_dev.files import save_png


class AssetTests(unittest.TestCase):
    def test_preview_selector_matches_engine_paths_on_windows(self):
        from pathlib import PureWindowsPath

        from tidebound_dev.art import preview

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "assets/characters/ACTOR.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (128, 192), (1, 2, 3, 255)).save(source)
            with patch.object(preview, "Path", PureWindowsPath):
                self.assertEqual(
                    preview.select(root, "characters/ACTOR")["path"],
                    "Graphics/Characters/ACTOR.png",
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
            source = root / "assets/pokemon/BIRD"
            source.mkdir(parents=True)
            for name, size in (("front", (160, 160)), ("back", (160, 160)), ("icon", (128, 64))):
                image = Image.new("RGBA", size, (1, 2, 3, 0))
                image.putpixel((0, 0), (40, 50, 60, 128))
                image.save(source / f"{name}.png")

            def export_images(art):
                with patch.dict(pokemon.POKEMON, {"BIRD": art}, clear=True):
                    for export in pokemon.exports(root):
                        if export.source.suffix == ".png":
                            export.write(root)

            export_images(PokemonArt("BIRD"))
            outputs = root / "game/Graphics/Pokemon"
            self.assertEqual(len(list(outputs.rglob("*.png"))), 5)
            with Image.open(outputs / "Front/BIRD.png") as image:
                self.assertEqual(image.getpixel((1, 1)), (1, 2, 3, 0))
            with Image.open(outputs / "Front shiny/BIRD.png") as image:
                self.assertEqual(image.getpixel((0, 0)), (40, 50, 60, 128))
            with self.assertRaises(FileNotFoundError):
                export_images(PokemonArt("BIRD", shiny=True))
            Image.new("RGBA", (160, 160)).save(source / "front_shiny.png")
            with self.assertRaisesRegex(ValueError, "empty artwork"):
                export_images(PokemonArt("BIRD", shiny=True))
            Image.new("RGBA", (80, 80), (1, 2, 3, 255)).save(source / "front_shiny.png")
            with self.assertRaisesRegex(ValueError, "shiny canvas"):
                export_images(PokemonArt("BIRD", shiny=True))
            Image.new("RGBA", (64, 128), (1, 2, 3, 255)).save(source / "icon.png")
            with self.assertRaisesRegex(ValueError, "horizontal strip"):
                export_images(PokemonArt("BIRD"))

    def test_missing_bundle_source_is_rejected_before_any_export(self):
        from tidebound_dev.art import compiler, files

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "game/Graphics/Items/KEY.png"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"previous export")
            source = root / "assets/items/KEY.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (48, 48), (1, 2, 3, 255)).save(source)
            with (
                patch.dict(pokemon.POKEMON, {"BIRD": PokemonArt("BIRD")}, clear=True),
                patch.dict(files.ALIASES, {}, clear=True),
                self.assertRaisesRegex(ValueError, "Missing asset source"),
            ):
                compiler.build(root)
            self.assertEqual(target.read_bytes(), b"previous export")

    def test_prop_preview_rejects_bad_metadata_at_the_source(self):
        from tidebound_dev.art import preview

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            picture = root / "assets/pictures/lamp.png"
            picture.parent.mkdir(parents=True)
            Image.new("RGBA", (16, 16), (1, 2, 3, 255)).save(picture)
            catalog = root / "assets/props.json"
            catalog.write_text(json.dumps({"lamp": {"file": "lamp", "anchor": [8, 20]}}))
            self.assertEqual(preview.select(root, "props/lamp")["anchor"], [8, 20])
            for metadata, message in (
                ({"file": "lamp", "anchor": None}, "anchor"),
                ({"file": "lamp", "anchor": [8, 20], "layer": 5}, "optional z"),
                ({"file": "../lamp", "anchor": [8, 20]}, "under assets/pictures"),
            ):
                with self.subTest(metadata=metadata):
                    catalog.write_text(json.dumps({"lamp": metadata}))
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
    def test_default_rebuild_refreshes_art_and_retires_only_owned_outputs(self):
        from contextlib import ExitStack

        from tidebound_dev import pipeline
        from tidebound_dev.art import files, ownership, pokemon

        with tempfile.TemporaryDirectory() as temp, ExitStack() as patches:
            root = Path(temp)
            (root / "assets/items").mkdir(parents=True)
            (root / "assets/props.json").write_text("{}")
            (root / "src/generated").mkdir(parents=True)
            stock = root / "game/Graphics/Items/STOCK.png"
            stock.parent.mkdir(parents=True)
            stock.write_bytes(b"irreplaceable stock input")
            source = root / "assets/items/KEY.png"
            target = root / "game/Graphics/Items/KEY.png"
            for obj, name, value in (
                (pokemon, "POKEMON", {}),
                (files, "ALIASES", {}),
                (ownership, "MAP_OUTPUTS", ()),
            ):
                patches.enter_context(patch.object(obj, name, value))
            patches.enter_context(patch.object(pipeline, "scripts"))
            patches.enter_context(
                patch.object(
                    pipeline,
                    "maps",
                    side_effect=AssertionError("ordinary rebuild must preserve editor maps"),
                )
            )
            for color in ((1, 2, 3, 128), (4, 5, 6, 200)):
                Image.new("RGBA", (48, 48), color).save(source)
                pipeline.rebuild(root)
                with Image.open(target) as image:
                    self.assertEqual(image.getpixel((0, 0)), color)
            source.unlink()
            with (
                patch.dict(files.ALIASES, {"Graphics/Items/OTHER.png": "Graphics/Items/KEY.png"}),
                self.assertRaisesRegex(ValueError, "generated output"),
            ):
                pipeline.rebuild(root)
            pipeline.rebuild(root)
            self.assertFalse(target.exists())
            self.assertEqual(stock.read_bytes(), b"irreplaceable stock input")
