"""The installed operation package must be safe to import and share one plan."""

import importlib
from pathlib import Path
import unittest
from unittest.mock import patch

from tidebound_dev import pipeline


class PythonPackageTests(unittest.TestCase):
    def test_core_operations_import_without_game_io(self):
        with (
            patch.object(Path, "read_bytes", side_effect=AssertionError("import read")),
            patch.object(Path, "write_bytes", side_effect=AssertionError("import write")),
            patch.object(Path, "read_text", side_effect=AssertionError("import read")),
            patch.object(Path, "write_text", side_effect=AssertionError("import write")),
        ):
            for module in (
                "pipeline",
                "content.opening_items",
                "content.quest_data",
                "content.configure",
                "content.encounters",
                "checks.rebuild",
                "release.candidates",
                "packaging.pipeline",
            ):
                importlib.reload(importlib.import_module("tidebound_dev." + module))

    def test_script_only_rebuild_does_not_load_or_regenerate_maps(self):
        root = Path("/disposable/source")
        with (
            patch.object(pipeline, "maps", side_effect=AssertionError("map regeneration")),
            patch.object(pipeline, "scripts") as embed,
        ):
            pipeline.rebuild(root)
        embed.assert_called_once_with(root)
