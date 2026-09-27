from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tidebound_dev.release.metadata as release_tools


class RuntimeConfigTests(unittest.TestCase):
    def check_config(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "game").mkdir()
            (root / "game/mkxp.json").write_text(text)
            scripts = {
                "Tidebound/domain/state": 'VERSION = "0.8.6"',
                "Settings": 'GAME_VERSION = "0.8.6"',
            }
            config = dict(
                version="0.8.6",
                runtime_archive="runtime",
                runtime_source="source",
                runtime_patch="patch",
                runtime_sha256="hash",
                runtime_source_sha256="hash",
                runtime_patch_sha256="hash",
            )
            with (
                patch.object(release_tools, "load_release", return_value=config),
                patch.object(release_tools, "validate_archive", return_value=scripts),
                patch.object(release_tools, "sha256", return_value="hash"),
            ):
                release_tools.check_sources(root)

    def test_duplicate_save_or_font_keys_are_rejected(self):
        for extra in ('"dataPathApp":"OtherSaves"', '"fontHeightReporting":0'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.check_config(
                    '{"dataPathApp":"Tidebound_Opening_0_2","fontHeightReporting":1,' + extra + "}"
                )

    def test_commented_settings_do_not_satisfy_release_requirements(self):
        with self.assertRaises(ValueError):
            self.check_config(
                '// "dataPathApp":"Tidebound_Opening_0_2"\n// "fontHeightReporting":1\n{}'
            )

    def test_comments_and_comment_markers_in_strings_remain_valid(self):
        self.check_config(
            '// launch settings\n{"dataPathApp":"Tidebound_Opening_0_2",/* font fix */"fontHeightReporting":1,"example":"https://host/path/*file*/"}'
        )

    def test_runtime_trailing_commas_preserve_strings_and_nested_values(self):
        self.check_config(
            '{"dataPathApp":"Tidebound_Opening_0_2","fontHeightReporting":1,"bindings":{"c":"Use",},"values":[1,2,],"title":"literal ,} ,]",}'
        )
        path = Path(__file__).resolve().parents[2] / "game/mkxp.json"
        self.check_config(path.read_text())
