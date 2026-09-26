# Development

The normal loop is **edit → `uv run play` → `uv run check`**.
Run commands from the checkout; no environment activation or manual runtime
copying is needed.

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

`uv run doctor` inspects prerequisites. The game bundles Ruby; a system Ruby
installation is not required for normal development.

## Commands

| Command | Result |
| --- | --- |
| `uv run play` | Embed current Ruby, build and launch a native development player |
| `uv run build` | Same build without launching; prints its path |
| `uv run build --platform windows` | Cross-package a Windows development copy |
| `uv run build --platform linux` | Cross-package a Linux x86_64 development copy |
| `uv run check` | Tooling, geometry, scripts and quest/save tests; no game regeneration |
| `uv run check --all` | Also regenerate in isolation and compare outputs |
| `uv run rebuild` | Embed the Ruby load manifest only |
| `uv run rebuild --all` | Intentionally regenerate maps, data, art, reports and scripts |
| `uv run editor` | On Windows, restore ignored helpers and open `game/Game.rxproj` |

`uv run build` is the game command. `uv build` builds a Python package, not
Tidebound. `uv run tidebound --help` lists the commands.

Builds go into unique ignored `.build/dev/` directories. Development players use
`Tidebound_Development` saves, shared between development builds. Release saves
stay in `Tidebound_Opening_0_2`; installed release apps are not replaced.
The refactored development build accepts save schema 2. Earlier demo saves are
unsupported and remain usable with their original release; the new reader rejects
them without rewriting their files. Use a fresh development save for this branch.
Closing the game returns control to `uv run play`. Old `.build/` directories and
`.cache/` extractions can be deleted when no game is running; neither holds saves.

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
Ordinary `play` rebuilds scripts, not map geometry.

Keep compiled data checked in: stock Essentials inputs cannot all be rebuilt
from the custom generators. Review generated diffs alongside source changes.
No development command commits, pushes, merges or publishes.

## Less common work

Run a tool with `uv run python tools/<name>.py` or a test with
`uv run python tests/<name>.py`. Optional audio/PDF regeneration has separate
dependencies. For the game specification PDF, run
`uv run --group docs python tools/render_bible.py`; use `--output /path/to/preview.pdf`
to render a preview. macOS/Windows use Times New Roman and Arial; Linux needs
Liberation Serif and DejaVu Sans (`fonts-liberation` and `fonts-dejavu-core` on Ubuntu).
Audio generation needs NumPy and ffmpeg. Rebuilding the Mac engine is separate from
packaging: see [runtime provenance](runtime/macOS.md).

Verified release candidates require a clean checkout and the procedure in
[releasing](releasing.md). Development copies are not release artifacts.

## Tooling choice

uv provides one locked Python environment and command set on native Windows,
macOS and Linux, including CI. devenv requires Nix and WSL2 on Windows, which
does not reproduce the native Windows game/editor environment. Defer a mandatory
devenv shell until a concrete need outweighs that additional setup.

References: [uv projects](https://docs.astral.sh/uv/guides/projects/),
[uv entry points](https://docs.astral.sh/uv/concepts/projects/config/),
[devenv installation](https://devenv.sh/getting-started/).
