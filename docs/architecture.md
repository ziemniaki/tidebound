# Architecture and editing map

Tidebound extends Pokémon Essentials 21.1 on mkxp-z. This layout separates
authoring inputs, playable engine files, tooling and documentation while keeping
the engine's expected directory structure intact inside `game/`.

## Where to make a change

| Area | Source | Generated/runtime output |
| --- | --- | --- |
| Rules, state, identity and recovery | `src/001_Core.rb` | `game/Data/Scripts.rxdata` |
| Essentials save/battle integration | `src/002_Essentials.rb` | Same script archive |
| Opening, quests and presentation | Numbered `src/004_*.rb` through `025_*.rb` | Same script archive |
| Map layouts and events | `tools/rebuild_maps.py`, `landscape.py`, `lighthouse_interiors.py`, `vault_maps.py`, `demo_maps.py`, `pond_map.py` and room modules | `game/Data/Map*.rxdata`, tilesets, previews/reports |
| Maze/pond/passage geometry | Map generators | `src/003_MapPassages.rb`, generated section of `018_PsychicMaze.rb`, `024_PondGeometry.rb` |
| Species, items, trainers, encounters | `tools/rebuild_*_data.py`, `rebuild_opening_items.py` | Matching `game/PBS/*.txt`, compiled `game/Data/*.dat` and generated sprites |
| Artwork | `assets/<species>/` sources and export recipes | `game/Graphics/` |
| Sound | `tools/create_audio.py`, existing attributed assets | `game/Audio/` |
| Engine packaging | `tools/package_*.py`, `release.json`, pinned `runtime/` | Ignored local builds or CI artifacts |

The Python map modules intentionally share a generator namespace. Keep that
loading order when changing them. Separating their internals into a new map
format is future work, not part of this directory migration.

## Ruby loading and ownership

`tools/rebuild_scripts.py` inserts all numbered `src/*.rb` in filename order
immediately before Essentials' Main entry. The game reads the compiled archive.
`tools/script_archive.py` rejects duplicate, out-of-order or stale custom entries
and a competing `Plugins/Tidebound` installation.

`001_Core` keeps game rules independent from the engine; `002_Essentials` adapts
native objects and battle/save hooks. Later numbered modules group opening,
coast, neighbour, vault, regional species, presentation and dream/hideout/pond
content. Extend focused modules as features grow. Do not rename persistent Ruby
classes merely to make filenames cleaner.

`tests/prepare_reference.py` extracts stock engine code into an ignored inspection
directory. Editing that extraction does not change the game. Stock scripts and
some compiled data have no separate authoritative source here: `game/Data/`
must remain tracked and must not be cleared like a conventional build folder.

## Maps and RPG Maker

The editor project is `game/Game.rxproj`. IDs 101–116 are generated story maps;
stock demo maps are retained. `tools/generated/` holds collision masks, event
reports, manifests and offline previews. Those are build outputs, not editable
map definitions. Reconcile direct editor changes with the generators before a
full rebuild. Ordinary `uv run play` only rebuilds scripts.

## Saves and behavior that must survive changes

Release saves use `Tidebound_Opening_0_2`. Development player copies use
`Tidebound_Development`. Both live in the OS user-data directory, outside the
checkout and app. The base editor project retains the release namespace.

`TideboundSaveState = Tidebound::State` supports Essentials' symbol-based class
validation. Keep existing class names, schema, Pokémon identities, forms, owner,
personal IDs, moves, held items, quest keys and event IDs unless an explicit
migration preserves them. An empty party is not evidence of a new game.

The loss adapter snapshots the party before Essentials' cleanup heals it.
Recovery restores the archived individual, not a replacement capture. Avoid
duplicate companions/items and memorials. Only outcome 1 advances trainer wins;
loss, draw and cancellation leave the encounter retryable. Technical failures
must preserve rollback behavior rather than becoming permanent narrative loss.

Use the existing wild/trainer wrappers and handle their astral-transfer result.
Death mechanics are not a global replacement for every engine blackout route.
Manual saves, provisional recovery balance and late-game state helpers are not
proof that the full final-game design is implemented.

## Runtime boundaries

`runtime/` contains immutable engine inputs, source/license/provenance and the
focused portable Mac patch. Windows player/editor files are restored from pinned
ZIPs into ignored directories; they are never manually downloaded as a prerequisite.
Packaging validates hashes and architecture before use. Loose `.exe`/`.dll`
files are ignored; source archives remain tracked for offline reproducibility.
This changes placement, not existing Git history or repository download size.

Keep game logic separate from developer commands in `tools/tidebound_dev/`.
The CLI delegates to the same packagers used by CI, then configures only the
disposable development copy with isolated saves. Release package checks and
provenance are described in [releasing](releasing.md).
