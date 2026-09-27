# Engine project and generated outputs

`Game.rxproj` is the RPG Maker XP editor project. This directory combines stock
engine inputs, generated Tidebound outputs and directly maintained assets.
It is not a disposable build directory.

| Editing | Source to change first |
| --- | --- |
| `Data/Scripts.rxdata` | `src/`, load manifest and explicit `tools/tidebound_dev/scripts/patches.py` patches |
| Authored native maps and custom tilesets | [Authored maps/tilesets](../content/maps/AGENTS.md) |
| Tidebound species/forms/items/encounter PBS and `.dat` | [Content definitions](../content/pokemon/AGENTS.md) |
| Custom Pokémon, character, trainer, item and picture PNGs | [Asset ownership/export guide](../content/AGENTS.md) |
| Sound files | [Audio workflow](../content/audio/AGENTS.md) |

Do not edit ignored `tests/engine_reference/`: it is an inspection copy.
Do not delete stock data or seemingly unused art based on text searches; Essentials
resolves many filenames dynamically. Use the [RPG Maker workflow](../docs/development.md#rpg-maker) to import saved map
edits into authored content before rebuilding. Preserve supplied edits.

`uv run play` compiles all authored content, including maps. Edit approved sources in `content/`, not exported PNG/OGG files;
`game/.generated/assets.json` identifies owned exports. The same rebuild writes
fixed tilesets, lighting, authored PBS and native data;
arbitrary new PBS fields require native compiler validation.

RPG Maker Test Play uses the project save namespace. Use `uv run play` for the
separate development namespace. Restored EXE/DLL helpers are ignored; use
`uv run editor` on Windows instead of committing local binaries.
