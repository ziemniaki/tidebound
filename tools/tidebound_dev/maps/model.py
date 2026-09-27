from .registry import MAP_NAMES, MAPS
from .transfers import Transfer
from dataclasses import asdict
from . import definitions

"""In-memory RPG Maker map, event and tile primitives. Importing writes nothing."""
import struct
from rubymarshal.classes import RubyObject, UserDef
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from PIL import Image, ImageDraw

PATTERNS = [
    [27, 28, 33, 34],
    [5, 28, 33, 34],
    [27, 6, 33, 34],
    [5, 6, 33, 34],
    [27, 28, 33, 12],
    [5, 28, 33, 12],
    [27, 6, 33, 12],
    [5, 6, 33, 12],
    [27, 28, 11, 34],
    [5, 28, 11, 34],
    [27, 6, 11, 34],
    [5, 6, 11, 34],
    [27, 28, 11, 12],
    [5, 28, 11, 12],
    [27, 6, 11, 12],
    [5, 6, 11, 12],
    [25, 26, 31, 32],
    [25, 6, 31, 32],
    [25, 26, 31, 12],
    [25, 6, 31, 12],
    [15, 16, 21, 22],
    [15, 16, 21, 12],
    [15, 16, 11, 22],
    [15, 16, 11, 12],
    [29, 30, 35, 36],
    [29, 30, 11, 36],
    [5, 30, 35, 36],
    [5, 30, 11, 36],
    [39, 40, 45, 46],
    [5, 40, 45, 46],
    [39, 6, 45, 46],
    [5, 6, 45, 46],
    [25, 30, 31, 36],
    [15, 16, 45, 46],
    [13, 14, 19, 20],
    [13, 14, 19, 12],
    [17, 18, 23, 24],
    [17, 18, 11, 24],
    [41, 42, 47, 48],
    [5, 42, 47, 48],
    [37, 38, 43, 44],
    [37, 6, 43, 44],
    [13, 18, 19, 24],
    [13, 14, 43, 44],
    [37, 42, 43, 48],
    [17, 18, 47, 48],
    [13, 18, 43, 48],
    [1, 2, 7, 8],
]
NEIGHBORS = [
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    42,
    32,
    42,
    32,
    35,
    19,
    35,
    18,
    42,
    32,
    42,
    32,
    34,
    17,
    34,
    16,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    42,
    32,
    42,
    32,
    35,
    19,
    35,
    18,
    42,
    32,
    42,
    32,
    34,
    17,
    34,
    16,
    45,
    39,
    45,
    39,
    33,
    31,
    33,
    29,
    45,
    39,
    45,
    39,
    33,
    31,
    33,
    29,
    37,
    27,
    37,
    27,
    23,
    15,
    23,
    13,
    37,
    27,
    37,
    27,
    22,
    11,
    22,
    9,
    45,
    39,
    45,
    39,
    33,
    31,
    33,
    29,
    45,
    39,
    45,
    39,
    33,
    31,
    33,
    29,
    36,
    26,
    36,
    26,
    21,
    7,
    21,
    5,
    36,
    26,
    36,
    26,
    20,
    3,
    20,
    1,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    42,
    32,
    42,
    32,
    35,
    19,
    35,
    18,
    42,
    32,
    42,
    32,
    34,
    17,
    34,
    16,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    46,
    44,
    46,
    44,
    43,
    41,
    43,
    40,
    42,
    32,
    42,
    32,
    35,
    19,
    35,
    18,
    42,
    32,
    42,
    32,
    34,
    17,
    34,
    16,
    45,
    38,
    45,
    38,
    33,
    30,
    33,
    28,
    45,
    38,
    45,
    38,
    33,
    30,
    33,
    28,
    37,
    25,
    37,
    25,
    23,
    14,
    23,
    12,
    37,
    25,
    37,
    25,
    22,
    10,
    22,
    8,
    45,
    38,
    45,
    38,
    33,
    30,
    33,
    28,
    45,
    38,
    45,
    38,
    33,
    30,
    33,
    28,
    36,
    24,
    36,
    24,
    21,
    6,
    21,
    4,
    36,
    24,
    36,
    24,
    20,
    2,
    20,
    0,
]


def obj(class_name, **values):
    return RubyObject(class_name, {"@" + k: v for k, v in values.items()})


def table(values, x, y=1, z=1):
    t = UserDef("Table")
    t._load(
        struct.pack("<5i", 3 if z > 1 else 2 if y > 1 else 1, x, y, z, len(values))
        + struct.pack("<" + "h" * len(values), *values)
    )
    return t


def command(code, *parameters, indent=0):
    return obj("RPG::EventCommand", code=code, indent=indent, parameters=list(parameters))


def script(code):
    lines = code.splitlines()
    return [command(355 if i == 0 else 655, line) for i, line in enumerate(lines)]


def page(code, charset="", trigger=0, opacity=255, move=0):
    condition = obj(
        "RPG::Event::Page::Condition",
        switch1_valid=False,
        switch2_valid=False,
        variable_valid=False,
        self_switch_valid=False,
        switch1_id=1,
        switch2_id=1,
        variable_id=1,
        variable_value=0,
        self_switch_ch="A",
    )
    graphic = obj(
        "RPG::Event::Page::Graphic",
        tile_id=0,
        character_name=charset,
        character_hue=0,
        direction=2,
        pattern=0,
        opacity=opacity,
        blend_type=0,
    )
    route = obj(
        "RPG::MoveRoute",
        repeat=True,
        skippable=True,
        list=[obj("RPG::MoveCommand", code=0, parameters=[])],
    )
    return obj(
        "RPG::Event::Page",
        condition=condition,
        graphic=graphic,
        move_type=move,
        move_speed=2,
        move_frequency=2,
        move_route=route,
        walk_anime=True,
        step_anime=False,
        direction_fix=False,
        through=(charset == ""),
        always_on_top=False,
        trigger=trigger,
        list=script(code) + [command(0)],
    )


def tile(x, y):
    return 384 + x + y * 8


class Map:
    def __init__(self, id, name, w, h, tileset, floor=0):
        self.id, self.name, self.w, self.h, self.tileset = id, name, w, h, tileset
        self.layers = [[[0] * w for _ in range(h)] for _ in range(3)]
        self.layers[0] = [[floor] * w for _ in range(h)]
        self.walk = [[False] * w for _ in range(h)]
        self.events = {}
        self.targets = []
        self.transfers = []

    def rect(self, x, y, w, h, t, z=0, walk=None):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.layers[z][yy][xx] = t
                if walk is not None:
                    self.walk[yy][xx] = walk

    def stamp(self, sx, sy, w, h, x, y, walk=False, z=1):
        for yy in range(h):
            for xx in range(w):
                self.layers[z][y + yy][x + xx] = tile(sx + xx, sy + yy)
                if walk is not None:
                    self.walk[y + yy][x + xx] = walk

    def event(self, name, x, y, code, charset="", trigger=0, opacity=255, move=0, blocks=False):
        eid = len(self.events) + 1
        self.events[eid] = obj(
            "RPG::Event",
            id=eid,
            name=name,
            x=x,
            y=y,
            pages=[page(code, charset, trigger, opacity, move)],
        )
        if blocks:
            self.walk[y][x] = False
        self.targets.append((name, x, y, trigger, blocks))
        return eid

    def door(self, x, y, destination, dx, dy, d=2, name="Door"):
        """Source uses this area's coordinates; destinations are always absolute."""
        destination = MAPS[destination] if isinstance(destination, str) else destination
        transfer = Transfer(destination, dx, dy, d)
        eid = self.event(name, x, y, transfer.script(), trigger=1)
        event = self.events[eid].attributes
        self.walk[event["@y"]][event["@x"]] = True
        self.transfers.append({"event": eid, "page": 0, **asdict(transfer)})
        return eid

    def serialize(self):
        flat = [v for layer in self.layers for row in layer for v in row]
        m = obj(
            "RPG::Map",
            tileset_id=self.tileset,
            width=self.w,
            height=self.h,
            autoplay_bgm=True,
            bgm=obj(
                "RPG::AudioFile",
                name=definitions.BY_ID[self.id].music,
                volume=80,
                pitch=100,
            ),
            autoplay_bgs=False,
            bgs=obj("RPG::AudioFile", name="", volume=100, pitch=100),
            encounter_list=[],
            encounter_step=30,
            data=table(flat, self.w, self.h, 3),
            events=self.events,
        )
        return writes(m)

    def render(self, game):
        ts = loads((game / "Data/Tilesets.rxdata").read_bytes())[self.tileset].attributes
        atlas = Image.open(game / "Graphics/Tilesets" / f"{ts['@tileset_name']}.png").convert(
            "RGBA"
        )
        canvas = Image.new("RGBA", (self.w * 32, self.h * 32), (5, 9, 20, 255))
        autos = {}
        for layer in self.layers:
            for y, row in enumerate(layer):
                for x, t in enumerate(row):
                    if t >= 384:
                        c = (t - 384) % 8
                        r = (t - 384) // 8
                        image = atlas.crop((c * 32, r * 32, c * 32 + 32, r * 32 + 32))
                    elif t >= 48:
                        key = t // 48 - 1
                        if key not in autos:
                            autos[key] = Image.open(
                                game / "Graphics/Autotiles" / f"{ts['@autotile_names'][key]}.png"
                            ).convert("RGBA")
                        auto = autos[key]
                        # Variant zero is the seamless centre, four 16px chunks.
                        image = Image.new("RGBA", (32, 32))
                        for i, chunk in enumerate(PATTERNS[t % 48]):
                            cx = ((chunk - 1) % 6) * 16
                            cy = ((chunk - 1) // 6) * 16
                            image.paste(
                                auto.crop((cx, cy, cx + 16, cy + 16)), ((i % 2) * 16, (i // 2) * 16)
                            )
                    else:
                        continue
                    if 48 <= t < 384 and auto.height == 32:
                        image = auto.crop((0, 0, 32, 32))
                    canvas.alpha_composite(image, (x * 32, y * 32))
        for e in self.events.values():
            p = e.attributes
            g = p["@pages"][0].attributes["@graphic"].attributes
            if g["@character_name"] and g["@opacity"]:
                im = Image.open(
                    game / "Graphics/Characters" / f"{g['@character_name']}.png"
                ).convert("RGBA")
                w, h = im.width // 4, im.height // 4
                im = im.crop((w, 0, w * 2, h))
                canvas.alpha_composite(im, (p["@x"] * 32 + (32 - w) // 2, p["@y"] * 32 + 32 - h))
        if self.id in (102, 103, 108, 112):
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
        elif self.id == 105:
            canvas = Image.alpha_composite(
                canvas, Image.new("RGBA", canvas.size, (10, 19, 49, 155))
            )
        return canvas.convert("RGB")


class CoastMap(Map):
    OX, OY = 24, 20

    def rect(self, x, y, *args, **kw):
        super().rect(x + self.OX, y + self.OY, *args, **kw)

    def stamp(self, sx, sy, w, h, x, y, **kw):
        super().stamp(sx, sy, w, h, x + self.OX, y + self.OY, **kw)

    def event(self, name, x, y, *args, **kw):
        return super().event(name, x + self.OX, y + self.OY, *args, **kw)

    def polygon(self, points, t, walk=True):
        im = Image.new("1", (self.w, self.h))
        ImageDraw.Draw(im).polygon([(x + self.OX, y + self.OY) for x, y in points], fill=1)
        for yy in range(self.h):
            for xx in range(self.w):
                if im.getpixel((xx, yy)):
                    self.layers[0][yy][xx] = t
                    self.walk[yy][xx] = walk

    def path(self, x, y, w, h, stone=False):
        base = 26 if stone else 12
        for yy in range(h):
            for xx in range(w):
                self.rect(
                    x + xx,
                    y + yy,
                    1,
                    1,
                    tile(
                        1 if xx == 0 else 3 if xx == w - 1 else 2,
                        base + (0 if yy == 0 else 2 if yy == h - 1 else 1),
                    ),
                    walk=True,
                )


class RoadMap(CoastMap):
    OX, OY = 0, 0
