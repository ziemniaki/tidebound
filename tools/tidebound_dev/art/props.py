"""Export prop anchors alongside images; maps select assets, not filename rules."""

import json
from ..files import ruby


def build(root):
    records = json.loads((root / "assets/props.json").read_text())
    for name, record in records.items():
        path = root / "assets/pictures" / (record["file"] + ".png")
        if not path.is_file():
            raise ValueError(f"Prop {name}: missing approved picture {path}")
        if len(record["anchor"]) != 2 or any(type(n) is not int for n in record["anchor"]):
            raise ValueError(f"Prop {name}: anchor must be [x, y] in pixels")
        if "z" in record and type(record["z"]) is not int:
            raise ValueError(f"Prop {name}: z must be an integer")
    (root / "src/generated/prop_assets.rb").write_text(
        "# Generated from assets/props.json.\nmodule Tidebound::Presentation\n"
        + "  PROP_ASSETS = "
        + ruby(records)
        + ".freeze\nend\n"
    )
