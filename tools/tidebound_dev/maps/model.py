"""Native RPG Maker records for map serialization."""

import struct
from rubymarshal.classes import RubyObject, UserDef


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
