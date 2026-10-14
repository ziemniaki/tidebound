# Map authoring

`map.json` owns the map ID, display name, named entrances, encounters, atmosphere,
actor identities/roles, lighting and retired event IDs. `layout.json` owns the complete RPG
Maker map: dimensions, tile layers, audio, events, pages and movement routes.
Builds serialize this authored data; they never execute map builders.
Follow the [editor workflow](../../docs/development.md#rpg-maker) for RPG Maker edits.

## Layout and tiles

- `layout.json::data.shape` is `[width, height, 3]`; `rows` contains every row of
  layer 0, then layer 1, then layer 2. Event dictionary keys are numeric IDs as
  strings; each event's `id` must match its key. `$type` names native RPG classes;
  preserve unfamiliar page/command fields rather than constructing a partial copy.
- `tileset_id` refers to `content/tilesets/<name>/tileset.json::id` or a stock
  tileset. Each custom bundle owns `image.png`, native passage/priority/terrain
  tables and optional `windows.png`. Tile 384 is the first 32px square; sheets
  have eight columns. IDs 48–383 select the seven native autotile slots.
- **Append tiles; do not repack or reorder them.** Their numeric IDs are stable
  references shared by all maps using that sheet. Keep every existing square in
  place when extending a sheet. Native sheets must fit 256 × 16,384 pixels.
  Extend all three metadata tables with new tiles. Changing a tileset's passage
  flags intentionally changes every occurrence of that tile; use another tile
  when only one occurrence should behave differently.
- Collision uses Essentials' native passage, priority and terrain settings.
  There is no runtime map-mask override. Passage low bits block down/left/right/up;
  0 allows all, 15 blocks all. Priority affects drawing **and** which layer stops
  the passage search. Terrain 13 ignores passage; terrain 6 is StillWater/Surf.
  Event `through` and active page settings still affect character collision.
- Furniture's northern caps, upright cupboard tops and potted-plant foliage are
  overhangs: use passage 0 and priority 1, with passable floor and wall trim on
  that cell. Keep the lower body solid. Check all three layers: a blocked floor
  duplicate or trim tile still blocks a passable overhang. Do not mark the entire
  artwork rectangle as the object's footprint, or apply this rule to terrain
  boundaries, building walls and ground-level rubble barriers.
- A relocating or hidden NPC needs ordinary floor underneath. Its active event
  owns character collision; baking its initial position into a blocked floor
  leaves an invisible obstacle after it moves or disappears.
- `windows.png` matches the fixed sheet square-for-square; alpha is light strength.
  Moving a window tile moves its light automatically. Keep masks aligned when
  adding tiles. The compiler writes the packed runtime light sheet.

## Events and gameplay

- Never renumber existing map/event IDs: saved self-switches use those IDs.
  Live IDs belong only to `layout.json::events`. `map.json::retired_event_ids`
  records deleted IDs; import records deletions and rejects reuse. Allocate above
  both the live and retired maxima; RPG Maker may offer a retired ID. For JSON
  deletions, add the removed ID to that list yourself.
- `actor_settings` maps event IDs to runtime roles and optional `key`, `species`,
  `asset`, `state`, `index` or `cue`. `key` identifies an actor independently of its
  display name. Each declaration must reference a live event. Feature behavior
  follows [src/AGENTS.md](../../src/AGENTS.md).
- Roles select consumers in `world/actors.rb`: companions need `species`, spirits
  need `index`, neighbor wildlife needs `state`, props need `asset` from
  `content/props/`. Door cues are `north|south|east|west`. Do not infer roles from labels.
- Use native Transfer Player (command 201) for ordinary doors; direct destinations
  are checked against map bounds/passages. A variable-driven transfer needs a
  gameplay test. Feature-controlled travel uses `World.travel` in Ruby.
- Script events use 355 plus 655 continuations, then command 0. Keep branching
  in Ruby feature entry points. Trigger values: 0 action, 1 player touch, 2 event
  touch, 3 autorun, 4 parallel. Guard and erase one-time autoruns. Pages are selected
  last-to-first; every page can change movement, collision and graphics.
- Named entrances in `map.json` are absolute `[x, y, direction]`. Coast's `origin`
  is only for explicit `World.coast_xy` conversions; native layout positions stay
  absolute. Moving a door destination does not move a named playtest entrance.
- Maze slide/warp geometry derives from event script calls and their positions.
  Stop events contain the native comment `tidebound:slide_stop`; move the event
  with its painted diamond. The entry and Natu event define start/goal. Pond water
  derives from terrain tags; `road/mechanics.json` declares tested reward regions.

## Add or generate a map

Copy a small room into a lower_snake_case bundle to preserve native defaults, or
create a map in RPG Maker and import it. Allocate a new map ID unless deliberately
adopting a native map; declarations own those IDs on rebuild. Add entrances and
actor settings only when needed. Procedural authoring may write these same editable
files; reusable tooling belongs in the existing package, never a map-specific
build generator.

Run `uv run play` to compile and play; `uv run build --compile-only` exports without
launching. Inspect layouts in RPG Maker and verify appearance, entrances,
interactions and collision in the native player. Stage source changes and run
`uv run check --all`; static validation does not establish event scheduling or rendering.
The compiler updates the native map revision so saves reload changed maps.

Local illumination settings and units are documented in [architecture](../../docs/architecture.md#local-lighting-prototype). Declare light blockers separately from movement collision.
