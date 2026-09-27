"""Native RPG Maker records and the XP autotile rendering pattern table."""

import struct
from rubymarshal.classes import RubyObject, UserDef

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
