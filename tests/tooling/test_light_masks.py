"""Tileset compaction must preserve light placement and approved mask pixels."""

from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from PIL import Image
from tidebound_dev.maps.scenery import window_lights


class LightMaskTests(unittest.TestCase):
    def test_repacked_tile_uses_source_mask_at_the_same_map_position(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in (
                "assets/tilesets/Outside",
                "game/Graphics/Pictures/Tidebound",
                "src/generated",
            ):
                (root / directory).mkdir(parents=True)
            mask = Image.new("RGBA", (256, 64))
            mask.putpixel((65, 34), (230, 180, 120, 75))
            mask.save(root / "assets/tilesets/Outside/windows.png")
            area = SimpleNamespace(
                id=1, light_mask="Outside/windows.png", source_tiles={}, layers=[[], [[0, 394]]]
            )
            paths = SimpleNamespace(root=root, game=root / "game")
            window_lights(paths, [area])
            image = root / "game/Graphics/Pictures/Tidebound/window_panes.png"
            ruby = root / "src/generated/window_lights.rb"
            original = (image.read_bytes(), ruby.read_bytes())
            area.layers[1][0][1] = 450
            area.source_tiles = {450: 394}
            window_lights(paths, [area])
            self.assertEqual((image.read_bytes(), ruby.read_bytes()), original)
            with Image.open(image) as actual:
                self.assertEqual(actual.getpixel((1, 2)), (230, 180, 120, 75))
