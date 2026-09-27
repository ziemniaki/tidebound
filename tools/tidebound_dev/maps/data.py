"""Lossless, readable RPG Maker records. JSON is authoritative; Marshal is an export."""

import base64
import json
import struct
from rubymarshal.classes import RubyObject, RubyString, Symbol, UserDef
from .model import obj, table
from ..catalog import unique_keys


def read(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def encode(value):
    if isinstance(value, UserDef):
        raw = value._dump()
        if value.ruby_class_name == "Table":
            _, x, y, z, size = struct.unpack("<5i", raw[:20])
            values = list(struct.unpack(f"<{size}h", raw[20:]))
            return {
                "$type": "Table",
                "shape": [x, y, z],
                "rows": [values[i : i + x] for i in range(0, size, x)],
            }
        return {"$type": value.ruby_class_name, "$bytes": base64.b64encode(raw).decode()}
    if isinstance(value, Symbol):
        return {"$symbol": str(value)}
    if isinstance(value, (str, RubyString)):
        return str(value)
    if isinstance(value, RubyObject):
        return {
            "$type": value.ruby_class_name,
            **{key.removeprefix("@"): encode(v) for key, v in value.attributes.items()},
        }
    if isinstance(value, dict):
        return {"$pairs": [[encode(k), encode(v)] for k, v in value.items()]}
    if isinstance(value, list):
        return [encode(v) for v in value]
    if value is None or type(value) in (int, float, bool):
        return value
    raise ValueError(f"Unsupported RPG Maker value: {type(value).__name__}")


def decode(value):
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    if "$symbol" in value:
        return Symbol(value["$symbol"])
    if "$pairs" in value:
        return {decode(k): decode(v) for k, v in value["$pairs"]}
    kind = value["$type"]
    if kind == "Table":
        x, y, z = value["shape"]
        rows = value["rows"]
        if len(rows) != y * z or any(len(row) != x for row in rows):
            raise ValueError("Tile table shape and rows disagree")
        return table([v for row in rows for v in row], x, y, z)
    if "$bytes" in value:
        result = UserDef(kind)
        result._load(base64.b64decode(value["$bytes"], validate=True))
        return result
    return obj(kind, **{k: decode(v) for k, v in value.items() if k != "$type"})


def map_record(native):
    record = encode(native)
    # Event IDs are the native hash keys, not list positions. Keep edits local in Git.
    record["events"] = {str(k): v for k, v in record["events"]["$pairs"]}
    return record


def native_map(record):
    if any(str(int(key)) != key or int(key) < 1 for key in record["events"]):
        raise ValueError("Event IDs must be positive decimal keys without leading zeroes")
    record = {**record, "events": {"$pairs": [[int(k), v] for k, v in record["events"].items()]}}
    return decode(record)


def dump(value):
    """One row/coordinate/command parameter list per line, without enormous pretty arrays."""

    def format_value(value, depth=0):
        pad = "  " * depth
        if isinstance(value, dict):
            return (
                "{\n"
                + ",\n".join(
                    pad + "  " + json.dumps(k) + ": " + format_value(v, depth + 1)
                    for k, v in value.items()
                )
                + "\n"
                + pad
                + "}"
                if value
                else "{}"
            )
        if isinstance(value, list) and any(isinstance(v, (list, dict)) for v in value):
            return (
                "[\n"
                + ",\n".join(pad + "  " + format_value(v, depth + 1) for v in value)
                + "\n"
                + pad
                + "]"
            )
        return json.dumps(value, ensure_ascii=False)

    return format_value(value) + "\n"
