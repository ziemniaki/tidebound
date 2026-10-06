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
| `content/maps/<name>/map.json` + `layout.json` | Layout, native event pages, entrances and encounters | Native maps, metadata and encounters |
| `content/audio/{music,ambience,effects,cues}/` | Approved Ogg playback files | `Audio/{BGM,BGS,SE,ME}/` respectively |
| `content/ui/`, `content/effects/` | Shared UI and effect PNGs | Corresponding subdirectories of `Graphics/Pictures/` |
| `content/tilesets/` | Fixed native tile sheets, flags and light masks | Tilesets and lighting |

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
Native map records live in readable JSON; builds serialize them without executing
layout generators. Fixed tileset IDs and square positions preserve tile references
across map edits. Native passage/terrain tables are shared with RPG Maker; the game
has no separate collision override. Derived geometry, lighting and the world
registry are written to `src/generated/`.

`game/` is an ignored, generated RPG Maker project. Each build extracts the
hash-pinned, offline `runtime/essentials/base.zip`, applies `content/overrides/`,
then compiles authored bundles and Ruby. Previous outputs are never inputs.
The baseline's [provenance](../runtime/essentials/README.md) describes the curated
Essentials snapshot; it is not a pristine upstream distribution.

`content/overrides/` holds intentional native stock changes and project defaults,
using engine-relative paths. Authored bundles take precedence over stock content;
an override cannot also target a generated file with an authored owner. Maps and
tilesets keep their dedicated JSON workflow. Stock native edits are imported as
explicit overrides; generated files without an importer must be edited at source.

`src/generated/`, `game/.generated/` and `.build/maps/` contain derived Ruby,
validation inventories and reports. None is committed or needed on a fresh
checkout. Removing a declaration removes its output on the next build, without
retirement manifests or record cleanup. `check` builds before verifying;
`check --all` also builds from Git-tracked sources in isolation and compares the
complete generated game and Ruby, including decoded PNG pixels.

Inspect map appearance in RPG Maker or the native player.

The [RPG Maker workflow](development.md#rpg-maker) imports saved edits back into
these sources. Play/build compile current authored content. The map compiler derives
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
Windows players restore from pinned archives into ignored locations; optional
editor utilities remain archived for manual use.
Loose executable libraries stay untracked. The shared player staging pipeline
copies only native runtime files; platform adapters own layout, signing and
permissions. Release builds add archive round-trip verification. Publication and
native verification requirements live in [releasing](releasing.md).

## Local lighting prototype

`presentation/lighting.rb` owns the screen light field. Selected maps opt in through
`map.json::lighting`; other maps retain their existing atmosphere. Ambient brightness
and local visibility are independent from the map's colour tone. Local illumination
reveals the original scene rather than painting an opaque glow over it. Warm colour
adds a small tint after illumination; overlapping lights approach full visibility
without adding unbounded brightness. UI viewports remain above the light field.

Authoring controls:

| Property | Units and meaning |
| --- | --- |
| `ambient` | 0–100 brightness; 100 leaves scenery undimmed |
| `tone` | Native `[red, green, blue, grey]` atmosphere; avoid using large negative values as a second darkness layer |
| `player` | Neutral visibility source; same radius/strength/softness controls as other lights |
| `sources` | Lights anchored to an explicit `event` ID or fixed `position: [x, y]` in tiles |
| `radius`, `strength`, `softness` | Tiles, 0–1 contribution, and 0.1–1 fraction devoted to smooth edge falloff |
| `color`, `stretch` | RGB warmth and ellipse proportions, default white and `[1, 1]` |
| `offset`, `flicker` | Pixel offset from event centre; subtle source-strength variation, 0–0.1 |
| `flag` | Optional story key controlling whether a placed source is lit |
| `bounds`, `blockers` | Tile rectangles `[x, y, width, height]`; room/source limits and opaque barriers |
| `north_fade` | Smooth ambient gradient from `from_y` to a northern `to_y`, with target `ambient` |

Light blockers are authored independently of walking collision. Water, chairs and
small props are not implicitly opaque. Put sources in front of a wall, not inside
its blocker. Source bounds override room bounds. This prototype does not provide
height-aware shadows, beams or automatically inferred tree/building silhouettes.

An item's optional `item.json::light` record uses the same source properties.
The item compiler generates `Lighting::ITEM_LIGHTS` and native/PBS field-use data.
Use in the bag toggles an explicitly active item, saved in existing story state;
ownership alone never lights it. The Hand Lantern is supplied only by the
`lighting/forest` development scenario, with a temporary stock icon. Its acquisition,
fuel and quest role remain undesigned. No release-save migration is required.

The field samples every four world pixels, caches source falloff, culls off-screen
sources and only uploads changed fields through the bundled runtime's `Bitmap#raw_data=`.
Each spriteset owns and disposes its bitmaps/viewport. Only the current connected map
renders a screen mask. Native `world` verification captures the prototype, checks
lighthouse switching, movement, lantern save/load and disposal, and reports render
cost. Hardware performance and the final visual balance still need player review.
