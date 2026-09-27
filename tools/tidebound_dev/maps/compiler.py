"""Construct and serialize maps; the rebuild plan validates the complete game."""

from dataclasses import dataclass
from pathlib import Path

from importlib import import_module
from .definitions import DEFINITIONS
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
    def tools(self):
        return self.root / "tools"


@dataclass
class BuildContext:
    paths: BuildPaths
    palette: LandscapePalette
    rooms: InteriorPainter


def construct(paths):
    context = BuildContext(paths, LandscapePalette(paths.game), InteriorPainter(paths.game))
    built = []
    for name, definition in sorted(DEFINITIONS.items(), key=lambda item: item[1].id):
        module = import_module(f"{__package__}.areas.{name}.build")
        area = module.build(context)
        if area.id != definition.id:
            raise ValueError(f"Map {name}: builder and declaration disagree")
        built.append((definition, module, area))
    landscape.save_atlas(paths, context.palette, [m for d, _, m in built if d.atlas == "landscape"])
    interior.save_atlas(paths, context.rooms, [m for d, _, m in built if d.atlas == "interior"])
    for _, module, area in built:
        if hasattr(module, "finish"):
            module.finish(context, area)
    return [area for _, _, area in built]


def build(root):
    paths = BuildPaths(root)
    maps = construct(paths)
    scenery.window_lights(paths, maps)
    serialize(paths, maps)
