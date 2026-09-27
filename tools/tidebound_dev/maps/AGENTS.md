# Map and event authoring

These builders own maps 101–116. Each `areas/<map>.py` owns its final layout, events and painting.
`compiler.construct` assembles complete maps and exports shared atlases; `serialization.serialize` writes RPG Maker maps, metadata, masks and
previews. `registry.py` exports map/actor identities and roles to Ruby. Read
[src/AGENTS.md](../../../src/AGENTS.md) for the gameplay side of an event.

## Add a map

1. Add a `MapDefinition` in `definitions.DEFINITIONS` with a distinct map ID,
   symbolic name, arrivals and any non-default music/metadata/atmosphere. Add `areas/<name>.py` with a builder
   returning its complete `Map` and wire it into `compiler.construct`'s returned list. Painters
   share atlases: adding an interior also needs the appropriate `save_atlas` input.
   Pass the supplied `BuildPaths`; do not write into the checkout via a global root.
2. Define entry/exit tiles; arrivals in the map definition drive reachability
   validation. Include a return route and any scripted/conditional arrivals.
3. Set walkability explicitly while drawing. `Map.walk` becomes `MAP_PASSAGES`.
   On these maps, `world/atmosphere.rb::Passages` replaces tile passage checks and
   returns terrain `None`; RPG Maker tileset flags alone will not create grass,
   Surf water or ledges. Fields and Pond supply specific terrain hooks. A new
   mechanic must account for those hooks, not just paint a grass/water tile.
4. `MapDefinition` supplies music, native/PBS metadata and runtime atmosphere.
   Ordinary maps default to the indoor preset. Choose another named preset for
   outdoor/special scenes. `outdoor` is the Essentials metadata flag; `night`
   controls Tidebound's permanent-night policy. They are distinct engine concerns.
5. Format, run `uv run rebuild --all`, stage new source **and** outputs, then
   `uv run check --all`. Inspect `tools/generated/map_<id>_preview.png` and play all
   entrances, exits and interactions. Offline previews approximate rendering;
   collision/terrain hooks and event pages still need native checks. Existing native
   world captures cover a named roster, not every new map automatically.

Static dock props and window-light masks are baked by `scenery.py`; map compilation
exports their PNGs and `src/generated/window_lights.rb`. Keep per-pixel asset work
in the builder; runtime presentation owns only positioning and animation.

## Coordinates, events and actors

- All drawing, event, door and `layers`/`walk` coordinates are absolute tiles.
  Coast layout uses `coast.absolute(x, y)` explicitly for local coordinates; its
  origin `(24, 20)` is defined in `definitions.py` and exported to Ruby.
  `World.coast_xy`/`travel_coast` convert local coast coordinates; `World.local_xy`
  converts event positions back to local coordinates for existing harvest keys.
  Door destinations and `World.travel` coordinates are always absolute.
- Use `Map.door` for ordinary transfers and small public Ruby calls for interactions.
  Script commands use 355 + 655 continuations and a terminating command 0; the
  `script`/`page` helpers produce them. Keep story branching in the Ruby owner.
- The helper's triggers are engine values: 0 action, 1 player touch, 2 event touch,
  3 autorun, 4 parallel. Unconditional autorun can repeatedly seize control; erase
  the current event and guard one-time effects in persistent quest state. A page
  with no charset defaults to `through=True`; an invisible event may need explicit
  collision. `blocks=True` also marks its tile unwalkable in the generated mask.
- Event IDs come from insertion order (`len(events)+1`); self-switch identity is
  `(map_id, event_id, letter)`. Reordering events can attach saved self switches to
  a different actor. Use feature state for new story progression; do not treat
  event IDs as durable names or reintroduce a save migration framework.
- Register a scene actor in `registry.ACTORS` with its key, owning map, readable
  label and role; pass `ACTORS["key"]` to `Map.event`. `World.actor(:key)` uses the
  generated map/event identity and returns nil on another map. Generation rejects
  missing, duplicate and misplaced identities. Labels do not control lookup.
- For anonymous props/companions, give `Map.event` an explicit `role`. Companion
  roles require `species`; spirits require a soul `index`; `neighbor_wild` requires
  the owning quest's `state` key. These select concrete consumers in
  `features/actors.rb`. A name such as `Wild:NATU` alone has no effect.
- Presentation also reads these roles. `demo_prop` requires its picture `asset`;
  door/exit threshold hints use `cue="north|south|east|west"`. Add a role and its
  consumer together; unknown roles and missing required fields fail generation.
  `Map.door` defaults to the south sill. Define actors at their final positions in their owning area. Do not append a
  second pass that finds and rewrites existing events by display label.
- Pass `direction`, `direction_fix` and `through` to `Map.event` when needed;
  keep Marshal page attribute access inside the map model.
- A charset is a four-column/four-row XP sheet, not a Pokémon party icon strip.
  Event pages select from the last matching page; later pages can override earlier
  collision/movement settings. Validation inspects every page. `Map.door` records
  structured destinations and checks bounds before passability. Direct Ruby travel
  calls and native Transfer Player commands in builder pages are rejected; put
  conditional movement in a feature method and test its success/retry/cancel routes.
  Static checks cannot prove Ruby routes: checkpoint returns are exercised in
  `tests/gameplay/opening.rb`, `neighbor.rb` and `hideout.rb`; dream/folded-room
  arrival/retry/return branches are in `tests/gameplay/world.rb`.

[Engine evidence](../../../docs/essentials-contracts.md) describes the inspected
contracts. `Map.targets` derives current event coordinates; painters can relocate
an event without resynchronizing a second position list. `blocking_events` retains
authored collision intent when a painter redraws the floor.
