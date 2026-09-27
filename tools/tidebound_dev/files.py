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
        return a.size == b.size and a.convert("RGBA").tobytes() == b.convert("RGBA").tobytes()
