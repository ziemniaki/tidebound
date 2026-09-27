# Asset pipeline

Image layouts and prop authoring: [content/AGENTS.md](../../../content/AGENTS.md).
Follow the parent [tooling guide](../AGENTS.md). `pipeline.rebuild` calls
`compiler.build` for every play/build/preview; extend that shared path.

| Change | Owner in this directory |
| --- | --- |
| File discovery / stock aliases | `files.py::exports` / bundle declarations |
| Pokémon bundle, shiny or cry reuse | `content/pokemon/<ID>/species.json::art` |
| File writing / image or audio checks | `export.py::Export.write` |
| Prop metadata validation / Ruby table | `props.py::load` / `write` |
| Native preview selection / rendering | `preview.py` / `preview.rb` |

`files.exports` and `pokemon.exports` supply the same records to writing and
`ownership.inventory`; do not add a second source/output list. Destinations are
repository-relative POSIX paths (`game/...`); sources use the supplied root.
Fixed tile bundles export through `maps/tilesets.py`; only the packed runtime light
sheet belongs in `ownership.MAP_OUTPUTS`. `game/.generated/assets.json`
is derived: never hand-edit it or use generated exports as recipe inputs.

The pipeline first restores the baseline and native overrides; exporters never
consume a previous build. Authored bundles may intentionally replace stock assets.
Removing or renaming a bundle needs no retirement code. Override paths must not
also be owned by a bundle. Map references and previews use `props.load`, not
separate JSON parsing/validation. Run `uv run check --all` after staging new sources
for a complete clean-build comparison.
