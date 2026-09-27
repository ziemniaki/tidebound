"""Explicit packing boundaries: maps in different groups never share a painter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Atlas:
    kind: str
    name: str
    texture: str


GROUPS = {
    "coast": Atlas("landscape", "Tidebound Landscape", "TideboundLandscape"),
    "fields": Atlas("landscape", "Tidebound Fields", "TideboundFields"),
    "lighthouse": Atlas("interior", "Tidebound Lighthouse", "TideboundLighthouse"),
    "storehouses": Atlas("interior", "Tidebound Storehouses", "TideboundStorehouses"),
    "dream": Atlas("interior", "Tidebound Dream", "TideboundDream"),
}
