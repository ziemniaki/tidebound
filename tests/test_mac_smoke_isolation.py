"""A malformed save setting must fail before a native fixture can launch."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mac_runtime_smoke as smoke


class SmokeIsolationTests(unittest.TestCase):
    def test_missing_or_duplicate_namespace_fails_before_launch(self):
        for text in ('{}', '{"dataPathApp":"player","dataPathApp":"other"}'):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                def extract(archive, destination):
                    game = destination / 'fixture/Tidebound.app/Contents/Game'
                    game.mkdir(parents=True)
                    (game / 'mkxp.json').write_text(text)
                with patch.object(smoke.sys, 'platform', 'darwin'), patch.object(smoke.platform, 'machine', return_value='arm64'), patch.object(smoke, 'extract_bundle', side_effect=extract), patch.object(smoke, 'run'), patch.object(smoke.subprocess, 'run') as launch:
                    with self.assertRaisesRegex(ValueError, 'one save namespace'):
                        smoke.smoke(root / 'fixture.zip', root / 'evidence', 'arm64', 'ordinary')
                    launch.assert_not_called()
