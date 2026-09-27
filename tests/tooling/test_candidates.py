"""A release candidate is a complete, single-commit transaction across platforms."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tidebound_dev.release import candidates
from tidebound_dev.release.artifacts import validate_candidate, write_checksums
from tidebound_dev.release.metadata import source_revision


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        (self.root / "docs/release-notes.md").write_text(
            "# Tidebound 1.2.3\n\n- A playable change.\n"
        )
        (self.root / "game.txt").write_text("committed game")
        for args in (
            ("init", "-q"),
            ("add", "."),
            (
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ),
        ):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        self.source = source_revision(self.root)
        self.output = self.root.parent / "candidate"
        self.config = {"version": "1.2.3", "mac_build": "1"}
        config = patch.object(candidates, "check_sources", return_value=self.config)
        config.start()
        self.addCleanup(config.stop)

    def package(self, platform, output, root):
        # Platform packaging has its own native/transaction checks. Supply its on-disk
        # contract here; candidate assembly, project archive and validation run for real.
        name, arch, manifest = {
            "mac": ("Mac", "universal", "BUILD.json"),
            "windows": ("Windows", "x64", "WINDOWS_BUILD.json"),
            "linux": ("Linux", "x86_64", "LINUX_BUILD.json"),
        }[platform]
        output.mkdir()
        with zipfile.ZipFile(output / f"Tidebound_{name}_1.2.3_{arch}.zip", "w") as archive:
            archive.write(root / "game.txt", "game.txt")
        (output / manifest).write_text(json.dumps({**self.config, "source": self.source}))
        write_checksums(output)

    def test_complete_candidate_matches_commit_and_project_contents(self):
        with patch.object(candidates, "build", side_effect=self.package):
            candidates.build_release(self.output, self.root)
        validate_candidate(self.output, "1.2.3", self.source["commit"], "1")
        with zipfile.ZipFile(self.output / "Tidebound_Project_1.2.3.zip") as archive:
            self.assertEqual(archive.read("Tidebound_Prototype/game.txt"), b"committed game")
        self.assertEqual(
            (self.output / "RELEASE_NOTES.md").read_text(),
            (self.root / "docs/release-notes.md").read_text(),
        )

    def test_last_platform_failure_never_publishes_a_partial_candidate(self):
        def fail(platform, output, root):
            self.package(platform, output, root)
            if platform == "linux":
                raise ValueError("corrupt Linux package")

        with patch.object(candidates, "build", side_effect=fail):
            with self.assertRaisesRegex(ValueError, "corrupt Linux"):
                candidates.build_release(self.output, self.root)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.parent.iterdir()), [self.root])

    def test_wrong_release_notes_fail_before_building_players(self):
        notes = self.root / "docs/release-notes.md"
        notes.write_text("# Tidebound 1.2.2\n\nOld notes.\n")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "stale notes",
            ],
            check=True,
        )
        with patch.object(candidates, "build", side_effect=AssertionError("unnecessary build")):
            with self.assertRaisesRegex(ValueError, "release notes must match"):
                candidates.build_release(self.output, self.root)
        self.assertFalse(self.output.exists())
