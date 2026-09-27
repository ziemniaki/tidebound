"""One definition for each map's arrivals, music, metadata and atmosphere."""

from dataclasses import dataclass
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
    arrivals: tuple[tuple[int, int], ...]
    atmosphere: str = "indoor"
    music: str = "Tidebound Stillness"
    battleback: str = "field"
    environment: str = "None"
    outdoor: bool = False
    night: bool = True

    def __post_init__(self):
        if not self.arrivals:
            raise ValueError(f"Map {self.id} needs at least one arrival")
        if self.atmosphere not in ATMOSPHERES:
            raise ValueError(f"Map {self.id}: unknown atmosphere {self.atmosphere}")

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
        return {**ATMOSPHERES[self.atmosphere], "night": self.night}


DEFINITIONS = {
    "home": MapDefinition(101, ((6, 10), (10, 12), (16, 4), (6, 4))),
    "coast": MapDefinition(
        102, ((32, 36), (48, 25), (45, 32), (77, 40)), "night", "Tidebound Shore"
    ),
    "forest": MapDefinition(103, ((17, 25), (11, 22)), "night", environment="Forest"),
    "lantern": MapDefinition(104, ((6, 9),)),
    "astral": MapDefinition(105, ((15, 21),), "astral", battleback="cave1", environment="Cave"),
    "shop": MapDefinition(106, ((8, 10),)),
    "bedroom": MapDefinition(107, ((6, 8), (8, 10))),
    "road": MapDefinition(108, ((18, 5), (35, 43), (26, 39)), "night"),
    "hideout": MapDefinition(109, ((11, 14),), "hideout"),
    "basement": MapDefinition(110, ((6, 13), (17, 5)), "vault"),
    "vault": MapDefinition(111, ((12, 15),), "vault"),
    "docks": MapDefinition(112, ((11, 28), (32, 23)), "night"),
    "museum": MapDefinition(113, ((14, 18),)),
    "maze": MapDefinition(114, ((5, 20), (4, 11), (9, 17), (22, 5), (16, 4))),
    "dream": MapDefinition(115, ((7, 8), (4, 7), (7, 5), (9, 8))),
    "folded": MapDefinition(116, ((7, 22), (25, 7)), "folded"),
}
BY_ID = {definition.id: definition for definition in DEFINITIONS.values()}
if len(BY_ID) != len(DEFINITIONS):
    raise ValueError("Map definitions contain duplicate IDs")
