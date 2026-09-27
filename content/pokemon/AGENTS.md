# Species, forms, items and encounters

Each `<ENGINE_ID>/species.json` owns `species`, optional `metrics`, and `art`.
Compilers discover these bundles; there is no registration list. Source images
live in the same folder. Naming/ownership: [architecture](../../docs/architecture.md#authored-content).

## Add a species or regional form

1. Copy a nearby bundle and edit `species.json`. `species` and `metrics` each
   contain `inherit` (a native template ID) and `fields` (Essentials PBS properties).
   The compiler chooses PBS filenames. Metrics alter placement; do not offset the
   PNG and metric blindly together. Editor metric changes are overwritten.
2. Use `SPECIES` for a base species and `SPECIES_1` for form 1, never `SPECIES_0`.
   PBS uses `[SPECIES,1]`; runtime objects keep base `species` plus integer `form`.
3. Treat native inheritance and PBS defaults as separate mechanisms. Python copies
   a complete template; base-species PBS does not inherit from that template.
   Explicitly define the intended properties of a new species and verify them
   with the native Essentials compiler. Omitting a property is not proof that
   both representations agree. Empty arrays are omitted by the current PBS writer;
   they are not a general way to clear an inherited form field.
4. Evolution targets use the base species ID (`ARBOK`, not `ARBOK_1`). The compiler
   derives backlinks for custom targets. `DefaultForm_0` on a distinct evolved
   species deliberately normalizes form on species change; regional-to-regional
   evolution may retain form 1. Verify the actual evolved object's form, moves and
   identity, not only the declaration. See existing evolution tests before adding
   runtime hooks to compensate for a data definition.
5. Add `front.png`, `back.png`, `icon.png`. Current battle canvases are 160×160;
   preserve approved pixels. Icons are horizontal square-frame strips (currently
   128×64), never vertical strips. `art.cry` names a stock cry or this bundle's ID
   with local `cry.ogg`. `art.stock` explicitly reuses stock sprites; omit local
   PNGs in that case. `art.shiny: true` requires matching `front_shiny.png` and
   `back_shiny.png` (or their stock variants); otherwise normal art is reused.
   Party icons share normal/shiny pixels. Optional `art.palette` maps frame names
   (`Front`, `Back`, `Icons`) to `[[source_rgb, target_rgb], ...]` replacements.
   Missing expected colours fail export. Preview all frames, then inspect battle
   and party composition; form fallback can hide missing assets.
6. Format, `uv run rebuild`, stage additions, then `uv run check --all`.
   Native verification derives its roster from the catalog and compares all native
   species/metric attributes except PBS source bookkeeping and non-evolving family
   backlinks. It checks exact front/back/shiny/icon/cry resolution. Cry exports and native expectations share the asset catalog; normal/shiny party
   icons share the declared normal icon path. New species require their own assets by default.
   Run the native species scenario when altering definitions/compiler behavior.

## Data, form and encounter contracts

- `BaseStats` uses PBS order: **HP, Attack, Defense, Speed, Special Attack,
  Special Defense**. It differs from the common display order with Speed last.
  Python Height/Weight values are metres/kilograms; the compiler writes native
  tenths. Do not pre-multiply by ten or change the stat order when copying a design.

- `pokemon.form = n` clears cached ability, runs form hooks, recalculates stats and
  registers in the Pokédex. It **does not reset moves**. For a newly generated wild
  whose form has a different learnset, set form then `reset_moves`. Never reset
  an owned Pokémon's moves merely because it enters another map.
- `form_simple=` skips form hooks, ability invalidation and Pokédex registration.
  Even reading `form` can invoke `MultipleForms.getForm` and change state outside
  battle/storage; use `form_simple` when inspecting the stored form deliberately.
- `Pokemon.new` alone does not trigger `:on_wild_pokemon_created`; the wild-generation
  path does. A prepared Pokémon passed to battle may therefore bypass regional
  selection. Set intended form/learnset on scripted individuals explicitly.
- Encounter tables belong to `content/maps/<map>/map.json::encounters`:
  `"Land": {"chance": 18, "slots": [[100, "SUNKERN_1", 4, 6]]}`.
  Rows are weight, engine species/form ID, minimum and maximum level. The compiler
  emits PBS/native data and the regional-form table consumed by one engine hook.
  `wild_forms` declares additional scripted-wild defaults, e.g. `{"ARBOK": 1}`.
  Conflicting forms for one base species on the same map are rejected; special
  context-dependent mechanics need their own explicit feature. Terrain activation
  still belongs to the map/feature; a table alone does not create encounter tiles.
- The full pipeline compiles species before encounter rosters. Keep this order:
  encounter validation must see newly added species in the same build.

[Inspected Essentials methods](../../docs/essentials-contracts.md).
Full rebuild writes directly in dependency order. If it fails, fix the cause and
rerun before playing; it does not roll back generated files. `check --all` verifies
regeneration in a disposable copy. Review generated diffs before committing.

`game/.generated/content.json` records custom records and files. Full rebuild removes
retired records/files, so deleting a declaration retires its output without
touching stock inputs. Never hand-edit the inventory to claim a stock ID. Published
species/items may still exist in player saves: retire them only as an explicit
content decision. The manifest is written before generation so failed builds can
be fixed and rerun; it is not a save schema or migration system.
