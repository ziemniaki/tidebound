# Gameplay and Essentials integration

Files in `tidebound/` are embedded before Essentials' Main in `load_order.txt`
order. Edit the manifest when adding a file; dependencies must already be loaded
when constants, inheritance or hook registration are evaluated. `generated/` is
written by Python compilers. No second copy in `game/Plugins/Tidebound`.

Feature layout and actor rules: [features/AGENTS.md](tidebound/features/AGENTS.md).

## Add a quest or interaction

1. Put the state transition and dialogue in its feature module. Use
   `Tidebound.story` for persistent quest state; keep new feature state under a
   feature-specific key. Read the existing owner's state rather than maintaining
   another copy. `features/interactions.rb` owns shared mother/seller dispatch.
2. Put the short event call in the Python map builder; read the
   [map workflow](../tools/tidebound_dev/maps/AGENTS.md). A new Ruby method alone
   does not connect it to a map. Do not override another feature's method to
   change an interaction's priority.
3. Use `Scenes.run(*events, restore_positions: true) { ... }` for temporary actor
   staging. It owns collision during the scene and restores presentation/camera
   in `ensure`; inventory and quest progress remain your responsibility. Omit
   `restore_positions` when the movement should persist. Never use a quest's
   global busy flag to suppress another feature's actor updates.
   Use `World.travel`, `World.actor` and `Encounters` at engine boundaries. Check
   their actual return values. New shared operations belong in `world/` or
   `engine/`, not in an unrelated story chapter.
4. Format, rebuild, then `uv run check`. Map-event edits also require full rebuild
   and `check --all`. Add the relevant branch to a production-composition scenario;
   play the interaction, interruption/retry and map re-entry when applicable.

## Engine contracts that are easy to miss

- `EventHandlers.add(event, key, proc)` keeps the **first** callback for a duplicate
  key in v21.1. A second registration silently does nothing. Use a unique
  `:tidebound_<feature>_<purpose>` key and inspect the trigger's arguments.
  `HandlerHash` uses different replacement semantics; do not generalize between them.
- `pbMoveRoute` schedules a route and ignores `waitComplete`. It adds THROUGH_ON
  and THROUGH_OFF. Use `World.animate` when subsequent dialogue/state depends on
  completion; it waits while updating the scene and restores the prior `through`.
  Use `pbWait(seconds)` for elapsed time; `sleep` stalls the game loop.
- Erasing an autorun event is not a persistent quest completion flag. Guard its
  effects in saved state before it can run again after map reconstruction. Event
  pages are evaluated **last to first**; refresh/page changes can reset movement
  and collision properties.
- Battles: use `Encounters.able?` before starting an interaction and the Tidebound
  battle adapters. Core outcomes are integers: 0 aborted, 1 won, 2 lost, 3 fled,
  4 caught, 5 draw. Ruby treats all of them as truthy. Only `== 1` advances trainer
  victory. `Encounters.fight` and `Encounters.trainer` handle `:astral` transfers.
  Trainer definitions use named type/name/loss/team fields. Stop the living scene
  after transfer; only victory grants quest progress. `features/astral.rb` owns
  recurring guide/recovery/return interactions.
- Essentials heals loss/draw parties during `after_battle` when `canLose` is set.
  Tidebound snapshots **before** that cleanup. Moving recovery to `on_end_battle`
  loses the pre-heal state. Spirit capture restores the original companion;
  constructing a replacement loses identity, owner, moves and held-item state.
- Keep `TideboundSaveState` and its SaveData registration in `engine/battles.rb`.
  `reset_on_new_game` matters for a second new game in the same process. Use normal
  Essentials serialization; no new save schema/version mechanism.
- Pokémon form setters and learnsets have separate side effects; read the
  [content guide](../tools/tidebound_dev/content/AGENTS.md) before changing forms.
- Rendered visibility does not establish collision. Features declare availability;
  `world/actors.rb` applies it without knowing quest state. It indexes collision actors once, skips forced
  routes, and applies NPC resting visibility only on map entry or explicit
  `Actors.refresh` scene boundaries. Per-frame sync must not hide a cutscene actor. Generated actor roles select policy independently of display
  labels. `World.actor` resolves a registered identity only on its owning map;
  don't scan event names or assume an actor exists after a transfer.
- `Presentation::OwnedSprite` disposes its bitmap and only an explicitly owned
  viewport. Use it for independently loaded/allocated bitmaps, never borrowed/cache-backed
  images. Static props use approved pictures and anchors in `assets/props.json`;
  add an asset record and a `prop` event instead of another drawing class. Essentials Pokémon sprite classes own their `AnimatedBitmap` lifecycle;
  reuse `Presentation::Position` without giving a second owner the same bitmap.

Evidence and upstream methods: [Essentials contracts](../docs/essentials-contracts.md).
The harness uses Ruby 3.2 WASM, but shipped players use Ruby 3.1: passing headless
checks does not authorize newer syntax/APIs or prove rendered behavior.
