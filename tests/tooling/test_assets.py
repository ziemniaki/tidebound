"""Asset exports preserve approved pixels and reject unusable engine layouts."""

from pathlib import Path
import tempfile
import unittest
from PIL import Image
from tidebound_dev.art.pokemon import PokemonArt, frames
from tidebound_dev.files import save_png
from tidebound_dev.art.files import validate_audio


class AssetTests(unittest.TestCase):
    def test_renaming_an_image_to_ogg_does_not_make_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sound.ogg"
            Image.new("RGBA", (8, 8)).save(path, format="PNG")
            with self.assertRaisesRegex(ValueError, "Ogg Vorbis"):
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
            outputs = dict(frames(root, "BIRD", PokemonArt("BIRD")))
            self.assertEqual(len(outputs), 5)
            self.assertEqual(
                outputs["Graphics/Pokemon/Front/BIRD.png"].getpixel((1, 1)), (1, 2, 3, 0)
            )
            self.assertEqual(
                outputs["Graphics/Pokemon/Front shiny/BIRD.png"].getpixel((0, 0)), (40, 50, 60, 128)
            )
            with self.assertRaises(FileNotFoundError):
                list(frames(root, "BIRD", PokemonArt("BIRD", shiny=True)))
            Image.new("RGBA", (64, 128), (1, 2, 3, 255)).save(source / "icon.png")
            with self.assertRaisesRegex(ValueError, "horizontal strip"):
                list(frames(root, "BIRD", PokemonArt("BIRD")))

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
        from unittest.mock import patch
        from contextlib import ExitStack
        from tidebound_dev import pipeline
        from tidebound_dev.art import pokemon, files, ownership

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
            pipeline.rebuild(root)
            self.assertFalse(target.exists())
            self.assertEqual(stock.read_bytes(), b"irreplaceable stock input")
