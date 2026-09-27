"""The one rebuild plan used by development, CI and isolated regeneration."""

from .paths import ROOT
from .generation import staged_outputs
from .scripts.compiler import rebuild as scripts
from .maps.compiler import generate as maps
from .maps.validate import validate
from .content import opening_items, quest_data, encounters, species_compiler, configure
from .art import compiler as art


def generate(root):
    maps(root)
    opening_items.build(root)
    quest_data.build(root)
    # Consumers must see species added in this build, not stale compiled inputs.
    species_compiler.build(root)
    encounters.build(root)
    art.build(root)
    scripts(root)
    configure.build(root)
    validate(root, root / "tools/generated/event_scripts.json")


def rebuild(root=ROOT, full=False):
    if not full:
        scripts(root)
        return
    with staged_outputs(
        root,
        inputs=("game", "src", "assets", "release.json"),
        outputs=("game", "src/generated", "tools/generated"),
    ) as stage:
        generate(stage)
