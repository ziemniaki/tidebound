# Pokémon artwork workflow

Retain source art under `assets/<species>/`; engine filenames use species IDs,
not display names. For stats/forms/evolutions, also read the
[content workflow](../tools/tidebound_dev/content/AGENTS.md). Art-only replacement
of an existing form does not require changing its gameplay definition.

## Find the owner before replacing a PNG

`tools/tidebound_dev/art/compiler.py::build` runs on full rebuild.
All repeatable game pixel exports run here using locked Pillow. Inputs are either
stock sprites plus a palette/detail recipe, retained Nivalora/Whyduck artwork, or
`pixels.png` atlases for Sunkern, Moonkern, Moonflora and Glaciverm. Each atlas is
320×224: front 160×160 at (0,0), back at (160,0), two-frame 128×64 icon at (0,160).
Edit those approved pixels directly; export only crops, without resampling.
Their high-resolution `reference.png` and prompts are design references. The retired
ImageMagick recipes did not reproduce shipped pixels on a current installation.
Do not re-quantize that reference art during a maintenance rebuild.

`art/compiler.py` makes species/form aliases and cry copies after their producers.
Editing generated destinations alone will be undone. Change the declared source.
The approved files under `Whyduck/pieces/` are build inputs; update those directly.
The source/exporter inventory is in [artwork](../docs/artwork.md).

## Add or replace an asset

1. Keep the approved source and export recipe together. For new repeatable
   exporters, put callable code in `tools/tidebound_dev/art/`, pass the destination
   game root explicitly and register it in the current export path. Importing an
   exporter must not write files. Do not add another shell-only export pipeline.
2. Export transparent PNGs into `game/Graphics/Pokemon/Front`, `Back`, `Front shiny`,
   `Back shiny`, and `Icons` as required by the approved design. Name base form
   `SPECIES.png`, form 1 `SPECIES_1.png`; **not** `SPECIES_0.png` or a comma ID.
   Existing custom battle canvases are usually 160×160; this is a project art
   convention, not an engine limit. Preserve native pixel scale and positioning.
3. Icons are a **horizontal strip of square frames**: the engine takes image
   height as frame width. Existing custom icons are two 64×64 frames, hence
   128×64. A 64×128 vertical strip is not equivalent. Icon centering assumes space
   above the figure; inspect it in the party UI, not only in an image viewer.
4. Adjust sprite placement through `METRICS` in the content definitions and
   regenerate; manual debug-editor metric changes otherwise disagree with the
   generator. Do not offset the PNG and the metrics blindly at the same time.
5. Check the exact filename resolved for the intended species/form, normal/shiny
   and front/back. Essentials deliberately falls back to normal/base/`000` art;
   “a bitmap loaded” does not prove the requested asset exists. Reusing normal art
   for shiny is an explicit art decision, not evidence of a shiny design.
6. Run the actual exporter, then full rebuild if its outputs are pipeline-owned;
   stage source and outputs before `check --all`. Inspect front/back in battle and
   icons in the party screen. Native `species` derives its roster from content definitions and checks exact
   resolved paths, icon layout and cries. Declare deliberate cry reuse in
   `content/verification.py`; missing artwork cannot pass via a placeholder.
   Record provenance/credit in `docs/credits.md` when adding outside assets.

For cries, use [audio workflow](../tools/tidebound_dev/art/AGENTS.md). Resolver and icon-frame
implementation: [Essentials contracts](../docs/essentials-contracts.md).
