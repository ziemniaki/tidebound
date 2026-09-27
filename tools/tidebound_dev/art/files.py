"""Derive native asset paths from authored content ownership."""

from ..catalog import AUDIO, bundles
from .export import Export
from . import props


def exports(root):
    content = root / "content"
    for source in sorted((content / "actors").glob("*/character.png")):
        yield Export(source, f"game/Graphics/Characters/{source.parent.name}.png")
    for identifier, record in bundles(root, "items", "item.json").items():
        source = content / "items" / identifier / "icon.png"
        if "stock_icon" in record:
            if source.exists():
                raise ValueError(f"Item {identifier}: choose stock_icon or a local icon.png")
            source = root / f"game/Graphics/Items/{record['stock_icon']}.png"
        yield Export(source, f"game/Graphics/Items/{identifier}.png")
    for identifier, record in bundles(root, "trainers", "trainer.json").items():
        for name, folder, prefix in (
            ("portrait", "Trainers", ""),
            ("character", "Characters", "trainer_"),
        ):
            source = content / "trainers" / identifier / f"{name}.png"
            if "stock" in record:
                if source.exists():
                    raise ValueError(f"Trainer {identifier}: choose stock or local artwork")
                source = root / f"game/Graphics/{folder}/{prefix}{record['stock']}.png"
            yield Export(source, f"game/Graphics/{folder}/{prefix}{identifier}.png")
    for name in sorted(
        {record["file"].removeprefix("props/") for record in props.load(root).values()}
    ):
        yield Export(
            content / "props" / name / "image.png", f"game/Graphics/Pictures/props/{name}.png"
        )
    for category in ("ui", "effects"):
        for source in sorted((content / category).glob("*.png")):
            yield Export(source, f"game/Graphics/Pictures/{category}/{source.name}")
    for category, destination in AUDIO.items():
        for source in sorted((content / "audio" / category).glob("*.ogg")):
            yield Export(source, f"game/Audio/{destination}/{source.name}")
