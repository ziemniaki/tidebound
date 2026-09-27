# Working on Tidebound

Pokémon Essentials 21.1 on mkxp-z; gameplay stays Ruby, authoring/build tools stay
Python. Deliver a complete, playable change within the requested scope.
Creative authority is [specs/game-design.md](specs/game-design.md); planned lore
and provisional mechanics are not permission to implement them.

## Engineering standard

- Follow all applicable authoring, build, verification and release workflows,
  including linked guides. Read the existing implementation before changing it.
  When a workflow needs a lasting capability, extend it rather than creating a bypass.
- Prefer no new code when a source edit, existing tool or manual one-off completes
  the task cleanly. Temporary scripts are fine for one-off work; do not turn them
  into permanent tooling without a concrete recurring need.
- For lasting code changes, extend the existing owner and shared path. Prefer a
  declaration or a small API change over a special-case script, duplicate pipeline,
  manual output patch or permanent workaround for one task.
- Make extensions useful to the next similar case without another exception.
  Keep one source of truth and reuse discovery, validation and lifecycle rules.
  Update the workflow, its checks and its documentation together.
- Build the simplest complete solution. Add the complexity the feature needs;
  do not cut required behavior or weaken correctness to keep the code small.
  Every new abstraction, branch or configuration option must earn its maintenance
  cost through a concrete requirement or shared use. Reduce incidental complexity
  where feasible. Generalize demonstrated needs;
  avoid speculative frameworks and unrelated refactors. Keep feature-specific
  behavior with its feature until there is a concrete shared responsibility.
- Finish the integration: connect source to its consumer, regenerate required
  outputs, run the applicable checks and report what was actually verified.

## Read for your change

Read [current status](docs/status.md), then the applicable guides below, including
cross-directory guides when your task touches their outputs. Each guide names
its source files, engine traps and verification; do not load every guide by default.
Keep shared rules here, local contracts in scoped guides and detailed procedures
in `docs/`. Update the owning document rather than duplicating instructions.

| Task | Guide |
| --- | --- |
| Quest, dialogue, battle, save or sprite behavior | [src/AGENTS.md](src/AGENTS.md) |
| Add/edit a map, actor or transfer | [maps/AGENTS.md](content/maps/AGENTS.md) |
| Species/form, evolution or encounter data | [pokemon/AGENTS.md](content/pokemon/AGENTS.md) |
| Items, actors, artwork and prop anchors | [content/AGENTS.md](content/AGENTS.md) |
| Music, sound effect or cry | [audio/AGENTS.md](content/audio/AGENTS.md) |
| Authoring/build tools or CLI | [tooling/AGENTS.md](tools/tidebound_dev/AGENTS.md) |
| Asset pipeline | [art/AGENTS.md](tools/tidebound_dev/art/AGENTS.md) |
| RPG Maker edits or compiled game files | [game/AGENTS.md](game/AGENTS.md) |
| Start a playthrough from a declared state | [Playtest workflow](docs/development.md#playtest-scenarios) |
| Add/change tests | [tests/AGENTS.md](tests/AGENTS.md) |
| Packaging, CI, release | [releasing](docs/releasing.md), [runtime notes](docs/architecture.md#runtime-boundaries) |

Use the embedded engine as the version authority; tutorials for other versions
are not API contracts. See [Essentials contracts](docs/essentials-contracts.md)
and [structure and naming](docs/architecture.md#authored-content).

## Commands and shared outputs

Run from the repository root. uv owns Python dependencies; Node is pinned in
`.node-version`; gameplay uses bundled Ruby (no system Ruby setup).

```sh
uv run play           # compile authored game, stage and launch a development player
uv run build          # same compilation without launch
uv run preview pokemon/WHYDUCK  # inspect one asset without loading a save
uv run format         # before embedding Ruby
uv run build --compile-only # update the compiled project without packaging a player
uv run check          # headless gate; never regenerates tracked game data
uv run check --all    # also regenerate in isolation and compare
```

Both build modes and play use the same complete compilation. Stage new sources and
outputs before `check --all`: its input set comes from `git ls-files`.
Setup/editor details: [development](docs/development.md).

Use a focused branch in `ziemniaki/tidebound`, never a fork. Independent agents
need separate checkouts. Before splitting work, agree map/species/form IDs, actor
identities, handler keys and shared entry points; report changes in the PR.
Combine source first, then regenerate shared binaries once; never resolve binary
conflicts by choosing one agent's output wholesale.
Follow the [integration workflow](docs/development.md#independent-feature-work).

## Project constraints

- Maps are authored in `content/maps/`; import saved RPG Maker edits with
  `uv run editor import` before rebuilding. `game/Data` still contains irreplaceable
  stock inputs; never clear it.
- Preserve current Pokémon identity, held items and quest state. An empty party
  may be an astral journey. Do not add save versions, compatibility gates or old
  migration chains. Never delete player saves to make a check pass.
- Release saves use `Tidebound_Opening_0_2`; `play` uses `Tidebound_Development`.
  RPG Maker Test Play uses the project/release namespace. Keep `fontHeightReporting: 1`.
- Ordinary locations remain night. Maintenance does not authorize engine or
  gameplay redesign. Update current docs in place when behavior changes.
- PR pushes run quick checks; full builds use `/verify` or release tags. Keep Mac
  CI at one translocated launch per architecture; other paths are manual diagnostics.
  Docs-only changes do not need a platform matrix. Report actual checks/playtests.
- Release assets are three player ZIPs: Mac universal, Windows x64, Linux x86_64.
  Published tags/assets are immutable. Notes are one concise player-facing list.
