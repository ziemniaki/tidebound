"""Validate a native, fixed-destination Transfer Player command."""

from dataclasses import dataclass
from .registry import MAP_NAMES


@dataclass(frozen=True)
class Transfer:
    map_id: int
    x: int
    y: int
    direction: int = 2

    def validate(self, masks):
        if any(type(value) is not int for value in (self.map_id, self.x, self.y, self.direction)):
            raise ValueError("Transfer coordinates/map/direction must be integers")
        if self.direction not in (2, 4, 6, 8):
            raise ValueError(f"Invalid transfer direction {self.direction}")
        mask = masks.get(str(self.map_id))
        if mask is None or self.map_id not in MAP_NAMES:
            raise ValueError(f"Unknown transfer map {self.map_id}")
        if not (0 <= self.y < len(mask) and 0 <= self.x < len(mask[self.y])):
            raise ValueError(f"Transfer outside map {self.map_id}: {self.x},{self.y}")
        if mask[self.y][self.x] != "1":
            raise ValueError(f"Blocked transfer to map {self.map_id}: {self.x},{self.y}")
