# Working on Tidebound

Continue the existing Pokémon Essentials 21.1 game. The creative director is
not a developer and often works through agents. Handle setup, rebuilding and
verification yourself; deliver a playable result and a short explanation.

## Start here

1. Inspect `git status`; preserve existing work. Use a focused branch in
   `ziemniaki/tidebound`, not a fork or an old release ZIP.
2. Read [current status](docs/status.md) and relevant sections of
   [architecture](docs/architecture.md). [Development](docs/development.md)
   explains commands; [testing](docs/testing.md) describes deeper checks.
3. For narrative, art or mechanics decisions, consult
   [specs/game-design.md](specs/game-design.md). Confirmed decisions govern;
   proposals, working names and intentionally unresolved mysteries are not canon.
4. Update current documentation in place. Keep this file short. Git history
   preserves retired code and instructions; do not restore them as active guidance.

## Everyday commands

Run from the checkout with [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv run doctor          # inspect prerequisites
uv run play            # embed Ruby, build a native dev copy, launch it
uv run build           # build without launching
uv run check           # tests and map/source agreement; no game regeneration
uv run rebuild         # embed src/load_order.txt sources in game/Data/Scripts.rxdata
uv run rebuild --all   # intentionally regenerate maps, data, art and scripts
uv run check --all     # also compare regeneration in a disposable copy
```

uv manages Python and locked dependencies. Checks need the exact Node version
in `.node-version`; `check` installs locked test packages automatically.
Mac packaging needs Xcode command-line tools. Development players use
`Tidebound_Development` saves; releases retain `Tidebound_Opening_0_2`.
Build outputs and restored binaries are ignored. Never commit saves or caches.

## Edit the source of truth

| Change | Authoritative files |
| --- | --- |
| Game vision, canon, unresolved design | `specs/game-design.md` |
| Custom Ruby, dialogue, state and presentation | `src/tidebound/`; embedding order in `src/load_order.txt` |
| Generated map layouts/events | `tools/rebuild_maps.py` and its map modules |
| Generated species/items/encounters | `tools/rebuild_*_data.py`; then `game/PBS` and `game/Data` outputs |
| Source artwork and export recipes | `assets/<species>/`; exports in `game/Graphics/` |
| Engine project and required game data | `game/`; `game/Game.rxproj` opens in RPG Maker XP |
| Runtime inputs and patches | `runtime/`, pinned by `release.json` |
| Tooling and workflow | `tools/`, `tests/`, `.github/workflows/`, `docs/` |

Ruby is embedded once in `src/load_order.txt` order, immediately before Essentials' Main.
Register every new Ruby file in that manifest. Generated Ruby belongs in
`src/generated/`; generators must never rewrite handwritten source.
Never install a second copy in `Plugins/Tidebound`. Ignored engine reference
extractions under `tests/engine_reference/` are inspection copies, not source.

Maps 101–116 are generated. Rebuilding overwrites direct RPG Maker edits.
Preserve supplied editor changes and reconcile the generator before running
`rebuild --all`. Never delete `game/Data` as disposable output: stock engine
scripts/data remain required inputs. `tools/generated/` contains reports and
masks, not map-authoring sources.

## Preserve the game

- Preserve current Pokémon objects, identities, held items and quest state. An
  empty party can mean an unresolved astral journey. The refactoring explicitly
  permits dropping historic save compatibility: use one supported-version boundary,
  not feature-local migration chains. Never delete player save files or reset
  current saves to hide errors.
- Preserve `TideboundSaveState`, the release save namespace and
  `fontHeightReporting: 1`. Battle losses snapshot companions before Essentials
  heals them. Only won trainer battles advance victory flags.
- Ordinary locations are perpetual night. Early scenes retain familiar Gen 3
  readability; do not reveal later lore or resolve open mysteries accidentally.
- Repository maintenance does not authorize an engine or gameplay rewrite.

## Finish a change

Run `uv run check`; use `uv run check --all` for generator/layout changes and
relevant native checks for packaging or integration. Review generated diffs.
Distinguish automated evidence from actual playthroughs. Keep
[docs/status.md](docs/status.md) current without appending a diary.

PR pushes run quick checks. Full platform builds use `/verify` and must match
the reviewed head. Workflow/layout migrations also need a full run dispatched
on the branch to exercise the new definitions; see [releasing](docs/releasing.md).
Do not merge or publish merely because a local test passed.

Release metadata lives in `release.json`; notes in `docs/release-notes.md`.
Published tags/assets are immutable. Releases contain exactly three player ZIPs
(Mac universal, Windows x64, Linux x86_64). Keep technical artifacts in CI. Notes
are one concise flat list: no download instructions, README-first directions,
platform-selection section, agent chatter or generic filler.

Mac tests cover Downloads, long Unicode paths and actual read-only App
Translocation on both architectures. Only disposable fixtures receive approved
quarantine attributes; never alter global security settings or ship test flags.
