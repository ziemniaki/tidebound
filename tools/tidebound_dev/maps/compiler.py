"""Construct and serialize maps; the rebuild plan validates the complete game."""

from dataclasses import dataclass
from pathlib import Path

from runpy import run_path
from types import SimpleNamespace
from .definitions import DEFINITIONS
from .atlases import GROUPS
from . import landscape, interior, scenery
from .interior import InteriorPainter
from .landscape_painter import LandscapePalette
from .serialization import serialize


@dataclass(frozen=True)
class BuildPaths:
    root: Path

    @property
    def game(self):
        return self.root / "game"

    @property
    def generated(self):
        return self.game / ".generated"


@dataclass
class BuildContext:
    paths: BuildPaths
    palette: LandscapePalette | None = None
    rooms: InteriorPainter | None = None


def contexts(paths):
    result = {None: BuildContext(paths)}
    for key, group in GROUPS.items():
        if group.kind == "landscape":
            result[key] = BuildContext(paths, palette=LandscapePalette(paths.game))
        elif group.kind == "interior":
            result[key] = BuildContext(paths, rooms=InteriorPainter(paths.game))
        else:
            raise ValueError(f"Unknown atlas kind: {group.kind}")
    return result


def construct(paths):
    groups = contexts(paths)
    built = []
    for name, definition in sorted(DEFINITIONS.items(), key=lambda item: item[1].id):
        module = SimpleNamespace(**run_path(str(paths.root / "content/maps" / name / "build.py")))
        area = module.build(groups[definition.atlas])
        if area.id != definition.id:
            raise ValueError(f"Map {name}: builder and declaration disagree")
        built.append((definition, module, area))
    for key, group in GROUPS.items():
        maps = [m for d, _, m in built if d.atlas == key]
        context = groups[key]
        if group.kind == "landscape":
            landscape.save_atlas(paths, context.palette, maps, group)
        else:
            interior.save_atlas(paths, context.rooms, maps, group)
    for definition, module, area in built:
        if hasattr(module, "finish"):
            module.finish(groups[definition.atlas], area)
    return [area for _, _, area in built]


def build(root):
    paths = BuildPaths(root)
    paths.generated.mkdir(parents=True, exist_ok=True)
    (root / ".build/maps").mkdir(parents=True, exist_ok=True)
    maps = construct(paths)
    scenery.window_lights(paths, maps)
    serialize(paths, maps)
