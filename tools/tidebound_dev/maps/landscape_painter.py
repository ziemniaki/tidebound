from PIL import Image, ImageDraw
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import copy
import json
import struct

from .model import Map, RoadMap, tile, table, command, script
import math
import random
from collections import deque
from .shoreline import shoreline


class LandscapePalette:
    def __init__(self, game):
        self._native = (
            Image.open(game / "Graphics/Tilesets/Outside.png")
            .convert("RGBA")
            .crop((0, 0, 256, 456 * 32))
        )
        # Story maps use native rows through 451. Leave room below the GL 16K texture limit.
        self._tile_images = []
        self._tile_cache = {}
        self._base_count = 384 + (self._native.height // 32) * 8

        self.PINE = self.art(0, 55, 3, 3)
        self.ROUND = self.art(3, 61, 3, 3)
        self.AUTUMN = self.art(3, 67, 3, 3)
        self.ROCK = self.art(0, 108, 3, 3)
        self.BUSH = self.art(3, 59)
        self.SMALLROCKS = [
            self.art(0, 140, 2, 2).crop((16, 16, 48, 48)),
            self.art(2, 140, 2, 2).crop((16, 16, 48, 48)),
        ]
        self.FLOWER = (
            Image.open(game / "Graphics/Autotiles/Flowers1.png")
            .convert("RGBA")
            .crop((0, 0, 32, 32))
        )
        self.WHITE = self.art(7, 3)

    def baked(self, im, tag=0):
        key = (im.tobytes(), tag)
        if key not in self._tile_cache:
            self._tile_cache[key] = self._base_count + len(self._tile_images)
            self._tile_images.append((im.copy(), tag))
        return self._tile_cache[key]

    def art(self, x, y, w=1, h=1):
        return self._native.crop((x * 32, y * 32, (x + w) * 32, (y + h) * 32))

    def clear_nature(self, m, all_forest=False):
        for y in range(m.h):
            for x in range(m.w):
                v = m.layers[1][y][x]
                row = (v - 384) // 8 if v >= 384 else -1
                nature = (
                    52 <= row <= 75
                    or 108 <= row <= 110
                    or (139 <= row <= 143 and (v - 384) % 8 < 4)
                    or v in [240, tile(6, 0), tile(7, 3), tile(7, 0)]
                )
                if nature:
                    m.layers[1][y][x] = 0
                    # Restore old nature footprints only on real land, not water or borders.
                    if m.layers[0][y][x] >= 384 and (m.id != 103 or 3 <= x <= 32 and 3 <= y <= 26):
                        m.walk[y][x] = True
        for _, x, y, _, blocks in m.targets:
            if blocks:
                m.walk[y][x] = False

    def grass_patch(self, p, cx, cy, rx, ry):
        m = p.m
        for y in range(max(0, cy - ry - 1), min(m.h, cy + ry + 2)):
            for x in range(max(0, cx - rx - 1), min(m.w, cx + rx + 2)):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if (
                    d < 1.0 + p.rng.uniform(-0.13, 0.13)
                    and m.walk[y][x]
                    and (x, y) not in p.protected
                    and m.layers[1][y][x] == 0
                ):
                    m.layers[1][y][x] = tile(7, 0)

    def groves(self, p, centres, attempts):
        # Filled canopy blocks, with overlapping crowns as in early-generation maps.
        # Clearings and corridors are carved OUT of the forest, not dotted with trees.
        m = p.m

        def allowed(x, y, size):
            cells = [(xx, yy) for yy in range(y, y + size) for xx in range(x, x + size)]
            return all(
                0 <= xx < m.w
                and 0 <= yy < m.h
                and (xx, yy) not in p.protected
                and (xx, yy) not in p.clearings
                and m.layers[1][yy][xx] == 0
                and m.layers[0][yy][xx] == tile(1, 0)
                for xx, yy in cells
            )

        def in_grove(x, y):
            return (
                min(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 for cx, cy, rx, ry in centres) < 3.6
            )

        for y in range(0, m.h - 2, 2):
            for x in range((y // 2) % 2, m.w - 2, 2):
                if allowed(x, y, 3) and in_grove(x + 1, y + 1):
                    im = self.ROUND if (x // 7 + y // 6) % 3 else self.PINE
                    p.plant(im, x, y, 3, 3, check=False)
        # Younger trees thicken edges, while low shrubs soften the last single tiles.
        for size in [2, 1]:
            for y in range(m.h - size):
                for x in range(m.w - size):
                    if not allowed(x, y, size) or not in_grove(x, y):
                        continue
                    cells = {(xx, yy) for yy in range(y, y + size) for xx in range(x, x + size)}
                    if cells & p.occupied:
                        continue
                    nearby = sum(
                        (x + dx, y + dy) in p.occupied
                        for dx, dy in [(-1, 0), (size, 0), (0, -1), (0, size)]
                    )
                    if nearby and (size == 2 or (x + y) % 3 == 0):
                        p.plant(
                            self.PINE if size == 2 else self.BUSH, x, y, size, size, check=False
                        )
        for x, y in sorted(p.occupied):
            p.ground(x, y, 0.16)

    def clearing(self, p, x, y, w, h):
        p.clearings.update((xx, yy) for yy in range(y, y + h) for xx in range(x, x + w))

    def scree(self, p, regions):
        # Overlapping whole boulders follow the rocky land boundary, with smaller feet.
        m = p.m
        for x0, y0, x1, y1 in regions:
            for y in range(y0, y1, 2):
                for x in range(x0 + (y % 4) // 2, x1, 2):
                    size = 2 if (x + y) % 4 else 3
                    cells = [(xx, yy) for yy in range(y, y + size) for xx in range(x, x + size)]
                    if any(
                        not (0 <= xx < m.w and 0 <= yy < m.h)
                        or (xx, yy) in p.protected
                        or m.layers[1][yy][xx]
                        for xx, yy in cells
                    ):
                        continue
                    # Don't fill open ocean: these are contiguous land-edge formations.
                    if not any(m.layers[0][yy][xx] >= 192 for xx, yy in cells):
                        continue
                    p.plant(self.ROCK, x, y, size, size, check=False)
                    for xx, yy in cells:
                        p.ground(xx, yy)

    def rock_group(self, p, x, y, scale=3, coastal=False):
        m = p.m
        if coastal:
            cells = [(xx, yy) for yy in range(y, y + scale) for xx in range(x, x + scale)]
            if any(
                not (0 <= xx < m.w and 0 <= yy < m.h)
                or (xx, yy) in p.protected
                or (xx, yy) in p.occupied
                or m.layers[1][yy][xx]
                for xx, yy in cells
            ):
                return
            p.plant(self.ROCK, x, y, scale, scale, check=False)
        elif not p.plant(self.ROCK, x, y, scale, scale):
            return
        for dx, dy in [(-1, 1), (scale, scale - 1), (scale - 1, scale), (0, scale), (-1, scale)]:
            xx, yy = x + dx, y + dy
            if (
                not (0 <= xx < m.w and 0 <= yy < m.h)
                or (xx, yy) in p.protected
                or (xx, yy) in p.occupied
            ):
                continue
            if m.layers[1][yy][xx] or m.layers[0][yy][xx] < 192:
                continue
            p.plant(p.rng.choice(self.SMALLROCKS), xx, yy, 1, 1, check=False)
            if m.layers[0][yy][xx] == tile(1, 0):
                p.ground(xx, yy, 0.3)

    def painter(self, area):
        return Landscape(area, self)


class Landscape:
    def __init__(self, m, palette):
        self.palette = palette
        self.m = m
        self.rng = random.Random(1400 + m.id)
        self.overlay = Image.new("RGBA", (m.w * 32, m.h * 32))
        self.sprites = []
        self.occupied = set()
        self.protected = set()
        self.ground_cells = set()
        self.clearings = set()
        self.native_layer = copy.deepcopy(m.layers[1])
        # Event centres and their interaction spaces remain open. Autoruns excluded.
        for name, x, y, trigger, blocks in m.targets:
            if trigger == 3:
                continue
            for yy in range(y - 1, y + 2):
                for xx in range(x - 1, x + 2):
                    self.protected.add((xx, yy))
        # Every existing road/path/plank remains available to scripted movement.
        for y in range(m.h):
            for x in range(m.w):
                v = m.layers[0][y][x]
                if (
                    m.walk[y][x]
                    and v >= 384
                    and v != tile(1, 0)
                    and not (m.id == 102 and v == tile(2, 27))
                ):
                    self.protected.add((x, y))

    def reserve(self, x, y, w, h):
        self.protected.update((xx, yy) for yy in range(y, y + h) for xx in range(x, x + w))

    def valid(self, x, y, w, h, protected=True):
        m = self.m
        if x < 0 or y < 0 or x + w > m.w or y + h > m.h:
            return False
        return all(
            (xx, yy) not in self.occupied
            and (not protected or (xx, yy) not in self.protected)
            and m.layers[1][yy][xx] == 0
            and m.layers[0][yy][xx] == tile(1, 0)
            for yy in range(y, y + h)
            for xx in range(x, x + w)
        )

    def plant(self, img, x, y, w=3, h=3, check=True, solid=True):
        if check and not self.valid(x, y, w, h):
            return False
        m = self.m
        if x < 0 or y < 0 or x + w > m.w or y + h > m.h:
            return False
        img = img.resize((w * 32, h * 32), Image.Resampling.NEAREST)
        self.sprites.append((y + h, img, x * 32, y * 32))
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.occupied.add((xx, yy))
                if solid:
                    m.walk[yy][xx] = False
        return True

    def decal(self, img, x, y):
        if 0 <= x < self.m.w and 0 <= y < self.m.h and self.m.layers[1][y][x] == 0:
            self.overlay.alpha_composite(img, (x * 32, y * 32))

    def ground(self, x, y, amount=0.16):
        if self.m.layers[0][y][x] == tile(1, 0):
            self.ground_cells.add((x, y))

    def finish(self):
        # Feather connected humus beds into grass. No square patchwork under trees.
        for x, y in sorted(self.ground_cells):
            im = self.palette.art(1, 0)
            px = im.load()
            for yy in range(32):
                for xx in range(32):
                    edge = 1.0
                    for dx, dy, dist in [
                        (-1, 0, xx),
                        (1, 0, 31 - xx),
                        (0, -1, yy),
                        (0, 1, 31 - yy),
                    ]:
                        if (x + dx, y + dy) not in self.ground_cells:
                            edge = min(edge, min(1, dist / 12))
                    factor = 0.16 * edge
                    r, g, b, a = px[xx, yy]
                    px[xx, yy] = (
                        round(r * (1 - factor) + 75 * factor),
                        round(g * (1 - factor) + 86 * factor),
                        round(b * (1 - factor) + 66 * factor),
                        a,
                    )
            self.m.layers[0][y][x] = self.palette.baked(im)
        for _, im, x, y in sorted(self.sprites, key=lambda v: v[0]):
            self.overlay.alpha_composite(im, (x, y))
        for y in range(self.m.h):
            for x in range(self.m.w):
                im = self.overlay.crop((x * 32, y * 32, x * 32 + 32, y * 32 + 32))
                if im.getbbox():
                    self.m.layers[2][y][x] = self.palette.baked(im)


# Native tree sprites use these exact complete rectangles (no editor placeholders).
# The isolated round tree occupies columns 3..5, rows 63..65.
