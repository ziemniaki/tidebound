from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tidebound_dev.art.audio import encode_loop


class AudioPublicationTests(unittest.TestCase):
    def test_encoder_failure_preserves_existing_audio_and_removes_temporary_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "loop.ogg"
            output.write_bytes(b"original playable loop")

            def fail(command, **kwargs):
                Path(command[-1]).write_bytes(b"partial encoder output")
                raise subprocess.CalledProcessError(1, command)

            with (
                patch("tidebound_dev.art.audio.subprocess.run", side_effect=fail),
                self.assertRaises(subprocess.CalledProcessError),
            ):
                encode_loop(b"\0" * 16, output, 22050)
            self.assertEqual(output.read_bytes(), b"original playable loop")
            self.assertEqual(list(Path(tmp).iterdir()), [output])

    def test_success_publishes_the_finished_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "loop.ogg"
            output.write_bytes(b"old loop")

            def encode(command, **kwargs):
                self.assertEqual(output.read_bytes(), b"old loop")
                Path(command[-1]).write_bytes(b"complete encoded loop")

            with patch("tidebound_dev.art.audio.subprocess.run", side_effect=encode):
                encode_loop(b"\0" * 16, output, 22050)
            self.assertEqual(output.read_bytes(), b"complete encoded loop")
            self.assertEqual(list(Path(tmp).iterdir()), [output])
