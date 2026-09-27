"""One file export, used by both the writer and the ownership inventory."""

import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from ..files import save_png
from .recolors import recolor


@dataclass(frozen=True)
class Export:
    source: Path
    destination: str  # Repository-relative, with forward slashes on every platform.
    palette: dict | None = None
    matching_canvas: Path | None = None

    def write(self, root):
        target = root / self.destination
        target.parent.mkdir(parents=True, exist_ok=True)
        if self.source.suffix != ".png":
            validate_audio(self.source)
            shutil.copy2(self.source, target)
            return
        if self.palette is not None:
            image = recolor(self.source, self.palette)
        else:
            with Image.open(self.source) as source:
                image = source.convert("RGBA")
        try:
            width, height = image.size
            if "/Characters/" in self.destination and (width % 4 or height % 4):
                raise ValueError(
                    f"{self.source}: XP characters require a four-column, four-row sheet"
                )
            if "/Pokemon/Icons/" in self.destination and (width < height or width % height):
                raise ValueError(f"{self.source}: icon must be a horizontal strip of square frames")
            if not image.getchannel("A").getbbox():
                raise ValueError(f"{self.source}: empty artwork")
            if self.matching_canvas:
                with Image.open(self.matching_canvas) as normal:
                    if image.size != normal.size:
                        raise ValueError(
                            f"{self.source}: shiny canvas must match normal canvas {normal.size}"
                        )
            save_png(image, target)
        finally:
            image.close()


def validate_audio(path):
    """Check container/codec headers, not musical quality or native decoding."""
    if path.suffix == ".wav":
        import wave

        try:
            with wave.open(str(path), "rb") as audio:
                if audio.getnchannels() not in (1, 2) or not audio.getnframes():
                    raise ValueError(f"{path}: expected nonempty mono/stereo PCM WAV")
        except (wave.Error, EOFError) as error:
            raise ValueError(f"{path}: expected nonempty mono/stereo PCM WAV") from error
        return
    with path.open("rb") as audio:
        header = audio.read(27)
        if len(header) != 27 or header[:5] != b"OggS\x00":
            raise ValueError(f"{path}: expected Ogg Vorbis, not a renamed file")
        audio.read(header[26])  # First page's lacing table.
        identification = audio.read(30)
        if (
            len(identification) != 30
            or identification[:7] != b"\x01vorbis"
            or identification[11] not in (1, 2)
        ):
            raise ValueError(f"{path}: expected mono/stereo Ogg Vorbis")
