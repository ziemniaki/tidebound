"""The one rebuild plan used by development, CI and isolated regeneration."""

from .paths import ROOT
from .scripts.compiler import rebuild as scripts
from .maps.compiler import build as maps
from .maps.validate import validate
from .content import opening_items, quest_data, encounters, species_compiler, configure


def rebuild(root=ROOT, full=False):
    if full:
        maps(root)
        opening_items.build(root)
        quest_data.build(root)
        encounters.build(root)
        species_compiler.build(root)
    scripts(root)
    if full:
        configure.build(root)
        validate(root, root / "tools/generated/event_scripts.json")
