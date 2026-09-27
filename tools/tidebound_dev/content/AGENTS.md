# Species, forms, items and encounters

`species.py` combines family `SPECIES` and `METRICS` catalogs.
`species_compiler.py` writes both native `.dat` and PBS. Generated PBS is not the
source of truth. Species PNGs follow the [asset workflow](../../../assets/AGENTS.md).

## Add a species or regional form

1. Add a record to the relevant family module (`plants`, `insects`, `coastal`), or
   add a cohesive family module and include it in `species.py`. Catalog merges
   reject duplicate IDs across modules.
2. Use `SPECIES` for a new base species and `SPECIES_1` for form 1 in Python keys.
   PBS uses `[SPECIES]` / `[SPECIES,1]`; runtime objects retain base `species` plus
   `form`. `inherit` selects the native template, `file` the generated PBS stem,
   `fields` the supported PBS properties. `native_field` rejects unknown fields.
3. Treat native inheritance and PBS defaults as separate mechanisms. Python copies
   a complete template; base-species PBS does not inherit from that template.
   Explicitly define the intended properties of a new species and verify them
   with the native Essentials compiler. Omitting a property is not proof that
   both representations agree. Empty tuples are omitted by the current PBS writer;
   they are not a general way to clear an inherited form field.
4. Evolution targets use the base species ID (`ARBOK`, not `ARBOK_1`). The compiler
   derives backlinks for custom targets. `DefaultForm_0` on a distinct evolved
   species deliberately normalizes form on species change; regional-to-regional
   evolution may retain form 1. Verify the actual evolved object's form, moves and
   identity, not only the declaration. See existing evolution tests before adding
   runtime hooks to compensate for a data definition.
5. Add metrics and approved front/back/icon/shiny assets as needed. Declare cry and shiny reuse once in `art/pokemon.py::POKEMON`. Form artwork/cry fallback can hide missing files.
6. Format, `uv run rebuild --all`, stage additions, then `uv run check --all`.
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
- Encounter tables belong to `maps/areas/<map>/map.json::encounters`:
  `"Land": {"chance": 18, "slots": [[100, "SUNKERN_1", 4, 6]]}`.
  Rows are weight, engine species/form ID, minimum and maximum level. The compiler
  emits PBS/native data and the regional-form table consumed by one engine hook.
  `wild_forms` declares additional scripted-wild defaults, e.g. `{"ARBOK": 1}`.
  Conflicting forms for one base species on the same map are rejected; special
  context-dependent mechanics need their own explicit feature. Terrain activation
  still belongs to the map/feature; a table alone does not create encounter tiles.
- The full pipeline compiles species before encounter rosters. Keep this order:
  encounter validation must see newly added species in the same build.

Items/quest rewards use `story.py` for PBS/native data. Item and trainer images
belong to `assets/` or explicit stock aliases in `art/files.py`, never this compiler.
A successful item definition does not guarantee a reward fits: `$bag.add` can
return false. Advance reward state only after successful delivery, as existing
quest flows do. Test a full bag when adding a one-time reward.

[Inspected Essentials methods](../../../docs/essentials-contracts.md).
Full rebuild writes directly in dependency order. If it fails, fix the cause and
rerun before playing; it does not roll back generated files. `check --all` verifies
regeneration in a disposable copy. Review generated diffs before committing.

`tools/generated/content.json` records custom records and files. Full rebuild removes
those records before compiling, so deleting a declaration retires its output without
touching stock inputs. Never hand-edit the inventory to claim a stock ID. Published
species/items may still exist in player saves: retire them only as an explicit
content decision. The manifest is written before generation so failed builds can
be fixed and rerun; it is not a save schema or migration system.
