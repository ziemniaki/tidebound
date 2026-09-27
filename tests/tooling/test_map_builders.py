"""Map edits preserve interaction positions and publish only validated outputs."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev.maps import compiler


class MapBuilderTests(unittest.TestCase):
    def test_landscape_protects_relocated_events_without_a_shadow_position_list(self):
        from tidebound_dev.maps.model import Map
        from tidebound_dev.maps.landscape_painter import Landscape

        area = Map(101, "Room", 10, 10, 1)
        event_id = area.event("Object", 2, 2, "", blocks=True)
        area.events[event_id].attributes["@x"] = 6
        landscape = Landscape(area, None)
        self.assertIn((6, 2), landscape.protected)
        self.assertNotIn((2, 2), landscape.protected)
        self.assertTrue(area.targets[0][-1])  # Relocation preserves authored collision intent.

    def test_validation_failure_does_not_publish_any_generated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "game/Data").mkdir(parents=True)
            original = root / "game/Data/Map101.rxdata"
            original.write_bytes(b"original")

            def failed_output(paths, _maps):
                (paths.game / "Data/Map101.rxdata").write_bytes(b"changed")
                (paths.root / "src/generated/map_passages.rb").write_text("changed")

            with (
                patch.object(compiler, "construct", return_value=[]),
                patch.object(compiler, "serialize", side_effect=failed_output),
                patch(
                    "tidebound_dev.maps.validate.validate",
                    side_effect=ValueError("blocked transfer"),
                ),
            ):
                with self.assertRaisesRegex(ValueError, "blocked transfer"):
                    compiler.build(root)
            self.assertEqual(original.read_bytes(), b"original")
            self.assertFalse((root / "src").exists())
            self.assertFalse((root / "tools").exists())


if __name__ == "__main__":
    unittest.main()
