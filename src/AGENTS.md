# Gameplay and Essentials integration

`load_order.txt` embeds `tidebound/` before Essentials' Main. Register every new
file, with dependencies before constants, inheritance and hook registration that
use them. Python owns `generated/`; never install a second `game/Plugins/Tidebound` copy.

Feature layout and actor rules: [features/AGENTS.md](tidebound/features/AGENTS.md).

## Add a quest or interaction

1. Keep transitions and dialogue in their feature; persist state under its key in
   `Tidebound.story`. Read another owner's state instead of copying it.
   `features/interactions.rb` owns shared mother/seller dispatch and priority.
2. Wire a short entry-point call into the authored event using the
   [map workflow](../content/maps/AGENTS.md). A Ruby method alone is not playable.
3. Use `Scenes.run(*events, restore_positions: true) { ... }` for temporary actor
   staging. It owns collision during the scene and restores presentation/camera
   in `ensure`; inventory and quest progress remain your responsibility. Omit
   `restore_positions` when the movement should persist. Never use a quest's
   global busy flag to suppress another feature's actor updates.
   Use `World.travel`, `World.actor` and `Encounters` at engine boundaries;
   check their return values. Shared operations belong in `world/` or `engine/`.
4. Format, run `uv run build --compile-only`, then `uv run check`. Map-event edits
   also need `check --all`. Add the relevant branch to a production-composition scenario;
   play the interaction, interruption/retry and map re-entry when applicable.

## Engine contracts

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
  [content guide](../content/pokemon/AGENTS.md) before changing forms.
- Visibility does not establish collision. Features declare availability;
  `world/actors.rb` applies it without quest knowledge. It indexes collision actors
  once, skips forced routes and sets resting visibility on entry or `Actors.refresh`.
  Per-frame sync must not hide cutscene actors. Generated roles select policy,
  not display labels. `World.actor` resolves identity only on its owning map;
  never scan names or assume an actor exists after transfer.
- `Presentation::OwnedSprite` disposes its bitmap and only an explicitly owned
  viewport; never give it borrowed/cached images. Static props use
  `content/props/<name>/prop.json` and a `prop` event, not another drawing class.
  Essentials Pokémon sprites own their `AnimatedBitmap`; reuse
  `Presentation::Position` without adding a second bitmap owner.

Evidence and upstream methods: [Essentials contracts](../docs/essentials-contracts.md).
The harness uses Ruby 3.2 WASM, but shipped players use Ruby 3.1: passing headless
checks does not authorize newer syntax/APIs or prove rendered behavior.
