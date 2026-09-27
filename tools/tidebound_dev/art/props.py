"""Export prop anchors alongside images; maps select assets, not filename rules."""

import json
from pathlib import PurePosixPath

from ..files import ruby


def load(root):
    records = json.loads((root / "assets/props.json").read_text())
    for name, record in records.items():
        if not isinstance(record, dict) or not {"file", "anchor"} <= record.keys() <= {
            "file",
            "anchor",
            "z",
        }:
            raise ValueError(f"Prop {name}: expected file, anchor and optional z")
        filename = record["file"]
        if (
            not isinstance(filename, str)
            or not filename
            or "\\" in filename
            or PurePosixPath(filename).is_absolute()
            or ".." in PurePosixPath(filename).parts
        ):
            raise ValueError(
                f"Prop {name}: file must be a path under assets/pictures without extension"
            )
        path = root / "assets/pictures" / (filename + ".png")
        if not path.is_file():
            raise ValueError(f"Prop {name}: missing approved picture {path}")
        anchor = record["anchor"]
        if (
            not isinstance(anchor, list)
            or len(anchor) != 2
            or any(type(n) is not int for n in anchor)
        ):
            raise ValueError(f"Prop {name}: anchor must be [x, y] in pixels")
        if "z" in record and type(record["z"]) is not int:
            raise ValueError(f"Prop {name}: z must be an integer")
    return records


def write(root, records):
    (root / "src/generated/prop_assets.rb").write_text(
        "# Generated from assets/props.json.\nmodule Tidebound::Presentation\n"
        + "  PROP_ASSETS = "
        + ruby(records)
        + ".freeze\nend\n"
    )
