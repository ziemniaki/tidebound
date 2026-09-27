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
   cry source and whether shiny artwork is distinct. For an original cry, set
   `cry` to the asset's own ID and add `cry.ogg` to its source bundle. `shiny=True` requires
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

## Characters, trainers, item icons and pictures

Put approved PNGs in `characters/`, `trainers/`, `items/` or `pictures/`; paths
below that directory become paths below `game/Graphics/<Category>/`. Reuse stock
art explicitly in `art/files.py::ALIASES`. Do not copy artwork in a content or map
builder. Every output has one source; an approved file and an alias cannot own
the same destination.

Characters use XP's **four columns × four rows**, in down/left/right/up order.
The frame canvas includes transparent padding; equal division alone cannot prove
correct feet alignment or direction order. Inspect all directions in the engine.
Trainer battle portraits and Pokémon party icons are different formats; never
use a party strip as a walking charset. Trainer IDs must match the content record.
Item icons use item IDs; absent images otherwise resolve to Essentials' `000`.

Maps reference assets and own placement/collision. Static prop images and anchors
belong to the asset owner; interaction and animation remain in Ruby. A painted
object does not automatically block movement. Map-embedded artwork such as the
lantern beacon reads approved source pixels when assembling its tileset.

For world props, `assets/props.json` assigns a picture and pixel anchor (the point
placed at an event's screen coordinates), plus an optional fixed `z` layer.
Anchors may lie outside the image. Map events can select an `asset` explicitly;
never infer placement from filename prefixes or a special event coordinate.
Static props share `presentation/props.rb`; flickering lamps and quest props retain
their behavior owners. `load_prop` replaces and disposes an independently loaded
bitmap; do not pass it a shared/cache-owned image. Household pie/plate states are
separate images, while the pearl glint remains a small dynamic effect.
