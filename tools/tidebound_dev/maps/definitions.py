"""One definition for each map's arrivals, music, metadata and atmosphere."""

from dataclasses import dataclass, field
from ..catalog import bundles
from rubymarshal.classes import Symbol

ATMOSPHERES = {
    "indoor": {"tone": [-8, -14, -25, 12], "fog": "", "opacity": 0, "speed": 1},
    "night": {"tone": [-80, -74, -48, 150], "fog": "smoke", "opacity": 24, "speed": 1},
    "haunted": {"tone": [-112, -112, -88, 220], "fog": "smoke", "opacity": 38, "speed": -1},
    "lightless": {"tone": [-168, -172, -160, 230], "fog": "", "opacity": 0, "speed": 1},
    "astral": {"tone": [-55, -46, -20, 160], "fog": "smoke", "opacity": 95, "speed": -2},
    "hideout": {"tone": [-35, -32, -25, 95], "fog": "", "opacity": 0, "speed": 1},
    "vault": {"tone": [-38, -38, -30, 65], "fog": "", "opacity": 0, "speed": 1},
    "folded": {"tone": [-20, -30, -12, 25], "fog": "", "opacity": 0, "speed": 1},
}


@dataclass(frozen=True)
class MapDefinition:
    id: int
    entrances: dict[str, list[int]] = field(default_factory=dict)
    name: str = ""
    actor_settings: dict = field(default_factory=dict)
    retired_event_ids: list[int] = field(default_factory=list)
    parent_id: int = 0
    order: int | None = None
    encounters: dict = field(default_factory=dict)
    wild_forms: dict[str, int] = field(default_factory=dict)
    atmosphere: str = "indoor"
    battleback: str = "field"
    environment: str = "None"
    outdoor: bool = False
    night: bool = True
    origin: tuple[int, int] = (0, 0)

    def __post_init__(self):
        keys = [v["key"] for v in self.actor_settings.values() if v.get("key")]
        if len(set(keys)) != len(keys):
            raise ValueError(f"Map {self.id}: duplicate actor identity")
        if type(self.id) is not int or self.id < 1:
            raise ValueError("Map IDs must be positive integers")
        if len(set(self.retired_event_ids)) != len(self.retired_event_ids) or any(
            type(i) is not int or i < 1 for i in self.retired_event_ids
        ):
            raise ValueError(f"Map {self.id}: retired event IDs must be unique positive integers")
        if any(
            len(p) != 3
            or any(type(v) is not int for v in p)
            or p[0] < 0
            or p[1] < 0
            or p[2] not in (2, 4, 6, 8)
            for p in self.entrances.values()
        ):
            raise ValueError(f"Map {self.id}: arrivals require [x, y, direction]")
        if self.atmosphere not in ATMOSPHERES:
            raise ValueError(f"Map {self.id}: unknown atmosphere {self.atmosphere}")

    @property
    def arrivals(self):
        return tuple(tuple(point[:2]) for point in self.entrances.values())

    def metadata(self, name):
        return {
            "Name": name,
            "ShowArea": True,
            "Outdoor": self.outdoor,
            "BattleBack": self.battleback,
            "Environment": self.environment,
        }

    def native_metadata(self, name):
        attributes = {
            "Name": "@real_name",
            "ShowArea": "@announce_location",
            "Outdoor": "@outdoor_map",
            "BattleBack": "@battle_background",
            "Environment": "@battle_environment",
        }
        return {
            attributes[key]: Symbol(value) if key == "Environment" else value
            for key, value in self.metadata(name).items()
        }

    def pbs_metadata(self, name):
        values = self.metadata(name)
        # Omitted engine defaults preserve the existing readable PBS encoding.
        return {
            key: value for key, value in values.items() if value is not False and value != "None"
        }

    def runtime_settings(self):
        return {**ATMOSPHERES[self.atmosphere], "night": self.night, "origin": self.origin}


def load(root):
    definitions = {
        name: MapDefinition(**record) for name, record in bundles(root, "maps", "map.json").items()
    }
    if len({d.id for d in definitions.values()}) != len(definitions):
        raise ValueError("Map definitions contain duplicate IDs")
    return definitions
