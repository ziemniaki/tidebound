"""Rebuild tracked game files in dependency order; checks supply a disposable root."""

from .scripts.compiler import rebuild as scripts
from .maps.compiler import build as maps
from .maps.validate import validate
from .content import story, encounters, species_compiler, configure
from .art import compiler as art


def rebuild(root, *, full=False):
    if full:
        art.build(root)
        maps(root)
        story.build(root)
        # Encounters must see species added by this build.
        species_compiler.build(root)
        encounters.build(root)
    scripts(root)
    if full:
        configure.build(root)
        validate(root, root / "tools/generated/event_scripts.json")
