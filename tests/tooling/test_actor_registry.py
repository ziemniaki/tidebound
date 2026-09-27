"""Actor labels are presentation; map ownership and identity are contracts."""

from dataclasses import replace
import unittest
from unittest.mock import patch
from tidebound_dev.maps import registry, model, areas


class ActorRegistryTests(unittest.TestCase):
    def test_duplicate_and_misplaced_actors_fail_generation(self):
        mother = registry.ACTORS["mother"]
        home = model.Map(101, "Home", 3, 3, 1)
        home.event(mother, 1, 1, "")
        home.event(mother, 2, 1, "")
        with patch.dict(registry.ACTORS, {"mother": mother}, clear=True):
            with self.assertRaisesRegex(ValueError, "Duplicate actor identity: mother"):
                registry.collect_actors([home])
        with self.assertRaisesRegex(ValueError, "belongs to home"):
            model.Map(102, "Coast", 3, 3, 1).event(mother, 1, 1, "")

    def test_label_changes_preserve_identity_role_and_placement(self):
        original = areas.build_home()
        with patch.dict(
            registry.ACTORS,
            {key: replace(value, label="Label " + key) for key, value in registry.ACTORS.items()},
        ):
            renamed = areas.build_home()
        self.assertEqual(original.actor_settings, renamed.actor_settings)
        for event_id in original.events:
            old = original.events[event_id].attributes
            new = renamed.events[event_id].attributes
            self.assertEqual((old["@x"], old["@y"]), (new["@x"], new["@y"]))
            self.assertEqual(
                old["@pages"][0].attributes["@through"], new["@pages"][0].attributes["@through"]
            )
        self.assertNotEqual(original.serialize(), renamed.serialize())

    def test_role_typos_and_incomplete_roles_are_rejected(self):
        area = model.Map(101, "Home", 3, 3, 1)
        for options in (
            {"role": "hose"},
            {"role": "room"},
            {"role": "spirit"},
            {"role": "neighbor_wild", "species": "NATU"},
            {"role": "demo_prop"},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                area.event("Any readable label", 1, 1, "", **options)

    def test_landscape_protects_relocated_events_without_a_shadow_position_list(self):
        from tidebound_dev.maps.landscape_painter import Landscape

        area = model.Map(101, "Room", 10, 10, 1)
        event_id = area.event("Object", 2, 2, "", blocks=True)
        area.events[event_id].attributes["@x"] = 6
        landscape = Landscape(area, None)
        self.assertIn((6, 2), landscape.protected)
        self.assertNotIn((2, 2), landscape.protected)
        self.assertTrue(area.targets[0][-1])  # Relocation preserves authored collision intent.
