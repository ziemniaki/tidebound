"""Construct, validate and publish generated maps from a disposable workspace."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile

from . import areas, vault, landscape, lighthouse, maze, dream, folded, hideout, harbor, pond
from . import dock_life
from .interior import InteriorPainter
from .landscape_painter import LandscapePalette
from .serialization import serialize
from .shoreline import coastal_shoreline, shoreline


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
    home = areas.build_home()
    coast = areas.build_coast()
    forest = areas.build_forest()
    lantern = areas.build_lantern()
    astral = areas.build_astral()
    shop = areas.build_shop()
    bedroom = areas.build_bedroom()
    road = areas.build_road()
    storehouse = areas.build_hideout()
    vault.connect(home, road)
    basement = vault.build_basement()
    archive = vault.build_vault()
    docks = vault.build_docks()
    museum = vault.build_museum()
    for area in (coast, road, docks):
        coastal_shoreline(area)
    shoreline(forest)
    palette = LandscapePalette(paths.game)
    landscape.decorate(paths, palette, coast, forest, road, docks)
    interior = InteriorPainter(paths.game)
    lighthouse.decorate(paths, interior, bedroom, home, lantern, basement, archive)
    puzzle = maze.build(paths, interior)
    bedroom_dream = dream.build(paths, interior)
    bedroom_folded = folded.build(paths, interior)
    hideout.decorate(paths, interior, storehouse)
    lighthouse.save_atlas(
        paths,
        interior,
        [
            bedroom,
            home,
            lantern,
            basement,
            archive,
            puzzle,
            bedroom_dream,
            bedroom_folded,
            storehouse,
        ],
    )
    harbor.decorate(paths, coast, docks, road)
    pond.decorate(paths, palette, road)
    dock_life.decorate(paths, docks)
    return [
        home,
        coast,
        forest,
        lantern,
        astral,
        shop,
        bedroom,
        road,
        storehouse,
        basement,
        archive,
        docks,
        museum,
        puzzle,
        bedroom_dream,
        bedroom_folded,
    ]


def build(root):
    # Keep authored input untouched until every map and transfer validates.
    from tidebound_dev.files import equivalent
    from tidebound_dev.maps.validate import validate

    with tempfile.TemporaryDirectory(prefix="tidebound-maps-") as temp:
        paths = BuildPaths(Path(temp))
        shutil.copytree(root / "game", paths.game)
        (paths.tools / "generated").mkdir(parents=True)
        (paths.root / "src/generated").mkdir(parents=True)
        serialize(paths, construct(paths))
        validate(paths.root, paths.tools / "generated/event_scripts.json", check_scripts=False)
        for directory in ("game", "tools/generated", "src/generated"):
            for source in (paths.root / directory).rglob("*"):
                if not source.is_file():
                    continue
                target = root / source.relative_to(paths.root)
                if target.exists() and equivalent(target, source):
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
