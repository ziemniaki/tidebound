"""Split approved pixel atlases without resampling, quantization or alpha blending.

Layout: 160x160 front and back side by side; 128x64 icon below the front.
The unused bottom-right area is not exported. High-resolution concept art is
reference material, not an alternative build input.
"""

from PIL import Image

ATLASES = {
    "Sunkern": "SUNKERN_1",
    "Moonkern": "MOONKERN",
    "Moonflora": "MOONFLORA",
    "Glaciverm": "GLACIVERM",
}


def generate(game, assets):
    for directory, species in ATLASES.items():
        path = assets / directory / "pixels.png"
        with Image.open(path) as source:
            if source.size != (320, 224):
                raise ValueError(f"{path}: expected a 320x224 pixel atlas, got {source.size}")
            source = source.convert("RGBA")
        for folder, bounds in (
            ("Front", (0, 0, 160, 160)),
            ("Back", (160, 0, 320, 160)),
            ("Icons", (0, 160, 128, 224)),
        ):
            frame = source.crop(bounds)
            frame.save(game / "Graphics/Pokemon" / folder / f"{species}.png")
            if folder != "Icons":
                frame.save(game / "Graphics/Pokemon" / f"{folder} shiny" / f"{species}.png")
