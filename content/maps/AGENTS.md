# Map authoring

`map.json` owns the map ID, display name, named entrances, encounters, atmosphere,
actor identities/roles and retired event IDs. `layout.json` owns the complete RPG
Maker map: dimensions, tile layers, audio, events, pages and movement routes.
Both are authored data. Builds serialize them; they never execute map builders.
The [editor workflow](../../docs/development.md#rpg-maker) is shared by humans and agents.

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
  `asset`, `state`, `index` or `cue`. A named `key` is the actor identity, independent of the event's display name. Every declared actor must reference an existing event. Follow [src/AGENTS.md](../../src/AGENTS.md) for feature behavior.
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

Create a lower_snake_case bundle with `map.json` and `layout.json`; copying a small
existing room preserves native defaults. Use a new map ID unless deliberately
adopting an existing native map; source declarations own those IDs on rebuild.
Declare entrances and actor settings only when needed. Alternatively create a map
in RPG Maker and import it using the linked editor workflow; no scaffold is needed.
Procedural tools may write these same files as a one-time authoring operation.
Their output is ordinary editable content; generators are never a build dependency.

Run `uv run play` to compile and play; `uv run build --compile-only` exports without
launching. Inspect `.build/maps/map_<id>_preview.png`, then verify entrances,
interactions and collision in the player. Stage sources/exports and run
`uv run check --all`. Previews do not establish event scheduling or gameplay.
The compiler updates Essentials' native map revision so saves reload changed maps
without rewriting Pokémon or quest state.
