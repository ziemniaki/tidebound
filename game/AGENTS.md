# Engine project and generated outputs

`Game.rxproj` is the RPG Maker XP editor project. This directory combines stock
engine inputs, generated Tidebound outputs and directly maintained assets.
It is not a disposable build directory.

| Editing | Source to change first |
| --- | --- |
| `Data/Scripts.rxdata` | `src/`, load manifest and explicit `tools/tidebound_dev/scripts/patches.py` patches |
| `Data/Map101.rxdata` … `Map116.rxdata`, custom tilesets | [Map builders](../tools/tidebound_dev/maps/AGENTS.md) |
| Tidebound species/forms/items/encounter PBS and `.dat` | [Content definitions](../tools/tidebound_dev/content/AGENTS.md) |
| Pokémon PNGs | [Asset ownership/export guide](../assets/AGENTS.md) |
| Sound files | [Audio workflow](../tools/tidebound_dev/art/AGENTS.md) |

Do not edit ignored `tests/engine_reference/`: it is an inspection copy.
Do not delete stock data or seemingly unused art based on text searches; Essentials
resolves many filenames dynamically. Manual editor changes to generated maps must
be brought back into their builders before regeneration. Preserve supplied edits.

`uv run play` refreshes custom assets and Ruby. It preserves compiled content and
map geometry. Edit approved sources in `assets/`, not their exported PNG/OGG files. Full rebuild publishes both authored PBS and native databases for supported
content; arbitrary new PBS fields require native compiler validation.

RPG Maker Test Play uses the project save namespace. Use `uv run play` for the
separate development namespace. Restored EXE/DLL helpers are ignored; use
`uv run editor` on Windows instead of committing local binaries.
