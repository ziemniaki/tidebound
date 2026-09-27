"""Offline map previews; decoded images and tile crops live for one generation."""

from PIL import Image
from rubymarshal.reader import loads
from .model import PATTERNS


class PreviewRenderer:
    def __init__(self, game):
        self.game = game
        self.tilesets = loads((game / "Data/Tilesets.rxdata").read_bytes())
        self.images = {}
        self.tiles = {}
        self.characters = {}

    def image(self, path):
        if path not in self.images:
            with Image.open(self.game / "Graphics" / path) as source:
                self.images[path] = source.convert("RGBA")
        return self.images[path]

    def tile(self, tileset, tile_id):
        key = tileset, tile_id
        if key in self.tiles:
            return self.tiles[key]
        ts = self.tilesets[tileset].attributes
        if tile_id >= 384:
            atlas = self.image(f"Tilesets/{ts['@tileset_name']}.png")
            x, y = (tile_id - 384) % 8 * 32, (tile_id - 384) // 8 * 32
            image = atlas.crop((x, y, x + 32, y + 32))
        else:
            name = ts["@autotile_names"][tile_id // 48 - 1]
            auto = self.image(f"Autotiles/{name}.png")
            if auto.height == 32:
                image = auto.crop((0, 0, 32, 32))
            else:
                image = Image.new("RGBA", (32, 32))
                for i, chunk in enumerate(PATTERNS[tile_id % 48]):
                    x, y = (chunk - 1) % 6 * 16, (chunk - 1) // 6 * 16
                    image.paste(auto.crop((x, y, x + 16, y + 16)), ((i % 2) * 16, (i // 2) * 16))
        self.tiles[key] = image
        return image

    def character(self, name):
        if name not in self.characters:
            sheet = self.image(f"Characters/{name}.png")
            w, h = sheet.width // 4, sheet.height // 4
            self.characters[name] = sheet.crop((w, 0, w * 2, h))
        return self.characters[name]

    def render(self, area):
        canvas = Image.new("RGBA", (area.w * 32, area.h * 32), (5, 9, 20, 255))
        for layer in area.layers:
            for y, row in enumerate(layer):
                for x, tile_id in enumerate(row):
                    if tile_id >= 48:
                        canvas.alpha_composite(self.tile(area.tileset, tile_id), (x * 32, y * 32))
        for event in area.events.values():
            p = event.attributes
            g = p["@pages"][0].attributes["@graphic"].attributes
            if g["@character_name"] and g["@opacity"]:
                image = self.character(g["@character_name"])
                canvas.alpha_composite(
                    image,
                    (p["@x"] * 32 + (32 - image.width) // 2, p["@y"] * 32 + 32 - image.height),
                )
        if area.id in (102, 103, 108, 112):
            # Approximate the runtime Tone in the offline preview, without editing assets.
            rgb = canvas.convert("RGB")
            grey = rgb.convert("L").convert("RGB")
            rgb = Image.blend(rgb, grey, 150 / 255)
            rgb = Image.merge(
                "RGB",
                [
                    band.point(lambda v, shift=shift: max(0, v + shift))
                    for band, shift in zip(rgb.split(), [-80, -74, -48])
                ],
            )
            canvas = rgb.convert("RGBA")
        elif area.id == 105:
            canvas = Image.alpha_composite(
                canvas, Image.new("RGBA", canvas.size, (10, 19, 49, 155))
            )
        return canvas.convert("RGB")
