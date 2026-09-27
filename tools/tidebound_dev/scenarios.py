"""Resolve feature-owned playtest states before staging a disposable player."""

import json
from pathlib import Path
import re
from rubymarshal.classes import Symbol
from rubymarshal.reader import loads
from rubymarshal.writer import writes
from .maps.definitions import DEFINITIONS
from .runtime.development import replace_main

FIELDS = {
    "description",
    "base",
    "location",
    "checkpoint",
    "player",
    "pokemon",
    "party",
    "household",
    "bag",
    "story",
}


def catalog(root):
    return {
        f"{p.parent.parent.name}/{p.stem}": p
        for p in sorted((root / "src/tidebound/features").glob("*/scenarios/*.json"))
    }


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{path}: duplicate field {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(), object_pairs_hook=unique)
    if not isinstance(value, dict) or value.keys() - FIELDS:
        raise ValueError(f"{path}: unknown scenario fields")
    return value


def location(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("Location must be [map name, entrance name]")
    name, entrance = value
    if name not in DEFINITIONS or entrance not in DEFINITIONS[name].entrances:
        raise ValueError(f"Unknown map entrance: {value}")
    return [DEFINITIONS[name].id, *DEFINITIONS[name].entrances[entrance]]


def select(root, name):
    try:
        paths = catalog(root)
        if name not in paths:
            raise ValueError(f"Unknown scenario; available: {', '.join(paths)}")
        spec = read(paths[name])
        if base := spec.pop("base", None):
            if base not in paths:
                raise ValueError(f"Unknown base: {base}")
            parent = read(paths[base])
            if "base" in parent:
                raise ValueError("Scenario bases must be standalone (one level only)")
            # Only story merges by top-level key. Other fields replace as a whole.
            spec = {**parent, **spec, "story": {**parent.get("story", {}), **spec.get("story", {})}}
        if not isinstance(spec.get("description"), str) or not spec["description"].strip():
            raise ValueError("A scenario needs a description")
        spec["arrival"] = location(spec["location"])
        spec["checkpoint"] = location(spec.get("checkpoint", spec["location"]))
        player = spec.get("player", {"name": "Ren", "avatar": 1})
        if (
            set(player) != {"name", "avatar"}
            or not isinstance(player["name"], str)
            or not player["name"].strip()
            or type(player["avatar"]) is not int
        ):
            raise ValueError("Player requires name and avatar")
        players = loads((root / "game/Data/player_metadata.dat").read_bytes())
        if player["avatar"] not in players:
            raise ValueError("Unknown player avatar")
        spec["player"] = player
        databases = {
            kind: loads((root / f"game/Data/{kind}.dat").read_bytes())
            for kind in ("species", "items", "moves")
        }
        pokemon = spec.setdefault("pokemon", {})
        for key, record in pokemon.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
                raise ValueError(f"Invalid Pokémon key: {key}")
            if record.keys() - {"species", "level", "name", "moves", "item"}:
                raise ValueError(f"{key}: unknown Pokémon fields")
            if Symbol(record.get("species", "")) not in databases["species"]:
                raise ValueError(f"{key}: unknown species/form")
            if type(record.get("level")) is not int or not 1 <= record["level"] <= 100:
                raise ValueError(f"{key}: level must be 1–100")
            if "moves" in record and (
                not isinstance(record["moves"], list)
                or not 1 <= len(record["moves"]) <= 4
                or any(Symbol(move) not in databases["moves"] for move in record["moves"])
            ):
                raise ValueError(f"{key}: expected one to four known moves")
            if "name" in record and (
                not isinstance(record["name"], str) or not record["name"].strip()
            ):
                raise ValueError(f"{key}: name must be nonempty text")
            if "item" in record and Symbol(record["item"]) not in databases["items"]:
                raise ValueError(f"{key}: unknown held item")
        for group in ("party", "household"):
            keys = spec.setdefault(group, [])
            if (
                not isinstance(keys, list)
                or len(keys) != len(set(keys))
                or set(keys) - pokemon.keys()
            ):
                raise ValueError(f"{group}: unknown or duplicate Pokémon keys")
        if len(spec["party"]) > 6 or set(spec["party"]) & set(spec["household"]):
            raise ValueError("Party holds at most six Pokémon; household pets must be separate")
        pets = [pokemon[key]["species"].split("_")[0] for key in spec["household"]]
        if len(pets) != len(set(pets)):
            raise ValueError("Household pets must have distinct base species")
        for item, count in spec.setdefault("bag", {}).items():
            if (
                Symbol(item) not in databases["items"]
                or type(count) is not int
                or not 1 <= count <= 999
            ):
                raise ValueError(f"Invalid bag item/count: {item}")
        if not isinstance(spec.setdefault("story", {}), dict) or "household_pets" in spec["story"]:
            raise ValueError("Story must be an object; use household for pet references")
        return {"id": name, **spec}
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise ValueError(f"Scenario {name}: {error}") from error


def prepare(game, spec):
    driver = Path(__file__).with_suffix(".rb").read_bytes()
    driver += b'\nDevelopmentScenario.run(load_data("Data/Scenario.rxdata"))\n'
    replace_main(game, driver)
    (game / "Data/Scenario.rxdata").write_bytes(writes(spec))
