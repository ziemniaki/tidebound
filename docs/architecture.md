# Architecture

Tidebound extends Pokémon Essentials 21.1 on mkxp-z. Ruby owns gameplay; Python
owns authoring, compilation and packaging. The native RPG Maker layout stays in
`game/`; contributors edit the source owned by each feature or content bundle.

## Authored content

`content/` is the source of truth for custom game content. A directory identifies
one thing; its declaration and approved artwork live together. Compilers discover
bundles by their conventional filenames, without another registration list.

| Source | Owns | Native destination |
| --- | --- | --- |
| `content/pokemon/<ID>/species.json` + frame PNGs/optional cry | Species, metrics, artwork and explicit stock reuse | Species/PBS data, Pokémon sprites and cries |
| `content/items/<ID>/item.json` + icon | Story Key Item definition and artwork | Item data and `Graphics/Items/<ID>.png` |
| `content/trainers/<ID>/trainer.json` + portrait/character | Trainer type and artwork | Trainer data, portraits and walking sheets |
| `content/actors/<name>/character.png` | Named actor walking sheet | `Graphics/Characters/<name>.png` |
| `content/props/<name>/prop.json` + image | Picture, anchor and optional fixed layer | `Graphics/Pictures/props/<name>.png`, generated prop table |
| `content/maps/<name>/map.json` + `build.py` | Layout, events, entrances, encounters and map-only art | Native maps, metadata, encounters and packed tilesets |
| `content/audio/{music,ambience,effects,cues}/` | Approved Ogg playback files | `Audio/{BGM,BGS,SE,ME}/` respectively |
| `content/ui/`, `content/effects/` | Shared UI and effect PNGs | Corresponding subdirectories of `Graphics/Pictures/` |
| `content/tilesets/` | Shared approved tile overlays | Packed map textures and lighting |

Use **lower_snake_case** for authored directories and ordinary filenames. Engine
species/item/trainer IDs retain uppercase (`WHYDUCK`, `SUNKERN_1`, `TIDEBOUNDOILKEYS`),
and their bundle directory is the ID. Inside bundles use fixed roles such as
`species.json`, `front.png`, `back.png`, `icon.png`, `character.png`, `image.png`.
Display names belong in declarations and can change independently of IDs.
Do not repeat the project name in filenames or introduce numbered variants without
meaningful identities. Source paths and output paths are derived, not separately registered.

These conventions apply to authored content. Stock engine filenames, licenses,
standard project configuration names and `AGENTS.md` retain their required names.
`references/` holds concepts, MIDI compositions and working material outside the
build. Approved custom playback audio is Ogg; existing stock MIDI/Ogg assets keep
their engine paths. Export does not synthesize or transcode music.

The build rejects invalid content names, ambiguous audio outputs, missing source
files, duplicate output ownership and recipes reading previous generated outputs.
Workflow details and engine traps live in [content/AGENTS.md](../content/AGENTS.md)
and its scoped guides; those instructions serve humans and agents alike.

## Gameplay ownership

`src/tidebound/features/<feature>/` owns related quest state, actor policies,
presentation and declarative starting states. Small independent features can
remain one Ruby file. Only reusable rendering belongs in `presentation/`.
`domain/state.rb` owns engine-independent rules; `engine/` adapts Essentials;
`world/` owns shared navigation, actor policy application and temporary scenes.

Feature modules register actor availability without teaching shared actor code
quest names or story keys. Shared NPC interaction priority is explicit in
`features/interactions.rb`. `world/scenes.rb` restores temporary presentation and
movement after interruption; story and inventory changes remain the feature's
responsibility. Engine hooks may prepend to Essentials; features do not prepend
to one another.

`src/load_order.txt` controls Ruby load order. The script compiler rejects missing,
unlisted, duplicate and stale sources and embeds them immediately before Main.
Stock engine changes are explicit patches in `tools/tidebound_dev/scripts/patches.py`.
`tests/engine_reference/` is an ignored extraction for inspection, never source.

## Maps and generated files

Map declarations allocate stable event IDs, named entrances and actor ownership.
Builders use the shared APIs in `tools/tidebound_dev/maps/`; those tools contain
compilers and reusable drawing primitives, not individual map definitions.
Atlas groups bound texture allocation. Packed tiles retain their original source
IDs for passage and lighting metadata. Regeneration derives runtime geometry and
the world registry into `src/generated/`; handwritten Ruby never embeds copied maps.

`game/` is the RPG Maker project and stays tracked. It contains stock inputs that
cannot currently be recreated from custom sources, alongside generated data.
It is not a disposable build directory. The ownership records and validation
sidecars under `game/.generated/` also stay tracked: they identify removable custom
outputs and let checks validate committed maps without regenerating them. They
are excluded from player packages. Never edit them by hand.

Offline previews and disposable reports go to ignored `.build/maps/`. Full
regeneration produces them; deleting them does not affect playing or checking the
game. Native checks and packaging validate the tracked game and its sidecars.
Full rebuild retires removed custom records/files and replaces current outputs;
stock inputs are never swept. Isolated regeneration removes owned file outputs
and verifies that all tracked generated files can be reproduced.

The editor project is `game/Game.rxproj`. Direct editor changes to generated maps
must be reconciled with their source before full rebuild. Ordinary play refreshes
artwork and Ruby while preserving map geometry. The map compiler derives
Essentials' existing map revision from native map/tileset bytes; loading a save
refreshes stale cached maps without changing Pokémon or quest state.

## Saves

Release saves use `Tidebound_Opening_0_2`; development players use
`Tidebound_Development`. Declared starts and their scratch-save behavior are covered
once in the [playtest workflow](development.md#playtest-scenarios). Saves live in
the OS user-data directory, outside the checkout and app. RPG Maker Test Play
retains the project/release namespace.

Use Essentials' normal serialization, without custom save versions or migration
chains. Preserve the `TideboundSaveState` registration and existing companion
identity, forms, held items and quest progress. See [gameplay contracts](../src/AGENTS.md)
for battle outcomes, loss recovery and scene lifecycle requirements.

## Runtime boundaries

`tools/tidebound_dev/` is an installed package. The CLI aliases share one parser;
`pipeline.py` owns the rebuild order. Compilers/exporters accept explicit roots
for disposable regeneration. No tool modifies `sys.path` or invokes another
standalone generator script. Formatting owns its dependency setup; operations do
not import it from the CLI.

`runtime/` holds pinned engine inputs, provenance and the portable Mac patch.
Windows player/editor helpers restore from pinned archives into ignored locations.
Loose executable libraries stay untracked. The shared player staging pipeline
copies only native runtime files; platform adapters own layout, signing and
permissions. Release builds add archive round-trip verification. Publication and
native verification requirements live in [releasing](releasing.md).
