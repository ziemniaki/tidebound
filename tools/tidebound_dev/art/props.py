"""Prop bundles own approved images and event anchors."""

import math

from ..catalog import bundles
from ..files import ruby


def load(root):
    declarations = bundles(root, "props", "prop.json")
    records = {}
    for name, record in declarations.items():
        if not {"anchor"} <= record.keys() <= {"anchor", "z", "image", "scale"}:
            raise ValueError(f"Prop {name}: expected anchor and optional z/image/scale")
        image = record.get("image", name)
        if image not in declarations or "image" in declarations[image]:
            raise ValueError(f"Prop {name}: image must name a prop with its own image.png")
        path = root / "content/props" / image / "image.png"
        if not path.is_file():
            raise ValueError(f"Prop {name}: missing approved picture {path}")
        if image != name and (path.parent.parent / name / "image.png").exists():
            raise ValueError(f"Prop {name}: choose image reuse or a local image.png")
        anchor = record["anchor"]
        if (
            not isinstance(anchor, list)
            or len(anchor) != 2
            or any(type(n) is not int for n in anchor)
        ):
            raise ValueError(f"Prop {name}: anchor must be [x, y] in pixels")
        if "z" in record and type(record["z"]) is not int:
            raise ValueError(f"Prop {name}: z must be an integer")
        if "scale" in record and (
            type(record["scale"]) not in (int, float)
            or not math.isfinite(record["scale"])
            or record["scale"] <= 0
        ):
            raise ValueError(f"Prop {name}: scale must be a finite positive number")
        records[name] = {"file": f"props/{image}", "anchor": anchor}
        if "z" in record:
            records[name]["z"] = record["z"]
        if "scale" in record:
            records[name]["scale"] = record["scale"]
    return records


def write(root, records):
    (root / "src/generated/prop_assets.rb").write_text(
        "# Generated from content/props/.\nmodule Tidebound::Presentation\n"
        + "  PROP_ASSETS = "
        + ruby(records)
        + ".freeze\nend\n"
    )
