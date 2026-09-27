# Asset ownership

Approved artwork is build input, not a recipe to reinterpret on every build.
`assets/references/` retains concepts and working pieces outside the export path.
The [asset guide](../assets/AGENTS.md) covers Pokémon naming and engine contracts.

| Assets | Authoritative input | Export owner |
| --- | --- | --- |
| Sunkern form, Moonkern, Moonflora, Glaciverm, Lapras form, Nivalora, Whyduck | `assets/pokemon/<ENGINE_ID>/{front,back,icon}.png` | `art/pokemon.py` |
| Whyduck shiny | `assets/pokemon/WHYDUCK/{front_shiny,back_shiny}.png` | Same bundle |
| Wurmple form, Frostcoon, Ekans/Arbok forms | Stock sprites and `art/recolors.py` palettes | Same bundle |
| Psyduck form | Explicit stock reuse in `art/pokemon.py::POKEMON` | Same bundle |
| Pokémon cries | Cry source in each `POKEMON` record | `art/compiler.py` |

All custom Pokémon export exact engine filenames, including cries. Shiny reuse
is explicit; native checks consume the same inventory. Recoloring preserves source
geometry and alpha. Approved PNG export preserves all pixels without resampling.
Current battle canvases are 160×160 and icons are horizontal 128×64 strips.

Run `uv run rebuild` to refresh standalone assets; use `--all` for map atlases and lighting. Stage new sources and outputs before
`uv run check --all`, which uses tracked inputs. Native species verification checks
actual engine resolution; battle/party inspection checks visual composition.

Species design lives in [specs/species](../specs/species/). Retain
[attribution](credits.md) when replacing artwork.

Other approved PNGs mirror engine categories under `assets/characters`, `trainers`,
`items` and `pictures`. `art/files.py` owns conventional copies and stock aliases.
The seated Ivo sheet, dock pictures, lantern glow and beacon are editable pixels.
Map builders compose maps/tilesets; content builders write definitions, not images.
The map compiler still owns packed tilesets, autotiles and window-mask placement.

`tools/generated/assets.json` records generated custom files and their producer.
It is derived, not a second authoring catalog. `files.py` and `pokemon.py` declare
source/destination pairs; the writer and ownership checks consume those same
records. Prop export, map references and previews share `props.py` validation. Duplicate destinations (including
case collisions) and recipes reading generated outputs fail before export.
Removing a declaration removes its former output on the next export; stock kit
files are never swept. `check --all` clears declared custom exports in its isolated
copy before rebuilding, so stale committed PNGs cannot hide a missing exporter.

Approved custom audio lives in `assets/audio/<category>/` and exports byte-for-byte.
The two ambient loops are approved sources; builds need no NumPy or ffmpeg.

`assets/props.json` owns world-picture anchors and optional fixed layers. It emits
`src/generated/prop_assets.rb`; maps reference these asset keys. Lamps, archive
props, household props, warm light, title backdrop and fold runes use approved
PNGs. Ruby handles movement, flicker, text and story state. Small threshold marks
and genuinely dynamic drawing remain in Ruby.

Window lighting uses the approved `assets/tilesets/Outside/windows.png` overlay.
Map packing retains source tile identities so masks survive atlas compaction.
This restores two road/storehouse window panes that the old final-tile heuristic
missed. Existing coast/dock masks retain their pixels and placements.

Stock fonts, battlebacks, animations and interface resources remain supplied
engine inputs under `game/`. Their filenames can be resolved dynamically; a text
search cannot establish that they are unused. New scene-specific UI art can use
`assets/pictures/`; stock-format replacements require the owning Essentials scene's
contract. Keep `fontHeightReporting: 1`; font loading and metrics need native
inspection. Battleback metadata names a set (`_bg`, `_base0`, `_base1`, `_message`),
not a single picture. Animation databases reference numbered graphics; do not
rename those independently of their data. See [engine contracts](essentials-contracts.md).
