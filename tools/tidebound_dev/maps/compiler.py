"""Construct and serialize maps; the rebuild plan validates the complete game."""

from dataclasses import dataclass
from pathlib import Path

from .areas import (
    home,
    coast,
    forest,
    lantern,
    astral,
    shop,
    bedroom,
    road,
    hideout,
    basement,
    vault,
    docks,
    museum,
    maze,
    dream,
    folded,
)
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


def construct(paths):
    palette = LandscapePalette(paths.game)
    rooms = InteriorPainter(paths.game)
    # Explicit atlas allocation order keeps generated tiles deterministic.
    wood = forest.build(palette)
    village = coast.build(palette)
    route = road.build(paths, palette)
    quay = docks.build(paths, palette)
    bed = bedroom.build(rooms)
    house = home.build(rooms)
    tower = lantern.build(paths, rooms)
    cellar = basement.build(rooms)
    archive = vault.build(rooms)
    puzzle = maze.build(paths, rooms)
    dream_room = dream.build(paths, rooms)
    folded_room = folded.build(paths, rooms)
    storehouse = hideout.build(paths, rooms)
    landscape.save_atlas(paths, palette, [village, wood, route, quay])
    interior.save_atlas(
        paths,
        rooms,
        [bed, house, tower, cellar, archive, puzzle, dream_room, folded_room, storehouse],
    )
    coast.save_tileset(paths, village)
    road.save_tileset(paths, palette, route)
    return sorted(
        [
            house,
            village,
            wood,
            tower,
            astral.build(),
            shop.build(),
            bed,
            route,
            storehouse,
            cellar,
            archive,
            quay,
            museum.build(),
            puzzle,
            dream_room,
            folded_room,
        ],
        key=lambda area: area.id,
    )


def build(root):
    paths = BuildPaths(root)
    maps = construct(paths)
    scenery.generate(paths, maps)
    serialize(paths, maps)
