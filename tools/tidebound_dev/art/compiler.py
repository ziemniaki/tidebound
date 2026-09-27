"""Export game assets after content data has compiled successfully."""

import shutil
from ..content.species import CRIES
from . import atlas, lapras, nivalora, recolors, whyduck


def build(root):
    game = root / "game"
    for target, source in CRIES.items():
        shutil.copy2(game / f"Audio/SE/Cries/{source}.ogg", game / f"Audio/SE/Cries/{target}.ogg")
    atlas.generate(game, root / "assets")
    nivalora.generate(game, root / "assets/Nivalora")
    lapras.generate(game)
    for folder in ("Front", "Back", "Front shiny", "Back shiny", "Icons"):
        sprites = game / "Graphics/Pokemon" / folder
        shutil.copy2(sprites / "PSYDUCK.png", sprites / "PSYDUCK_1.png")
    recolors.generate(game)
    whyduck.generate(game, root / "assets/Whyduck/pieces")
