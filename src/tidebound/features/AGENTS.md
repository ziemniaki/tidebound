# Feature ownership

A feature with several concerns gets one folder: `quest.rb` (state/transitions),
`actors.rb` (availability), `presentation.rb` when needed. See `neighbor/` and
`vault/`. Small independent features can remain one file. Add every Ruby file to
`src/load_order.txt`; keep dependencies before consumers.

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
- Shared-NPC interaction priority lives in `features/interactions.rb`; do not
  register competing callbacks or prepend one feature into another.
- Test through the composed gameplay harness, including interruption/retry for a
  changed scene. Headless movement doubles cannot prove native route behavior.
