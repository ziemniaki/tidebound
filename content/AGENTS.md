# Authored content

Edit approved sources here using [structure and naming](../docs/architecture.md#authored-content).
Follow the scoped guides for [Pokémon](pokemon/AGENTS.md), [maps](maps/AGENTS.md)
and [sound](audio/AGENTS.md). New content should fit the existing bundle/export
workflow; extend its [owner](../tools/tidebound_dev/art/AGENTS.md) if needed.
Use the shared [asset preview](../docs/development.md#asset-previews), then stage
source changes before `uv run check --all`.

## Actors, trainers and items

Actors use `actors/<name>/character.png`. XP sheets have **four columns × four
rows**, down/left/right/up; inspect all directions and feet alignment in the engine.
Pokémon party strips and trainer portraits are not walking sheets.

Items use `items/<ID>/item.json` (`name`, `description`) with `icon.png` or a
`stock_icon` engine ID. These are story Key Items; extend the compiler for other
behavior. Trainers use `trainers/<ID>/trainer.json` (`name`) with `portrait.png`
and `character.png`, or `stock` to reuse a native trainer template and artwork.
Local trainer artwork uses the YOUNGSTER template.
Battle rosters and reward delivery belong to the Ruby feature. `$bag.add` can fail:
advance a one-time reward only after successful delivery. Missing item/trainer
art can silently fall back to `000`; preview checks exact engine resolution.

## Props and lighting

A prop bundle has `image.png` and `prop.json`: `{"anchor": [16, 32]}`.
The integer anchor is placed at the event and may lie outside the image. Optional
integer `z` fixes the layer. To reuse another prop's pixels, use `"image": "dock_boat"`
and omit the local PNG; reuse must point directly to a bundle owning its image.
Map events declare `{"role": "prop", "asset": "dock_boat"}` in their map's
`actor_settings`; compile with `uv run build --compile-only`.
An image does not set collision, and filenames do not select gameplay behavior.

Static props share `presentation/props.rb`; flicker and quest transitions stay
with their feature. `load_prop` owns/disposes its bitmap; never pass it cached art.
Tile sheets (`tilesets/<name>/image.png`), IDs, collision and light masks follow
the [map guide](maps/AGENTS.md). Shared UI/effect images use `ui/` and `effects/`.
Keep concepts and working files in root `references/`, and external attribution
in [credits](../docs/credits.md).
