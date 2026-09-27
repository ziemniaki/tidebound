"""Map/event identities and actor contracts survive native display-name changes."""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from tidebound_dev.maps import registry, definitions
from tidebound_dev.maps.data import native_map
from tidebound_dev.paths import ROOT


class ActorRegistryTests(unittest.TestCase):
    def home(self):
        native = native_map(json.loads((ROOT / "content/maps/home/layout.json").read_text()))
        return SimpleNamespace(
            id=101,
            events=native.attributes["@events"],
            actor_settings={int(k): v for k, v in definitions.BY_ID[101].actor_settings.items()},
        )

    def test_named_actor_lookup_survives_rename_but_rejects_duplicate_and_wrong_map(self):
        area = self.home()
        area.events[1].attributes["@name"] = "A different display label"
        with patch.dict(
            registry.ACTORS,
            {k: v for k, v in registry.ACTORS.items() if v.map == "home"},
            clear=True,
        ):
            actors, _ = registry.collect_actors([area])
            self.assertEqual(actors["mother"], {"map": 101, "event": 1})
            with self.assertRaisesRegex(ValueError, "Duplicate actor"):
                registry.collect_actors([area, area])
            area.id = 102
            with self.assertRaisesRegex(ValueError, "belongs to home"):
                registry.collect_actors([area])

    def test_role_typos_and_incomplete_roles_fail_at_the_compiler_boundary(self):
        area = self.home()
        for info in (
            {"role": "hose"},
            {"role": "room"},
            {"role": "spirit"},
            {"role": "neighbor_wild", "species": "NATU"},
            {"role": "prop"},
        ):
            area.actor_settings = {1: info}
            with self.subTest(info=info), self.assertRaises(ValueError):
                registry.collect_actors([area])
