"""Later pages and invalid destinations must not escape static validation."""

from pathlib import Path
import shutil
import tempfile
import unittest
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from tidebound_dev.maps import model
from tidebound_dev.maps.validate import validate, validate_transfer

ROOT = Path(__file__).resolve().parents[2]


class TransferTests(unittest.TestCase):
    def test_bounds_are_checked_before_mask_indexing(self):
        for x, y in ((-1, 0), (0, -1), (2, 0), (0, 2)):
            with self.subTest(x=x, y=y), self.assertRaisesRegex(ValueError, "outside map"):
                validate_transfer({"101": ["11", "11"]}, 101, x, y)
        with self.assertRaisesRegex(ValueError, "Blocked"):
            validate_transfer({"101": ["0"]}, 101, 0, 0)

    def test_every_page_and_native_transfer_destination_is_validated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "game/.generated", root / "game/.generated")
            shutil.copytree(ROOT / "game/Data", root / "game/Data")
            for name in ("Graphics", "Audio"):
                (root / "game" / name).symlink_to(ROOT / "game" / name, target_is_directory=True)
            path = root / "game/Data/Map101.rxdata"
            original = path.read_bytes()
            for kind, expected in (
                ("charset", "page2 missing charset nonexistent"),
                ("computed", "page2: undeclared transfer"),
                ("native", "page2: Transfer outside map"),
            ):
                with self.subTest(kind=kind):
                    area = loads(original)
                    event = next(iter(area.attributes["@events"].values())).attributes
                    page = loads(writes(event["@pages"][0]))
                    event["@pages"].append(page)
                    if kind == "charset":
                        page.attributes["@graphic"].attributes["@character_name"] = "nonexistent"
                    elif kind == "computed":
                        page.attributes["@list"] = model.script(
                            "Tidebound::World . travel(:home, *arrival)"
                        )
                    else:
                        page.attributes["@list"] = [model.command(201, 0, 101, -1, 0, 2, 0)]
                    path.write_bytes(writes(area))
                    with self.assertRaisesRegex(RuntimeError, expected):
                        validate(root, check_scripts=False)
