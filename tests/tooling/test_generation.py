"""A failed generator or publication must not leave a partially updated game."""

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev import pipeline
from tidebound_dev.generation import staged_outputs


class GenerationTests(unittest.TestCase):
    def test_late_art_failure_leaves_all_live_outputs_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "game/Data").mkdir(parents=True)
            (root / "game/PBS").mkdir()
            (root / "game/Data/species.dat").write_bytes(b"original")

            def data(stage):
                (stage / "game/Data/species.dat").write_bytes(b"changed")
                (stage / "game/PBS/new.txt").write_text("new")

            with (
                patch.object(pipeline, "maps"),
                patch.object(pipeline.story, "build"),
                patch.object(pipeline.species_compiler, "build", side_effect=data),
                patch.object(pipeline.encounters, "build"),
                patch.object(pipeline.art, "build", side_effect=FileNotFoundError("missing PNG")),
            ):
                with self.assertRaisesRegex(FileNotFoundError, "missing PNG"):
                    pipeline.rebuild(root, full=True)
            self.assertEqual((root / "game/Data/species.dat").read_bytes(), b"original")
            self.assertFalse((root / "game/PBS/new.txt").exists())

    def test_publication_error_restores_replaced_files_and_removes_new_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "game").mkdir()
            (root / "game/a.txt").write_text("original a")
            (root / "game/c.txt").write_text("original c")
            replace = os.replace

            def fail_third(source, target):
                if Path(source).parts[-3:] == ("new", "game", "c.txt"):
                    raise OSError("publication failed")
                replace(source, target)

            with patch("tidebound_dev.generation.os.replace", side_effect=fail_third):
                with self.assertRaisesRegex(OSError, "publication failed"):
                    with staged_outputs(root, inputs=("game",), outputs=("game",)) as stage:
                        for name in ("a", "b", "c"):
                            (stage / f"game/{name}.txt").write_text("changed")
            self.assertEqual((root / "game/a.txt").read_text(), "original a")
            self.assertEqual((root / "game/c.txt").read_text(), "original c")
            self.assertFalse((root / "game/b.txt").exists())
            # A successful retry needs no cleanup and publishes the complete result.
            with staged_outputs(root, inputs=("game",), outputs=("game",)) as stage:
                for name in ("a", "b", "c"):
                    (stage / f"game/{name}.txt").write_text("complete")
            self.assertEqual(
                [p.read_text() for p in sorted((root / "game").iterdir())], ["complete"] * 3
            )

    def test_rollback_failure_retains_originals_and_reports_recovery_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            (root / "game").mkdir(parents=True)
            (root / "game/a.txt").write_text("original")
            replace = os.replace

            def fail_publish_and_restore(source, target):
                if "old" in Path(source).parts or Path(target).name == "b.txt":
                    raise OSError("storage unavailable")
                replace(source, target)

            with patch("tidebound_dev.generation.os.replace", side_effect=fail_publish_and_restore):
                with self.assertRaisesRegex(RuntimeError, "recovery files remain") as error:
                    with staged_outputs(root, inputs=("game",), outputs=("game",)) as stage:
                        (stage / "game/a.txt").write_text("changed")
                        (stage / "game/b.txt").write_text("new")
            (recovery,) = Path(temp).glob(".tidebound-publish-*")
            self.assertIn(str(recovery), str(error.exception))
            self.assertEqual((recovery / "old/game/a.txt").read_text(), "original")
