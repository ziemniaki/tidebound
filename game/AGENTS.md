# Engine project and generated outputs

`Game.rxproj` opens the RPG Maker XP project. Preserve its stock inputs and
directly maintained assets alongside generated outputs; never clear this directory.

| Editing | Source to change first |
| --- | --- |
| `Data/Scripts.rxdata` | `src/`, load manifest and explicit `tools/tidebound_dev/scripts/patches.py` patches |
| Authored native maps and custom tilesets | [Authored maps/tilesets](../content/maps/AGENTS.md) |
| Tidebound species/forms/items/encounter PBS and `.dat` | [Content definitions](../content/pokemon/AGENTS.md) |
| Custom Pokémon, character, trainer, item and picture PNGs | [Asset ownership/export guide](../content/AGENTS.md) |
| Sound files | [Audio workflow](../content/audio/AGENTS.md) |

- Preserve supplied editor edits: follow the [import workflow](../docs/development.md#rpg-maker)
  before rebuilding. It also covers editor setup and Test Play's save namespace.
- Fix generated content at its source, then rebuild through `uv run play` or
  `uv run build --compile-only`. Extend the owning compiler when needed;
  direct output patches disappear on the next build. New PBS fields need native
  compiler validation. `game/.generated/assets.json` identifies owned asset exports.
- Never delete stock data/art on text-search evidence alone; Essentials resolves
  filenames dynamically. Ignored `tests/engine_reference/` is for inspection only.
- Use `uv run play` for development playtesting. Keep extracted EXE/DLL files ignored.
