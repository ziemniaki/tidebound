"""Atlas exports preserve frame boundaries and alpha; full pixel parity is check --all."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from tidebound_dev.art import atlas
from tidebound_dev.files import save_png


class AtlasTests(unittest.TestCase):
    def test_frames_and_shiny_copies_preserve_source_pixels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "assets/Bird"
            source.mkdir(parents=True)
            image = Image.new("RGBA", (320, 224))
            # Distinct corners catch swapped frames, off-by-one crops and alpha loss.
            for point, color in (
                ((0, 0), (1, 2, 3, 0)),
                ((159, 159), (4, 5, 6, 64)),
                ((160, 0), (7, 8, 9, 128)),
                ((319, 159), (10, 11, 12, 255)),
                ((0, 160), (13, 14, 15, 32)),
                ((127, 223), (16, 17, 18, 200)),
            ):
                image.putpixel(point, color)
            image.save(source / "pixels.png")
            outputs = root / "game/Graphics/Pokemon"
            for folder in ("Front", "Back", "Icons", "Front shiny", "Back shiny"):
                (outputs / folder).mkdir(parents=True)
            with patch.dict(atlas.ATLASES, {"Bird": "BIRD"}, clear=True):
                atlas.generate(root / "game", root / "assets")
            for folder, size, first, last in (
                ("Front", (160, 160), (1, 2, 3, 0), (4, 5, 6, 64)),
                ("Back", (160, 160), (7, 8, 9, 128), (10, 11, 12, 255)),
                ("Icons", (128, 64), (13, 14, 15, 32), (16, 17, 18, 200)),
            ):
                with (
                    self.subTest(folder=folder),
                    Image.open(outputs / folder / "BIRD.png") as frame,
                ):
                    self.assertEqual(frame.size, size)
                    self.assertEqual(frame.getpixel((0, 0)), first)
                    self.assertEqual(frame.getpixel((size[0] - 1, size[1] - 1)), last)
                    if folder != "Icons":
                        with Image.open(outputs / (folder + " shiny") / "BIRD.png") as shiny:
                            self.assertEqual(frame.tobytes(), shiny.tobytes())

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
