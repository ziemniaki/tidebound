"""Moving a window tile moves its light without changing the approved mask."""

from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from PIL import Image
from tidebound_dev.maps.scenery import window_lights


class LightMaskTests(unittest.TestCase):
    def test_moved_tile_updates_light_position_without_changing_mask(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in (
                "content/tilesets/outside",
                "game/Graphics/Pictures/Tidebound",
                "src/generated",
            ):
                (root / directory).mkdir(parents=True)
            mask = Image.new("RGBA", (256, 64))
            mask.putpixel((65, 34), (230, 180, 120, 75))
            mask.save(root / "content/tilesets/outside/windows.png")
            area = SimpleNamespace(id=1, light_mask="outside/windows.png", layers=[[], [[0, 394]]])
            window_lights(root, [area])
            image = root / "game/Graphics/Pictures/Tidebound/window_panes.png"
            ruby = root / "src/generated/window_lights.rb"
            original = (image.read_bytes(), ruby.read_bytes())
            area.layers[1][0] = [394, 0]
            window_lights(root, [area])
            self.assertEqual(image.read_bytes(), original[0])
            self.assertNotEqual(ruby.read_bytes(), original[1])
            self.assertIn("[[0, 0, 0]]", ruby.read_text())
            with Image.open(image) as actual:
                self.assertEqual(actual.getpixel((1, 2)), (230, 180, 120, 75))
