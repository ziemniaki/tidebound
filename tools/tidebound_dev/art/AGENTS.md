# Asset pipeline

For approved image layouts and prop authoring, use [content/AGENTS.md](../../../content/AGENTS.md).

## Pipeline ownership

`pipeline.rebuild` calls `compiler.build` for every play/build/preview/rebuild.
`uv run rebuild --all` also runs map/content compilers. Pipeline entry points:

| Change | Owner in this directory |
| --- | --- |
| File discovery / stock aliases | `files.py::exports` / bundle declarations |
| Pokémon bundle, shiny or cry reuse | `content/pokemon/<ID>/species.json::art` |
| File writing / image or audio checks | `export.py::Export.write` |
| Prop metadata validation / Ruby table | `props.py::load` / `write` |
| Native preview selection / rendering | `preview.py` / `preview.rb` |

Content bundles are discovered without registration; source IDs determine destinations.
`files.exports` and `pokemon.exports` supply the same records to writing and
`ownership.inventory`; do not add a second source/output list. Destinations are
repository-relative POSIX paths (`game/...`); sources use the supplied root.
Maps register packed textures in `ownership.MAP_OUTPUTS`. `game/.generated/assets.json`
is derived: never hand-edit it or use generated exports as recipe inputs.

Keep retirement **before** writing replacements: case-only renames can otherwise
delete fresh files on macOS/Windows. Fix failed builds and rerun; there is no rollback.
Map references and previews use `props.load`, not separate JSON parsing/validation.
Verify pipeline changes with `uv run check --all` after staging new files: it removes
owned exports in an isolated copy and proves they rebuild from source.
