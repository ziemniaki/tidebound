# Map and event authoring

These builders own maps 101–116. `compiler.construct` composes their areas and
painters; `serialization.serialize` writes RPG Maker maps, metadata, masks and
previews. `registry.py` exports map/actor names to Ruby. Read
[src/AGENTS.md](../../../src/AGENTS.md) for the gameplay side of an event.

## Add a map

1. Reserve a distinct map ID and symbolic name in `registry.MAPS`. Add a builder
   returning `Map` and wire it into `compiler.construct`'s returned list. Decorators
   share atlases: adding an interior also needs the appropriate `save_atlas` input.
   Pass the supplied `BuildPaths`; do not write into the checkout via a global root.
2. Define entry/exit tiles and add the arrival coordinates to `validate.py::spawns`.
   Validation currently indexes that table for every map, so registry + builder
   alone is incomplete. Include a return route and any scripted/conditional arrivals.
3. Set walkability explicitly while drawing. `Map.walk` becomes `MAP_PASSAGES`.
   On these maps, `world/atmosphere.rb::Passages` replaces tile passage checks and
   returns terrain `None`; RPG Maker tileset flags alone will not create grass,
   Surf water or ledges. Fields and Pond supply specific terrain hooks. A new
   mechanic must account for those hooks, not just paint a grass/water tile.
4. Review music (`model.Map.serialize`), native map metadata (`serialization.py`),
   PBS metadata (`content/configure.py`) and runtime tone/fog (`world/atmosphere.rb`).
   They are currently separate owners; indoor classification is a hardcoded list.
   Changing `Outdoor` also affects engine day/night and field mechanics. The
   project's permanent-night policy is not equivalent to merely setting Outdoor.
5. Format, run `uv run rebuild --all`, stage new source **and** outputs, then
   `uv run check --all`. Inspect `tools/generated/map_<id>_preview.png` and play all
   entrances, exits and interactions. Offline previews approximate rendering;
   collision/terrain hooks and event pages still need native checks. Existing native
   world captures cover a named roster, not every new map automatically.

## Coordinates, events and actors

- Coordinates are tiles. Coast authoring methods add `(24, 20)` to local coordinates;
  direct `layers`/`walk` indexing does not. `World.travel_coast` accepts local coast
  coordinates; `World.travel(:coast, ...)` accepts absolute ones. Do not offset twice.
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
- `World.actor(:key)` resolves the registered name **on the current map**, returning
  nil if absent. The registry verifies global existence, not uniqueness or the
  expected map. Check the intended map and avoid duplicate names there.
- Names such as `Wild:`, `Spirit:`, `House:`, `Room:`, `Pookie outside`, `Shop keys`
  and `Crate...` are runtime inputs to actor/presentation logic, not decorative labels.
  Trace consumers in `features/actors.rb` and presentation before renaming/copying.
- A charset is a four-column/four-row XP sheet, not a Pokémon party icon strip.
  Event pages select from the last matching page; later pages can override earlier
  collision/movement settings. The current validator inspects only the first page
  and literal transfer calls; it does not prove all conditional routes are valid.

[Engine evidence](../../../docs/essentials-contracts.md) and
[audit follow-ups](../../../docs/decisions/authoring-audit.md) describe the current
limits. Do not expand every builder into a generic map framework to add one area.
