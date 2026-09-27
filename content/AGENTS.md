# Authored content

Read [structure and naming](../docs/architecture.md#authored-content) for ownership
and native path conventions. Pokémon: [pokemon/AGENTS.md](pokemon/AGENTS.md).
Maps: [maps/AGENTS.md](maps/AGENTS.md). Sound: [audio/AGENTS.md](audio/AGENTS.md).
Edit approved sources here; preview using the shared
[asset workflow](../docs/development.md#asset-previews). Stage sources and generated
outputs before `uv run check --all`. Pipeline changes use the
[exporter guide](../tools/tidebound_dev/art/AGENTS.md).

## Actors, trainers and items

Actors use `actors/<name>/character.png`. XP sheets have **four columns × four
rows**, down/left/right/up; inspect all directions and feet alignment in the engine.
Pokémon party strips and trainer portraits are not walking sheets.

Items use `items/<ID>/item.json` (`name`, `description`) plus `icon.png`, or an
explicit `stock_icon` engine ID. These are story Key Items; other item behavior
requires extending the compiler. Trainers use `trainers/<ID>/trainer.json` (`name`)
with `portrait.png` and `character.png`, or `stock` for an existing trainer type.
Stock trainer reuse supplies the native template as well as artwork; a trainer
with local artwork uses the YOUNGSTER native template.
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
Tile artwork lives in fixed `tilesets/<name>/image.png` sheets.
Shared UI and effect images use `ui/` and `effects/`.

Tile IDs, collision and aligned light masks follow the [map guide](maps/AGENTS.md).
Keep concepts and working files in root `references/`, and external attribution
in [credits](../docs/credits.md).
