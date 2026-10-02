# Tidebound — The Keeper’s Light

A Pokémon fangame about companionship, loss, and a haunted coast that never sees
daylight. Begin with a bird in a dream, return to a lighthouse home, and follow
an ordinary errand toward the harbour.

Built with Pokémon Essentials 21.1 and mkxp-z.

<p align="center">
  <img src="docs/images/lighthouse.png" alt="The lighthouse at night">
</p>

## Play

[Download the latest release](https://github.com/ziemniaki/tidebound/releases/latest)
for macOS (Intel or Apple Silicon), Windows x64, or Linux x86_64.
No development tools are needed. Tidebound is a continuously evolving game.
The current journey includes the lighthouse opening, coastal quests, harbour
errands, southern pond and a northern haunted forest with a skull-mouth cave.
Passage to Psyduck Island is offered at the harbour; the voyage and island are
still to come.

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[Git](https://git-scm.com/downloads), then:

```sh
git clone https://github.com/ziemniaki/tidebound.git
cd tidebound
uv run play
```

This builds and opens a native development copy with **separate development
saves**. Python dependencies and runtime extraction are handled automatically.
Mac builds need Xcode command-line tools; Linux needs the documented
[system libraries](docs/players/linux.txt).

```sh
uv run build       # build without opening the game
uv run check       # verify changes; requires Node 24.14.1
uv run preview pokemon/WHYDUCK  # inspect an asset in the engine
```

[Development guide](docs/development.md) · [Working with an agent](docs/development.md#agent-assisted-development)
· [Playtest starting states](docs/development.md#playtest-scenarios)
· [Architecture](docs/architecture.md) · [Testing](tests/AGENTS.md)
· [Releasing](docs/releasing.md) · [Engine contracts](docs/essentials-contracts.md)
· [Content guide](content/AGENTS.md) · [Walkthrough](docs/walkthrough.md)
· [Release notes](docs/release-notes.md)

## Project structure

| Directory | What belongs here |
| --- | --- |
| [`specs/`](specs/game-design.md) | Game design and creative decisions |
| `docs/` | Development, playtesting, releases and current status |
| `src/` | Custom Ruby gameplay and presentation |
| `game/` | Generated RPG Maker project and playable assets (ignored; created by build/play) |
| `tools/` | Build commands, map/data compilers and packaging |
| `tests/` | Headless checks and native runtime smoke tests |
| `content/` | Authored maps, Pokémon, items, actors, artwork and sound |
| `references/` | Concepts and working material outside the build |
| `runtime/` | Pinned engine inputs, patches and provenance |

Agents start with [AGENTS.md](AGENTS.md). Contributors should read the
[current status](docs/status.md) and preserve existing saves and creative direction.

## Feedback and credits

Report bugs through [GitHub Issues](https://github.com/ziemniaki/tidebound/issues),
including the game version, operating system and steps to reproduce.

Unofficial fan project. [Credits and third-party attribution](docs/credits.md)
apply; this repository does not grant rights to Pokémon or other third-party assets.
