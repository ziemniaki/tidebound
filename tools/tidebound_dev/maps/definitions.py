"""One definition for each map's arrivals, music, metadata and atmosphere."""

from dataclasses import dataclass, field
from ..catalog import bundles
from ..paths import ROOT
from rubymarshal.classes import Symbol

ATMOSPHERES = {
    "indoor": {"tone": [-8, -14, -25, 12], "fog": "", "opacity": 0, "speed": 1},
    "night": {"tone": [-80, -74, -48, 150], "fog": "smoke", "opacity": 24, "speed": 1},
    "astral": {"tone": [-55, -46, -20, 160], "fog": "smoke", "opacity": 95, "speed": -2},
    "hideout": {"tone": [-35, -32, -25, 95], "fog": "", "opacity": 0, "speed": 1},
    "vault": {"tone": [-38, -38, -30, 65], "fog": "", "opacity": 0, "speed": 1},
    "folded": {"tone": [-20, -30, -12, 25], "fog": "", "opacity": 0, "speed": 1},
}


@dataclass(frozen=True)
class MapDefinition:
    id: int
    entrances: dict[str, list[int]]
    name: str = ""
    actor_settings: dict = field(default_factory=dict)
    events: dict[str, int] = field(default_factory=dict)
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
        if len(set(self.events.values())) != len(self.events) or any(
            type(i) is not int or i < 1 for i in self.events.values()
        ):
            raise ValueError(f"Map {self.id}: event IDs must be unique positive integers")
        if not self.entrances or any(
            len(p) != 3 or p[2] not in (2, 4, 6, 8) for p in self.entrances.values()
        ):
            raise ValueError(f"Map {self.id} needs at least one arrival")
        if self.atmosphere not in ATMOSPHERES:
            raise ValueError(f"Map {self.id}: unknown atmosphere {self.atmosphere}")

    @property
    def actors(self):
        return {
            info["key"]: {
                "label": info["key"],
                "role": info.get("role", "npc"),
                "species": info.get("species", ""),
            }
            for info in self.actor_settings.values()
            if info.get("key")
        }

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


# Map declarations are discovered before composing encounters and actor registries.
DEFINITIONS = {
    name: MapDefinition(**record) for name, record in bundles(ROOT, "maps", "map.json").items()
}
BY_ID = {definition.id: definition for definition in DEFINITIONS.values()}
if len(BY_ID) != len(DEFINITIONS):
    raise ValueError("Map definitions contain duplicate IDs")
