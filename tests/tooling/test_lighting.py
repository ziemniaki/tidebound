"""Reject broken authored lights before they reach the native renderer."""

import unittest
from tidebound_dev.maps.definitions import MapDefinition
from tidebound_dev.maps.lighting import light, validate_map
from tidebound_dev.files import ruby


class LightingTests(unittest.TestCase):
    def test_map_source_identity_and_bounds(self):
        valid = {"ambient": 40, "sources": [{"event": 3, "radius": 4}], "bounds": [1, 1, 8, 8]}
        validate_map(valid, 10, 10, {3: object()})
        for config in (
            {"sources": [{"event": 4}]},
            {"sources": [{"position": [10, 2]}]},
            {"sources": [{"position": [2, 2], "event": 3}]},
            {"blockers": [[9, 1, 2, 3]]},
            {"north_fade": {"from_y": 2, "to_y": 8, "ambient": 10}},
            {"ambient": -1},
            {"player": {"strength": float("nan")}},
        ):
            with self.subTest(config=config), self.assertRaises(ValueError):
                validate_map(config, 10, 10, {3: object()})

    def test_item_and_map_share_light_units(self):
        source = {"radius": 4.5, "strength": 0.8, "color": [255, 180, 95]}
        light(source)
        settings = MapDefinition(
            id=1, lighting={"sources": [dict(source, event=2)]}
        ).runtime_settings()
        self.assertEqual(settings["lighting"]["sources"][0]["radius"], 4.5)
        self.assertIn('"sources" => [{"radius" => 4.5', ruby(settings["lighting"]))
        self.assertEqual(ruby([None, True]), "[nil, true]")
