# Feature ownership

A feature with several concerns gets one folder: `quest.rb` (state/transitions),
`actors.rb` (availability), `presentation.rb` when needed. See `neighbor/` and
`vault/`; small independent features can remain one file. Follow
[gameplay integration](../../AGENTS.md) for load order, event wiring and checks.

- Register named NPC rules with `Actors.on_entry(:actor_key) { |event, actor| ... }`;
  register changing role collision with `Actors.on_frame("role") { ... }`.
  Return visibility; do not mutate story or start dialogue in a predicate.
  Unknown/duplicate registrations fail on load. The core in `world/actors.rb`
  must not import quest names, story keys or feature-specific busy flags.
- `Scenes.run(*events, restore_positions: true)` gives temporary staging exclusive
  control over those actors. It restores position/direction when requested and
  always restores collision, opacity, speed and camera ownership on exit/error.
  Keep temporary visual flags in the feature's own `ensure`. Story transitions,
  item delivery and failure/retry rules remain explicit in the quest.
  The scene owner pairs setup with cleanup; callers invoke its action (`play`,
  for example), without resetting its presentation state in their own `ensure`.
- Shared-NPC interaction priority lives in `features/interactions.rb`; do not
  register competing callbacks or prepend one feature into another.
- Test through the composed gameplay harness, including interruption/retry for a
  changed scene. Headless movement doubles cannot prove native route behavior.

For reproducible starting states, follow the shared
[playtest workflow](../../../docs/development.md#playtest-scenarios).
