"""Content comparison for generated output, independent of PNG encoding."""

import hashlib
from PIL import Image


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def equivalent(before, after):
    if not after.is_file():
        return False
    if before.read_bytes() == after.read_bytes():
        return True
    if before.suffix.lower() != ".png":
        return False
    # PNG compressor bytes may differ across macOS/Linux and Pillow wheels.
    with Image.open(before) as a, Image.open(after) as b:
        return _same_pixels(a, b)


def _same_pixels(a, b):
    return a.size == b.size and a.convert("RGBA").tobytes() == b.convert("RGBA").tobytes()


def save_png(image, path):
    """Avoid Git noise when only the PNG encoder changed, not the artwork."""
    if path.is_file():
        with Image.open(path) as previous:
            if _same_pixels(previous, image):
                return
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def ruby(value):
    import json

    if isinstance(value, dict):
        return "{" + ", ".join(f"{ruby(k)} => {ruby(v)}" for k, v in value.items()) + "}"
    return json.dumps(value)
