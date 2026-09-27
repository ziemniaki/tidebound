"""Asset exports preserve approved pixels and reject unusable engine layouts."""

from pathlib import Path
import tempfile
import unittest
from PIL import Image
from tidebound_dev.art.pokemon import PokemonArt, frames
from tidebound_dev.files import save_png


class AssetTests(unittest.TestCase):
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
