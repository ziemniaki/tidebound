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

Run `uv run rebuild --all` to regenerate. Stage new sources and outputs before
`uv run check --all`, which uses tracked inputs. Native species verification checks
actual engine resolution; battle/party inspection checks visual composition.

Species design lives in [specs/species](../specs/species/). Retain
[attribution](credits.md) when replacing artwork.

Other approved PNGs mirror engine categories under `assets/characters`, `trainers`,
`items` and `pictures`. `art/files.py` owns conventional copies and stock aliases.
The seated Ivo sheet, dock pictures, lantern glow and beacon are editable pixels.
Map builders compose maps/tilesets; content builders write definitions, not images.
The map compiler still owns packed tilesets, autotiles and window-mask placement.
