# Asset sources

Approved custom sources live here; exported player files live in `game/`.
`references/` contains concepts and working material, never build inputs.
[Artwork ownership](../docs/artwork.md) lists the asset types and their owners.

## Pokémon sprites, forms and icons

1. Add approved PNGs under `pokemon/<ENGINE_ID>/`: `front.png`, `back.png`,
   `icon.png`. Use `SPECIES` for the base form and `SPECIES_1` for form 1, never
   `SPECIES_0` or comma IDs. Current battle canvases are 160×160; retain pixel
   scale and padding. Export does no quantization, resizing or alpha blending.
2. Register the ID in `tools/tidebound_dev/art/pokemon.py::POKEMON`. Declare its
   cry source and whether shiny artwork is distinct. `shiny=True` requires
   `front_shiny.png` and `back_shiny.png`; otherwise normal pixels are reused.
   Party icons currently share normal/shiny artwork. `stock` explicitly reuses
   stock sprites; the four palette recipes live in `art/recolors.py`.
3. Icons are a **horizontal strip of square frames**: Essentials takes image
   height as frame width. Our two 64×64 frames make a 128×64 image. A vertical
   strip is not equivalent. Preserve headroom; inspect centering in the party UI.
4. Stats and placement metrics belong to the [content owner](../tools/tidebound_dev/content/AGENTS.md).
   Do not offset PNGs and `METRICS` blindly together. Debug-editor metric changes
   are overwritten by regeneration.
5. Run `uv run rebuild --all`, stage source and outputs, then `uv run check --all`.
   Inspect front/back in battle and icons in the party screen. Native `species`
   checks exact normal/shiny/form paths and cries: Essentials' fallback to base
   sprites or `000` must not hide missing custom assets.

Art replacement of an existing form does not require changing gameplay data.
Use ordinary image tools or generation to prepare artwork, then approve the final
pixels. Do not add a bespoke production renderer for each Pokémon. Record external
provenance in [credits](../docs/credits.md). For audio, read the
[audio workflow](../tools/tidebound_dev/art/AGENTS.md).
