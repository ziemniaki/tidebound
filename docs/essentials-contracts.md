# Essentials integration evidence

The workflow guides are checked against the **embedded Essentials 21.1 engine**
in `game/Data/Scripts.rxdata` at Tidebound commit
`b55a75e87f0f23de0e4257556dd7add2378cd365` (0.8.7). Checked 2026-09-27.
The links below pin upstream v21.1; Tidebound's embedded patches take precedence.
Do not replace our engine with upstream master to match an example.

## Inspect the code actually shipped

```sh
uv run python tests/prepare_reference.py
rg -n 'def pbMoveRoute|def form=|def self.check_graphic_file' tests/engine_reference
```

`tests/engine_reference/index.json` maps original section names to extraction files.
Numeric prefixes are archive positions, not stable APIs. The extraction is ignored
and disposable. Source changes belong in `src/` or explicit patches in
`tools/tidebound_dev/scripts/patches.py`; keep inspected engine snippets out of the
custom load manifest.

| Contract | Embedded section / methods | Versioned upstream source |
| --- | --- | --- |
| Sprite/cry fallback | `Species_files` — `check_graphic_file, check_cry_file` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/010_Data/002_PBS%20data/009_Species_files.rb) |
| Icon frame layout | `Pokemon_Sprites` — `PokemonSpeciesIconSprite#refresh, #changeOrigin` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/014_Pokemon/001_Pokemon-related/003_Pokemon_Sprites.rb) |
| Form side effects | `Pokemon` — `form=, form_simple=, reset_moves, species=` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/014_Pokemon/001_Pokemon.rb) |
| Movement scheduling | `Overworld` — `pbMoveRoute, pbWait` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/012_Overworld/001_Overworld.rb) |
| Page priority and refresh | `Game_Event` — `refresh, erase, should_update?` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/004_Game%20classes/007_Game_Event.rb) |
| Handler key semantics | `Event_Handlers` — `NamedEvent#add, HandlerHash#add` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/003_Game%20processing/005_Event_Handlers.rb) |
| Callback arguments | `Event_HandlerCollections` — `EventHandlers and event descriptions` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/003_Game%20processing/006_Event_HandlerCollections.rb) |
| Audio path/fade wrappers | `Audio_Play` — `pbBGMPlay, pbSEPlay, pbBGMStop` | [v21.1](https://github.com/Maruno17/pokemon-essentials/blob/v21.1/Data/Scripts/008_Audio/002_Audio_Play.rb) |

Additional contracts verified in the embedded sections:

- `Overworld_BattleStarting`: `start_core` returns integer outcomes; `start`
  wrappers have different Boolean contracts. `after_battle` heals a loss/draw
  with `canLose` **before** firing `on_end_battle`.
- `Overworld_WildEncounters`: `pbGenerateWildPokemon` fires
  `on_wild_pokemon_created`; constructing a `Pokemon` directly does not.
- `SaveData_Value`: `ensure_class` takes a Symbol and validates with
  `Object.const_get`; passing the Class itself is not its API. Keep the existing
  TideboundSaveState registration. `reset_on_new_game` controls reinitialization.
- `Game_System`: `bgm_play_internal2` and `se_play` apply player volume preferences.
- `Interpreter_Commands`: `command_355` joins following 355/655 commands, then
  executes the combined script; use the map helpers to serialize it.

## Documentation cross-checks

The [Essentials map metadata documentation](https://essentialsengine.miraheze.org/wiki/Map_metadata)
distinguishes map metadata from the RPG Maker map itself. `Outdoor` affects
engine behavior, and `HealingSpot` is a Teleport destination, not a blackout
checkpoint. Tidebound uses its own checkpoint in the battle adapter.

[Species definitions](https://essentialsdocs.fandom.com/wiki/Defining_a_species)
and [forms](https://essentialsdocs.fandom.com/wiki/Forms) are the old wiki's indexed
pages, which link to the current wiki. Their form inheritance/asset naming claims
were checked against our resolver/compiler code. Direct requests to several current
wiki pages returned 403 during this audit; those pages were not treated as inspected
content. The embedded source is the authority for the precise contracts above.

[mkxp-z's README](https://github.com/mkxp-z/mkxp-z#what-doesnt-work) explicitly
excludes WMA. Audio playback still needs a native listening check: a successful
load or encoder exit does not establish a seamless loop or a suitable mix.
