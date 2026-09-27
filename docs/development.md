# Development

The normal loop is **edit → `uv run format` → `uv run play` → `uv run check`**.
Run commands from the checkout; no environment activation or manual runtime
copying is needed.

## Agent-assisted development

Describe the player-visible change and affected area. The agent reads `AGENTS.md`,
implements it on a branch, and builds a development player for you to try with
`uv run play`. Review the behavior and PR before merging. Story decisions belong
in `specs/`; development instructions belong in `docs/` and scoped `AGENTS.md` files.

If you also edit maps in RPG Maker XP, tell the agent which maps changed before
regeneration so those edits can be incorporated into their Python source.

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
| `uv run play` | Embed current Ruby, build and launch a native development player |
| `uv run build` | Same build without launching; prints its path |
| `uv run build --platform windows` | Cross-package a Windows development copy |
| `uv run build --platform linux` | Cross-package a Linux x86_64 development copy |
| `uv run format` | Format handwritten Python and Ruby |
| `uv run format --check` | Check formatting without editing |
| `uv run check` | Formatting, tooling, geometry, scripts and quest/save tests; no game regeneration |
| `uv run check --all` | Also regenerate in isolation and compare outputs |
| `uv run rebuild` | Export custom assets and embed the Ruby load manifest |
| `uv run rebuild --all` | Regenerate maps, data, pipeline-owned art, reports and scripts |
| `uv run tidebound package mac ../candidate` | Stage and verify a release ZIP; requires a clean checkout |
| `uv run editor` | On Windows, restore ignored helpers and open `game/Game.rxproj` |

`uv run build` is the game command. `uv build` builds a Python package, not
Tidebound. `uv run tidebound --help` lists the commands.

Development builds stage the native player directly, without making a release ZIP.
Builds go into unique ignored `.build/dev/` directories. Development players use
`Tidebound_Development` saves, shared between development builds. Release saves
stay in `Tidebound_Opening_0_2`; installed release apps are not replaced.
Closing the game returns control to `uv run play`. Old `.build/` directories and
`.cache/` extractions can be deleted when no game is running; neither holds saves.

Formatting uses [Ruff](https://docs.astral.sh/ruff/formatter/) for Python and
[Syntax Tree](https://github.com/ruby-syntax-tree/syntax_tree) for Ruby. Ruby runs
in the locked WASM test runtime; formatter libraries are pinned by URL/version
and SHA-256 in `tests/formatters.lock.json`, then cached under `.cache/formatters/`.
First formatting/check needs network access. Generated Ruby tables and stock
engine reference files are excluded. Format before rebuilding the script archive.

## Editing without losing work

Edit `src/tidebound/`, register new files in `src/load_order.txt`, then run `uv run play` or `uv run rebuild`. The engine
reads `game/Data/Scripts.rxdata`; source edits must be embedded. Never install a
second plugin copy. See [architecture](architecture.md) for ownership.

RPG Maker XP opens `game/Game.rxproj`. `uv run editor` restores its local runtime
and optional helpers from pinned archives. The editor edits the real project;
its own Test Play uses the project's normal save namespace. Use `uv run play`
for isolated development saves. Generated maps 101–116 must be reconciled with
their Python generators after direct editor changes. `rebuild --all` overwrites
those maps; review or commit editor work before intentionally regenerating.
Ordinary `play` refreshes custom artwork/audio and scripts; it preserves map geometry.

Full regeneration writes directly to tracked files. If it fails, fix the reported
error and rerun `uv run rebuild --all` before playing. Review the generated diff
in Git; `uv run check --all` verifies reproducibility in a disposable copy.

Keep compiled data checked in: stock Essentials inputs cannot all be rebuilt
from the custom generators. Review generated diffs alongside source changes.
No development command commits, pushes, merges or publishes.

## Authoring workflows

The scoped guides explain the source files, engine contracts and checks for
[gameplay](../src/AGENTS.md), [maps](../tools/tidebound_dev/maps/AGENTS.md),
[species/forms](../tools/tidebound_dev/content/AGENTS.md),
[Pokémon artwork](../assets/AGENTS.md) and [sound](../tools/tidebound_dev/art/AGENTS.md).
They apply to human development as well as agents.

Ordinary rebuild refreshes the [registered custom assets](artwork.md); full rebuild
also repacks map tilesets and lighting. Stock engine graphics/audio are direct inputs. Check the asset guide before
editing a game PNG: generated destinations are replaced by their exporter.

## Less common work

Reusable tools live in the installed `tidebound_dev` package. The everyday commands
call the same operations as CI; `pipeline.py` owns the full rebuild sequence. Short aliases such as `uv run format`
and `uv run tidebound format` use the same options and implementation.
Run a diagnostic module with `uv run python -m tidebound_dev.<module>` or a
focused test with `uv run python -m unittest tests.tooling.test_assets -v`
(see [testing](testing.md) for suite boundaries). Optional PDF regeneration has separate dependencies. For the game specification PDF, run
`uv run --group docs python -m tidebound_dev.documents.specification`; use `--output /path/to/preview.pdf`
to render a preview. macOS/Windows use Times New Roman and Arial; Linux needs
Liberation Serif and DejaVu Sans (`fonts-liberation` and `fonts-dejavu-core` on Ubuntu).
Approved audio files need no composer or encoder dependency. Rebuilding the Mac engine is separate from
packaging: see [runtime provenance](runtime/macOS.md).

Verified release candidates require a clean checkout and the procedure in
[releasing](releasing.md). Development copies are not release artifacts.

## Branches and pull requests

Work in `ziemniaki/tidebound`, without forks. Start from the current checkout and
preserve uncommitted work. A focused PR should describe the resulting behavior,
any changed integration contracts and the verification actually performed.

Quick checks run on pushes. Request `/verify` before merging substantial changes;
docs-only changes need link/contract review and quick checks. Workflow-definition
changes need branch-dispatched verification: `/verify` uses the trusted workflow.
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
`maps/areas/<map>/`; another area must not patch their events or geometry.

Include source and generated outputs in the PR. When combining work, resolve
source first, then regenerate once. For generator-owned binary conflicts, use a
known common baseline, apply the combined source, then run `uv run format`,
`uv run rebuild --all` and `uv run check --all`. Never choose one branch's archive
wholesale: that can discard another feature. Stock data and supplied editor/asset
edits need their own reconciliation. Never regenerate in another agent's active
checkout. Handoffs name the branch/commit, checks and remaining work.

## Tooling choice

uv provides one locked Python environment and command set on native Windows,
macOS and Linux, including CI. devenv requires Nix and WSL2 on Windows, which
does not reproduce the native Windows game/editor environment. Defer a mandatory
devenv shell until a concrete need outweighs that additional setup.

References: [uv projects](https://docs.astral.sh/uv/guides/projects/),
[uv entry points](https://docs.astral.sh/uv/concepts/projects/config/),
[devenv installation](https://devenv.sh/getting-started/).

## Asset previews

Edit the approved source, then launch the asset viewer:

```sh
uv run preview pokemon/WHYDUCK
uv run preview characters/Tidebound_Ivo_Seated
uv run preview props/ship1
uv run preview items/TIDEBOUNDOILKEYS
uv run preview trainers/TBLOCALYOUTH
uv run preview pictures/Tidebound/title
uv run preview 'audio/BGM/Tidebound Shore'
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
autoruns. Edits to starting states need only `play --from`; map/data changes still
need `uv run rebuild --all`. The starting-state driver is staged only for development;
keep `tools/tidebound_dev/scenarios.rb` out of `src/load_order.txt` and releases.
