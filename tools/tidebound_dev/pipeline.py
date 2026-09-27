"""One complete export plan for the editor, development players and checks."""

from .scripts.compiler import rebuild as scripts
from .maps.compiler import build as maps
from .maps.validate import validate
from .maps import editor
from .content import story, encounters, species_compiler, configure, ownership, map_features
from .art import compiler as art


def rebuild(root):
    editor.require_import(root)
    # Once saved editor edits are reconciled, the following writes are exports.
    # A failed export must not be misidentified as new editor work on the retry.
    editor.close(root)
    art.build(root)
    ownership.prepare(root, ownership.inventory(root))
    areas = maps(root)
    map_features.build(root, areas)
    story.build(root)
    species_compiler.build(root)
    encounters.build(root)
    scripts(root)
    configure.build(root)
    validate(root, root / ".build/maps/event_scripts.json")
    editor.remember(root)
