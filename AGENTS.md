# Working on Tidebound

Pokémon Essentials 21.1 on mkxp-z; gameplay stays Ruby, authoring/build tools stay
Python. The maintainer often works through agents. Deliver a playable change.
Creative authority is [specs/game-design.md](specs/game-design.md); planned lore
and provisional mechanics are not permission to implement them.

## Read for your change

Read [current status](docs/status.md), then the applicable guides below, including
cross-directory guides when your task touches their outputs. Each guide names
its source files, engine traps and verification; do not load every guide by default.

| Task | Guide |
| --- | --- |
| Quest, dialogue, battle, save or sprite behavior | [src/AGENTS.md](src/AGENTS.md) |
| Add/edit a map, actor or transfer | [maps/AGENTS.md](tools/tidebound_dev/maps/AGENTS.md) |
| Species/form, evolution, item or encounter data | [content/AGENTS.md](tools/tidebound_dev/content/AGENTS.md) |
| Pokémon artwork, icons and export recipes | [assets/AGENTS.md](assets/AGENTS.md) |
| Music, sound effect or cry | [art/AGENTS.md](tools/tidebound_dev/art/AGENTS.md) |
| RPG Maker edits or compiled game files | [game/AGENTS.md](game/AGENTS.md) |
| Add/change tests | [tests/AGENTS.md](tests/AGENTS.md) |
| Packaging, CI, release | [releasing](docs/releasing.md), [runtime notes](docs/architecture.md#runtime-boundaries) |

[Essentials contracts](docs/essentials-contracts.md) indexes the inspected engine
methods and upstream sources. Use the embedded engine as the version authority;
a tutorial for another Essentials version is not an API contract.

## Commands and shared outputs

Run from the repository root. uv owns Python dependencies; Node is pinned in
`.node-version`; gameplay uses bundled Ruby (no system Ruby setup).

```sh
uv run play           # embed current Ruby, stage and launch a development player
uv run build          # stage only; does not regenerate maps/content
uv run format         # before embedding Ruby
uv run rebuild        # embed src/load_order.txt into game/Data/Scripts.rxdata
uv run rebuild --all  # regenerate maps/content/art, then embed
uv run check          # headless gate; never regenerates tracked game data
uv run check --all    # also regenerate in isolation and compare
```

Full rebuild reproduces registered pixel exports; ambient audio production is
optional. See the asset/audio guides. Stage new files before `check --all`: its input set comes
from `git ls-files`. Setup/editor details: [development](docs/development.md).

Use a focused branch in `ziemniaki/tidebound`, never a fork. Independent agents
need separate checkouts; Git branches alone do not isolate writes. Map IDs, actor
identities, species/form IDs, event-handler keys and shared entry points are integration
contracts. Agree those before splitting work; report them in the PR. After combining
source changes, regenerate shared binaries once from the combined source. Never
resolve `Scripts.rxdata`, species databases or generated maps by choosing one
agent's binary wholesale. [Integration workflow](docs/development.md#independent-feature-work).

## Project constraints

- Maps 101–116 are generator-owned. Reconcile direct editor work before full
  rebuild. `game/Data` also contains irreplaceable stock inputs; never clear it.
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
