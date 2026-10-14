"""Validate authored illumination independently of walking collision."""

import math


def number(value, low, high, label):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be between {low} and {high}")


def vector(value, size, low, high, label):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{label} needs {size} numbers")
    for item in value:
        number(item, low, high, label)


def rectangle(value, label):
    vector(value, 4, 0, 10000, label)
    if value[2] <= 0 or value[3] <= 0:
        raise ValueError(f"{label} needs positive width and height")


def light(record, placed=False):
    allowed = {"radius", "strength", "color", "softness", "stretch", "flicker", "bounds"}
    if placed:
        allowed |= {"position", "event", "offset", "flag"}
    if not isinstance(record, dict) or record.keys() - allowed:
        raise ValueError("Unknown light property")
    number(record.get("radius", 3), 0.25, 20, "Light radius")
    number(record.get("strength", 0.7), 0, 1, "Light strength")
    number(record.get("softness", 0.8), 0.1, 1, "Light softness")
    number(record.get("flicker", 0), 0, 0.1, "Light flicker")
    vector(record.get("color", [255, 255, 255]), 3, 0, 255, "Light color")
    vector(record.get("stretch", [1, 1]), 2, 0.1, 4, "Light stretch")
    if "bounds" in record:
        rectangle(record["bounds"], "Light bounds")
    if placed:
        if ("position" in record) == ("event" in record):
            raise ValueError("Light needs exactly one position or event")
        if "position" in record:
            vector(record["position"], 2, 0, 10000, "Light position")
        if "event" in record and (type(record["event"]) is not int or record["event"] < 1):
            raise ValueError("Light event must be a positive ID")
        vector(record.get("offset", [0, 0]), 2, -1000, 1000, "Light offset")
        if "flag" in record and not isinstance(record["flag"], str):
            raise ValueError("Light flag must be a story key")


def validate(config):
    if not isinstance(config, dict) or config.keys() - {
        "ambient",
        "tone",
        "player",
        "sources",
        "blockers",
        "bounds",
        "north_fade",
    }:
        raise ValueError("Unknown lighting property")
    if not config:
        return
    number(config.get("ambient", 60), 0, 100, "Ambient brightness")
    vector(config.get("tone", [0, 0, 0, 60]), 4, -255, 255, "Lighting tone")
    if config.get("tone", [0, 0, 0, 60])[3] < 0:
        raise ValueError("Tone grey amount cannot be negative")
    light(config.get("player", {}))
    for source in config.get("sources", []):
        light(source, placed=True)
    for blocker in config.get("blockers", []):
        rectangle(blocker, "Light blocker")
    if "bounds" in config:
        rectangle(config["bounds"], "Room bounds")
    if "north_fade" in config:
        fade = config["north_fade"]
        if set(fade) != {"from_y", "to_y", "ambient"}:
            raise ValueError("North fade requires from_y, to_y and ambient")
        number(fade["ambient"], 0, 100, "North ambient")
        number(fade["to_y"], 0, 10000, "North fade end")
        number(fade["from_y"], 0, 10000, "North fade start")
        if fade["from_y"] <= fade["to_y"]:
            raise ValueError("North fade must end north of its start")


def validate_map(config, width, height, events):
    validate(config)
    for source in config.get("sources", []):
        if "event" in source and source["event"] not in events:
            raise ValueError(f"Light refers to missing event {source['event']}")
        if "position" in source:
            x, y = source["position"]
            if x >= width or y >= height:
                raise ValueError("Light position is outside its map")
    rectangles = list(config.get("blockers", []))
    if "bounds" in config:
        rectangles.append(config["bounds"])
    rectangles += [s["bounds"] for s in config.get("sources", []) if "bounds" in s]
    for x, y, w, h in rectangles:
        if x + w > width or y + h > height:
            raise ValueError("Light bounds/blocker exceeds the map")
