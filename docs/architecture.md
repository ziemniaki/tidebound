# Architecture and editing map

Tidebound extends Pokémon Essentials 21.1 on mkxp-z. This layout separates
authoring inputs, playable engine files, tooling and documentation while keeping
the engine's expected directory structure intact inside `game/`.

## Where to make a change

| Area | Source | Generated/runtime output |
| --- | --- | --- |
| Rules, state, identity and recovery | `src/tidebound/domain/state.rb` | `game/Data/Scripts.rxdata` |
| Essentials save/battle integration | `src/tidebound/engine/battles.rb` | Same script archive |
| Opening, quests and presentation | `src/tidebound/features/` and `src/tidebound/presentation/` | Same script archive |
| Map layouts and events | `tools/tidebound_dev/maps/` area builders and painters | `game/Data/Map*.rxdata`, tilesets, previews/reports |
| Maze/pond/passage geometry | Map generators | `src/generated/map_passages.rb`, `maze_geometry.rb`, `pond_geometry.rb` |
| Species, items, trainers, encounters | `tools/tidebound_dev/content/`, item/encounter builders | Matching `game/PBS/*.txt`, compiled `game/Data/*.dat` |
| Artwork | `assets/<species>/` inputs and `tools/tidebound_dev/art/` exporters | `game/Graphics/` |
| Sound | `tools/tidebound_dev/art/audio.py`, existing attributed assets | `game/Audio/` |
| Engine packaging | `tools/tidebound_dev/packaging/`, `release.json`, pinned `runtime/` | Ignored local builds or CI artifacts |

Map builders return independent in-memory areas. `maps/compiler.py` declares
composition explicitly: base areas, connections, landscape, interiors and harbor/
pond decoration. Painters own their tile atlases and caches; area modules receive
only the maps and painters they use. Imports never load or write game assets. Interaction targets are derived from
current event records; painters do not maintain a second position list.
Full rebuild generates maps, content, art and scripts in a temporary workspace,
then validates and publishes changed outputs. Failed generation/validation leaves
the checkout unchanged; publication errors roll back replaced files. This protects
ordinary I/O failures, not process termination midway through publication. Rebuild
after an interrupted publication. A failed rollback retains a reported recovery
directory rather than discarding the backups.

## Python operations

`tools/tidebound_dev/` is an installed Python package. `cli.py` gives the short uv
aliases and `tidebound <command>` one parser and command implementation;
`pipeline.py` is the single rebuild plan used by local development and isolated
regeneration. `scripts/`, `maps/`, `content/`, `art/`, `runtime/`, `packaging/` and
`release/` own callable operations. They accept explicit roots when operating on
a disposable copy. Modules do not modify `sys.path` or launch other generator
scripts. `formatting.py` owns the pinned Node/WASM and formatter setup used by checks;
operations never import setup from the CLI. `files.py` owns content hashing and
comparison, and `runtime/config.py` owns mkxp parsing and save namespaces.
The standalone GitHub comment dispatcher is in `.github/scripts/`.

## Regional data

`content/plants.py`, `insects.py` and `coastal.py` define forms, species and sprite
metrics using PBS field names; `content/species.py` is the combined catalog. `content/species_compiler.py` resolves templates, derives evolution
backlinks, validates references, then writes each database once. PBS text and
native attributes come from the same fields. Add a definition instead of another
executable builder. `content/story.py` writes all story Key Items in one database
pass and generates their PBS from the same fields, then builds trainer classes.
Artwork exports in `art/` are explicit functions; source
images remain in `assets/`.

## Ruby loading and ownership

`tools/tidebound_dev/scripts/compiler.py` embeds the files listed in `src/load_order.txt`
immediately before Essentials' Main. The manifest, not filenames or directory
sorting, controls the order. `tools/tidebound_dev/scripts/archive.py` rejects missing, duplicate,
unlisted, out-of-order or stale sources and a competing `Plugins/Tidebound` copy.

`src/tidebound/domain/state.rb` owns the engine-independent rules;
`engine/battles.rb` adapts native battle objects. `Tidebound.story` is the shared
state root; each feature owns its state transitions. `world/navigation.rb` owns
travel and actor movement, `world/atmosphere.rb` owns map lighting/passages, and
`engine/encounters.rb` owns shared party checks and encounter construction. Feature modules own
story behavior. Shared NPC interactions are dispatched explicitly in
`features/interactions.rb`; features do not prepend into one another. Engine
adapters can still prepend into Essentials interfaces.

Map definitions in `maps/definitions.py` own IDs, arrivals, music, metadata and
atmosphere. They feed native maps, PBS metadata, validation and generated runtime
settings. Map-qualified actor identities live in `maps/registry.py`; event roles
are authored beside their builders. Both compile to
`src/generated/world_registry.rb`. Python builders use that catalog, and Ruby
calls `World.travel(:road, ...)` or `World.actor(:mother)` instead of repeating
map IDs or event display names. Regeneration rejects missing, duplicate or misplaced actors;
headless integration verifies generated event calls against the loaded public API.

Generated Ruby is confined to `src/generated/`. Maze, pond and collision data are
whole generated files, never patches inside handwritten source. Necessary stock
engine modifications are declared and checked in `tools/tidebound_dev/scripts/patches.py`.

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

Tidebound uses Essentials' normal SaveData serialization without a custom version
or compatibility gate. New games initialize current state directly; historic
opening/map/species migrations are retired.

`TideboundSaveState = Tidebound::State` remains the native SaveData class
registration. Preserve current Pokémon identities, forms, owner, personal IDs,
moves, held items and quest state. An empty party is not evidence of a new game.

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
The CLI and CI share one player staging pipeline. Platform adapters own runtime
layout, signing and executable permissions. Development settings are applied
before signing; development builds publish the player directly. Release builds
add ZIP roundtrip verification and provenance manifests in an atomic transaction. Release package checks and
provenance are described in [releasing](releasing.md). `release/candidates.py`
assembles all platforms and the source archive; it does not invoke tests.
`release/artifacts.py` owns checksums and candidate validation for both normal
publication and explicit draft refresh. CI requires verification before packaging
and native launches before any release publication.

## Presentation and actor state

`features/actors.rb` synchronizes companion/key/crate collision during map updates,
independent of sprite creation. Generated roles carry species, soul index or
quest state key explicitly; readable labels do not select rendering or policy.
Its visibility rules are shared by the renderers.
Forced movement routes retain their collision ownership until the route finishes.

Code-drawn props inherit `Presentation::OwnedSprite`: it disposes the owned bitmap
exactly once and only disposes a viewport when explicitly owned. Native Pokémon
icons keep Essentials' resource lifecycle and share only the positioning mixin.
Drawing remains in focused presentation modules, including fields, docks and title.
