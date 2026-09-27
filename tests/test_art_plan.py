"""Full artwork export preserves approved pixels and consumes editable inputs."""

from pathlib import Path
import importlib
import pkgutil
import shutil
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from tidebound_dev import art
from tidebound_dev.art import compiler

ROOT = Path(__file__).resolve().parents[1]


class ArtPlanTests(unittest.TestCase):
    def test_exporters_do_not_read_or_write_on_import(self):
        with (
            patch("PIL.Image.open", side_effect=AssertionError("read on import")),
            patch("PIL.Image.Image.save", side_effect=AssertionError("write on import")),
        ):
            for module in pkgutil.iter_modules(art.__path__, art.__name__ + "."):
                if module.name.endswith(".audio"):
                    continue  # Optional sound-production tool, not part of pixel export.
                importlib.reload(importlib.import_module(module.name))

    def test_export_preserves_pixels_and_source_edit_reaches_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "assets", root / "assets")
            for directory in ("Graphics/Pokemon", "Audio/SE/Cries"):
                shutil.copytree(ROOT / "game" / directory, root / "game" / directory)
            compiler.build(root)
            for output in (root / "game/Graphics/Pokemon").rglob("*.png"):
                original = ROOT / output.relative_to(root)
                with Image.open(original) as old, Image.open(output) as new:
                    self.assertEqual(
                        (old.size, old.convert("RGBA").tobytes()),
                        (new.size, new.convert("RGBA").tobytes()),
                        str(output.relative_to(root)),
                    )
            source = root / "assets/Moonkern/pixels.png"
            with Image.open(source) as image:
                edited = image.convert("RGBA")
            edited.putpixel((0, 0), (15, 30, 45, 255))
            edited.save(source)
            compiler.build(root)
            for folder in ("Front", "Front shiny"):
                with Image.open(root / "game/Graphics/Pokemon" / folder / "MOONKERN.png") as image:
                    self.assertEqual(image.convert("RGBA").getpixel((0, 0)), (15, 30, 45, 255))
