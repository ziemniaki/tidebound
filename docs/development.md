# Development

The normal loop is **edit → `uv run format` → `uv run play` → `uv run check`**.
Run commands from the checkout; no environment activation or manual runtime
copying is needed.

## Agent-assisted development

Describe the player-visible change and affected area. The agent reads `AGENTS.md`,
implements it on a branch, and builds a development player for you to try with
`uv run play`. Review the behavior and PR before merging. Story decisions belong
in `specs/`; development instructions belong in `docs/` and scoped `AGENTS.md` files.

RPG Maker and agents edit the same authored maps through the [editor workflow](#rpg-maker).

## Setup

Install [Git](https://git-scm.com/downloads) and
[uv](https://docs.astral.sh/uv/getting-started/installation/).
`uv run` obtains Python 3.12 and the project dependencies from `uv.lock`.
`uv sync --locked` installs them ahead of time. First setup needs network access;
later builds can use cached dependencies and the checked-in runtimes offline.

For checks, install [Node.js 24.14.1](https://nodejs.org/download/release/v24.14.1/),
the version in `.node-version`. `uv run check` runs `npm ci --ignore-scripts` when
the test lockfile changes. Node is not needed just to build or play.

| Computer | Additional requirement |
| --- | --- |
| macOS Intel/ARM | Xcode command-line tools (`xcode-select --install`); no Apple developer certificate |
| Windows x64 | None for the player; install RPG Maker XP separately only for its editor |
| Linux x86_64 | Ubuntu 22.04/24.04 [runtime libraries](players/linux.txt); graphical desktop for playing |

The game bundles Ruby; a system Ruby installation is not required for development.

## Commands

| Command | Result |
| --- | --- |
| `uv run play` | Compile authored maps/content/assets/Ruby and launch a native development player |
| `uv run build` | Same build without launching; prints its path |
| `uv run build --platform windows` | Cross-package a Windows development copy |
| `uv run build --platform linux` | Cross-package a Linux x86_64 development copy |
| `uv run format` | Format handwritten Python and Ruby |
| `uv run format --check` | Check formatting without editing |
| `uv run check` | Compile, then check formatting, tooling, geometry, scripts, named Tidebound API calls and quest/save behavior |
| `uv run check --all` | Also regenerate in isolation and compare outputs |
| `uv run build --compile-only` | Compile the project and checkpoint it without packaging a player |
| `uv run tidebound package mac ../candidate` | Stage and verify a release ZIP; requires a clean checkout |
| `uv run editor import` | Import saved map/tileset and stock edits into source; works on every platform |

`uv run build` is the game command. `uv build` builds a Python package, not
Tidebound. `uv run tidebound --help` lists the commands.

Development builds stage the native player directly, without making a release ZIP.
Builds go into unique ignored `.build/dev/` directories. Development players use
`Tidebound_Development` saves, shared between development builds. Release saves
stay in `Tidebound_Opening_0_2`; installed release apps are not replaced.
Closing the game returns control to `uv run play`. Old `.build/dev/` players and `.cache/` extractions can be deleted when no game is
running. Preserve `.build/editor.json` until editor changes have been imported;
it records the comparison point, not a player save.

Formatting uses [Ruff](https://docs.astral.sh/ruff/formatter/) for Python and
[Syntax Tree](https://github.com/ruby-syntax-tree/syntax_tree) for Ruby. Ruby runs
in the locked WASM test runtime; formatter libraries are pinned by URL/version
and SHA-256 in `tests/formatters.lock.json`, then cached under `.cache/formatters/`.
First formatting/check needs network access. Generated Ruby tables and stock
engine reference files are excluded. Format before rebuilding the script archive.

## Editing without losing work

Edit `src/tidebound/`, register new files in `src/load_order.txt`, then run `uv run play` or `uv run build --compile-only`. The engine
reads `game/Data/Scripts.rxdata`; source edits must be embedded. Never install a
second plugin copy. See [architecture](architecture.md) for ownership.

## RPG Maker

The everyday Mac workflow is agent/source edits followed by `uv run play`, with
`--from` for a declared starting state. RPG Maker is optional; builds never launch it.

1. `uv run build` (optionally `--compile-only`) or `uv run play` compiles the game
   and automatically records the exported map/tileset state after success.
2. For visual map editing, open `game/Game.rxproj` manually in RPG Maker XP on
   a compatible Windows environment. Edit and **save**, then close the editor.
3. Run `uv run editor import`. Tiles, events (including all pages/routes), map
   audio, names/tree placement, custom tileset settings and textures return to
   their `content/` bundles. Stock native edits go to `content/overrides/`. Review `git diff`, then `uv run play`.

The importer compares editor and source changes against the last export. Edits to
separate fields or tile cells merge. Concurrent edits to event pages, command lists
or movement routes conflict as a whole: their positions are not stable identities.
Conflicts stop before any source is written. Resolve in source/editor and rerun. Scrolling, expanding a
map in the editor, and Marshal encoding differences do not create source changes.
Before exporting, builds compare the native project against the last build/import
checkpoint and refuse pending editor edits until imported. Once that check passes, the old
checkpoint is cleared; a new one is recorded only after compilation and validation
succeed. Fix failed builds and rebuild before continuing map editing.
Unsaved editor changes cannot be detected, so always save and close first.

New maps created in RPG Maker become `content/maps/<name>/` bundles on import,
keeping their native map IDs and tree placement. The name becomes a lower_snake_case
folder; an existing folder gets the map ID suffix. Renaming a map later changes
its display name, not its bundle key. Add named playtest entrances and actor roles
only when needed; ordinary editor transfers work without that extra metadata.
An unconnected draft map has no reachability starting point, so static interaction
checks begin once it has an entrance or incoming transfer.

Existing authored maps and custom tilesets round-trip through this workflow.
Stock maps, stock tileset records, native databases and assets import as engine-relative
files in `content/overrides/`. Mixed map/tileset databases exclude authored records
from those overrides. Concurrent changes to the same override stop with a conflict.
Edits to generated scripts/PBS/species data or other generated assets without an
importer stop with an error: change their owning source instead. Native file
deletion is not imported. Adding a custom tileset or editing
its light mask uses the [map guide](../content/maps/AGENTS.md). To remove an entire
authored map, import pending edits first, remove its source bundle and update its
references, then rebuild; whole-map deletion in RPG Maker is not imported.
Do not delete `.build/editor.json` to bypass a conflict.

Use `uv run play` for native playtesting with isolated development saves. XP's
own Test Play requires extracting `runtime/Windows/player.zip` into `game/` once
and uses the project/release save namespace. No editor installation is needed for
JSON authoring, importing saved project files or native Mac/Linux playtesting.

`game/` and `src/generated/` are ignored outputs, created automatically by build,
play, preview, check and release packaging. The pinned baseline is checked in,
so game assembly needs no extra download. If compilation fails, fix the reported
error and rebuild before editing in Maker. Commit authored source changes only.
No development command commits, pushes, merges or publishes.

When upgrading a checkout from the old tracked `game/` layout, save and import
pending map edits **before pulling**. Commit any remaining stock edits so Git
can protect them during the update. After pulling, preserve any remaining old
`game/` directory outside the checkout before the first build; do not discard
unimported work. A fresh clone needs only `uv run play`. Missing checkpoints on an
existing project stop the build rather than assume its contents are disposable.

## Authoring workflows

The scoped guides explain the source files, engine contracts and checks for
[gameplay](../src/AGENTS.md), [maps](../content/maps/AGENTS.md),
[species/forms](../content/pokemon/AGENTS.md),
[Pokémon artwork](../content/AGENTS.md) and [sound](../content/audio/AGENTS.md).
They apply to human development as well as agents.

Rebuild exports [authored custom assets](../content/AGENTS.md), fixed tilesets, maps and lighting. Stock engine graphics/audio come from the baseline and native overrides. Check the asset guide before
editing a game PNG: generated destinations are replaced by their exporter.

## Less common work

Reusable tools live in the installed `tidebound_dev` package. The everyday commands
call the same operations as CI; `pipeline.py` owns the full rebuild sequence. Short aliases such as `uv run format`
and `uv run tidebound format` use the same options and implementation.
Run a diagnostic module with `uv run python -m tidebound_dev.<module>` or a
focused test with `uv run python -m unittest tests.tooling.test_assets -v`
(see [testing](../tests/AGENTS.md) for suite boundaries). To generate a portable game specification PDF, run
`uv run --group docs python -m tidebound_dev.documents.specification`; use `--output /path/to/preview.pdf`
to choose another destination. The default `specs/game-design.pdf` is ignored;
commit the Markdown and renderer, not generated PDFs. macOS/Windows use Times New Roman and Arial; Linux needs
Liberation Serif and DejaVu Sans (`fonts-liberation` and `fonts-dejavu-core` on Ubuntu).
Approved audio files need no composer or encoder dependency. Rebuilding the Mac engine is separate from
packaging: see [runtime provenance](runtime/macOS.md).

Verified release candidates require a clean checkout and the procedure in
[releasing](releasing.md). Development copies are not release artifacts.

## Branches and pull requests

Work in `ziemniaki/tidebound`, without forks. Start from the current checkout and
preserve uncommitted work. A focused PR should describe the resulting behavior,
any changed integration contracts and the verification actually performed.

Quick checks run on pushes. Request `/verify` before merging substantial gameplay
or runtime changes; docs-only changes need link/contract review and quick checks.
Validate workflow definitions with `actionlint`. When they need native verification,
dispatch it on the changed branch: `/verify` uses the trusted workflow.
Releases assume the merged changes are tested; version bumps do not require a
fresh full matrix or manual playtest. Tags package and publish automatically.
Keep status-writing permissions separate from execution of untrusted PR code.
Publication follows the separate [release procedure](releasing.md).

## Independent feature work

Use separate checkouts for simultaneous agents; changing branches in a shared
directory does not isolate edits or builds. Before splitting work, agree the
contracts being touched: map/species/form IDs, actor identities and roles, handler
keys, public Ruby calls and script load order. Keep each feature's edits together.
The [task table](../AGENTS.md#read-for-your-change) routes to its source owner.

Coordinate changes to `src/load_order.txt`, `maps/compiler.py`, `maps/registry.py`,
species catalogs and shared NPC dispatch. Individual map layouts belong in
`content/maps/<map>/`; another area must not patch their events or geometry.

Include authored source changes in the PR. When combining work, resolve source
conflicts, then run `uv run format` and `uv run check --all`. Generated binaries
are ignored and rebuilt from the combined sources. Native override conflicts
need deliberate reconciliation; never choose one editor database wholesale when
both branches changed it. Never build in another agent's active checkout.
Handoffs name the branch/commit, checks and remaining work.

## Asset previews

Edit the approved source, then launch the asset viewer:

```sh
uv run preview pokemon/WHYDUCK
uv run preview actors/ivo
uv run preview props/moored_ship
uv run preview items/TIDEBOUNDOILKEYS
uv run preview trainers/TBLOCALYOUTH
uv run preview ui/title
uv run preview audio/music/shore
```

Use exact asset IDs/filenames without extensions. The command refreshes approved
assets and opens the viewer. Pokémon previews show normal/shiny front/back
sprites and animated icons; character previews animate all four directions.
Prop crosshairs mark the event anchor. Audio plays through Essentials' wrappers;
Enter replays it, Esc closes. This is a disposable development player: the preview
Main never enters a game or loads/writes a player save and never ships in releases.
Battle positioning metrics, map collisions, lighting and music transitions still
need inspection in their actual scenes.

## Playtest scenarios

```sh
uv run play --from neighbor/meal
```

This starts the **full game** with the declared starting state: location, party,
bag and story progress. Keep playing, travel, battle and save normally.
Omitting `--from` opens the normal development title screen. Each `--from` launch
starts fresh; saves made during it use `Tidebound_Playtest`, a scratch slot separate from normal development and
release saves. Concurrent playtests share that scratch slot.

Starting states live beside their feature in `src/tidebound/features/<feature>/scenarios/`.
For example, `neighbor/meal.json` reuses `opening/exploration` and changes only:

```json
{
  "base": "opening/exploration",
  "location": ["home", "from_coast"],
  "bag": {"TIDEBOUNDPIE": 1},
  "story": {"neighbor_quest": {"stage": ":pie"}}
}
```

Copy [the baseline](../src/tidebound/features/opening/scenarios/exploration.json)
for the complete format. `party` and `household` contain Pokémon directly, e.g.
`{"species": "NATU", "level": 12, "item": "MYSTICWATER"}`; `name` and `moves`
are optional. A base is standalone (no inheritance chains). Other fields replace
it; `story` merges only its top-level keys. `":pie"` denotes a Ruby symbol;
ordinary strings stay text. Map/entrance and species/item references are checked.

State is installed before map callbacks. Declare the flags needed to skip earlier
autoruns. Use `play --from` after editing either the starting state or game content; it
rebuilds before resolving map/species/item references. The starting-state driver is staged only for development;
keep `tools/tidebound_dev/scenarios.rb` out of `src/load_order.txt` and releases.
