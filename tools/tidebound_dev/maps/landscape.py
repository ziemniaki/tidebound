from ..files import save_png
from PIL import Image
from rubymarshal.reader import loads
from rubymarshal.writer import writes
import struct

from .model import tile, table
import math
from collections import deque


def save_atlas(paths, palette, maps, group):
    # Water depth is legible without compromising the animated native sea or vast horizon.
    # Only the story outdoor maps receive this cloned tileset; demo/astral remain untouched.
    tilesets = loads((paths.game / "Data/Tilesets.rxdata").read_bytes())
    landscape_id = next(
        (i for i, t in enumerate(tilesets) if t and t.attributes.get("@name") == group.name),
        len(tilesets),
    )
    ts = loads(writes(tilesets[1]))
    ts.attributes["@id"] = landscape_id
    ts.attributes["@name"] = group.name
    ts.attributes["@tileset_name"] = group.texture
    for m in maps:
        m.tileset = landscape_id
        m.light_mask = "Outside/windows.png"
    # Keep the native wave animations, tint only blue water pixels (not shore rock).
    for name, source, factors in [
        ("Tidebound Shallows", "Sea", (0.98, 1.13, 1.03)),
        ("Tidebound Open Sea", "Sea without shore", (0.87, 0.98, 1.0)),
        ("Tidebound Deep Sea", "Sea without shore", (0.76, 0.87, 0.94)),
    ]:
        im = Image.open(paths.game / "Graphics/Autotiles" / f"{source}.png").convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                red, green, blue, a = px[x, y]
                if blue > red and blue > green:
                    px[x, y] = (
                        int(red * factors[0]),
                        min(255, int(green * factors[1])),
                        min(255, int(blue * factors[2])),
                        a,
                    )
        save_png(im, paths.game / "Graphics/Autotiles" / f"{name}.png")
    ts.attributes["@autotile_names"][:3] = [
        "Tidebound Shallows",
        "Tidebound Open Sea",
        "Tidebound Deep Sea",
    ]
    # Extend native tables and atlas deterministically. Base tile IDs and window pixels stay exact.
    height = (palette._native.height // 32 + math.ceil(len(palette._tile_images) / 8)) * 32
    atlas = Image.new("RGBA", (256, height))
    atlas.alpha_composite(palette._native)
    for i, (im, tag) in enumerate(palette._tile_images):
        atlas.alpha_composite(im, ((i % 8) * 32, palette._native.height + (i // 8) * 32))
    if height > 16384:
        raise ValueError(
            f"Atlas {group.name} is {height}px high; split its maps into smaller groups (limit 16384)"
        )
    save_png(atlas, paths.game / f"Graphics/Tilesets/{group.texture}.png")
    for key in ["@passages", "@priorities", "@terrain_tags"]:
        data = ts.attributes[key]._dump()
        header = struct.unpack("<5i", data[:20])
        values = list(struct.unpack("<" + "h" * header[4], data[20:]))
        values = values[: palette._base_count] + [0] * max(0, palette._base_count - len(values))
        values += [tag if key == "@terrain_tags" else 0 for im, tag in palette._tile_images]
        ts.attributes[key] = table(values, len(values))
    if landscape_id == len(tilesets):
        tilesets.append(ts)
    else:
        tilesets[landscape_id] = ts
    (paths.game / "Data/Tilesets.rxdata").write_bytes(writes(tilesets))


def shade_water(m):
    dist = [[999] * m.w for _ in range(m.h)]
    q = deque()
    for y in range(m.h):
        for x in range(m.w):
            v = m.layers[0][y][x]
            if v >= 192 and v not in (tile(6, 150), tile(6, 151)):
                dist[y][x] = 0
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for xx, yy in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if 0 <= xx < m.w and 0 <= yy < m.h and dist[yy][xx] > dist[y][x] + 1:
                dist[yy][xx] = dist[y][x] + 1
                q.append((xx, yy))
    for y in range(m.h):
        for x in range(m.w):
            v = m.layers[0][y][x]
            if 48 <= v < 192:
                distance = dist[y][x]
                if distance <= 2:
                    m.layers[0][y][x] = 48 + (v % 48 if v < 96 else 0)
                elif distance <= 7:
                    m.layers[0][y][x] = 96
                else:
                    m.layers[0][y][x] = 144
