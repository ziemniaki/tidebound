# Tidebound — The Keeper’s Light

**Demo 1 · version 0.8.0 · Pokémon Essentials 21.1**

A solitary Pokémon journey through a haunted coastal land. Begin with a bird in a dream, return to a lighthouse home, and follow an ordinary errand toward a working harbour.

## Play the current demo

Open this repository’s **Releases**, choose **Demo 1 — 0.8.0**, and download **Tidebound_Mac_0.8.0.zip**. Unzip it and open Tidebound.app. The native app targets Intel Macs running Monterey 12.7.5; no Wine or Codex installation is needed. Read [MAC_README.txt](MAC_README.txt) for first-launch help.

For Windows, download **Tidebound_Project.zip** from the same release, extract it and run Game.exe. Keep the project’s folders together.

Arrow keys move; Enter interacts; Esc opens the menu. Save manually. Existing Tidebound saves use the same save folder. The current demo retains 99 starting Rare Candies for testing evolutions.

The eastern-pier captain’s invitation to Psyduck Island marks the demo’s end. You can continue exploring afterward; the voyage and island are future content.

**Migration status:** The complete current project and Mac demo are available in the release assets. The main documentation is browsable below. Importing the remaining individual source/assets into this Git tree is pending explicit approval of the one-time import operation. Until then, use Tidebound_Project.zip for the complete working project.

## Project navigation

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions for continuing development |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current implementation and known limitations |
| [START_HERE.md](START_HERE.md) | Opening walkthrough — spoilers |
| [Development/design_bible.md](Development/design_bible.md) | Full game bible — major story spoilers |
| [Development/design_bible.pdf](Development/design_bible.pdf) | Reading copy of the bible |
| [Development/README.md](Development/README.md) | Build and editing instructions |
| [Development/REPOSITORY_WORKFLOW.md](Development/REPOSITORY_WORKFLOW.md) | Repository, releases and handoff rules |
| Development/ | Editable Ruby scripts, map/data generators, art sources and tests |
| Data/, PBS/, Graphics/, Audio/ | Current compiled game data, definitions and assets |
| Runtime/macOS/ | Native runtime template, source and provenance |

This repository begins with the current 0.8.0 snapshot only. Earlier game releases and archived test screenshots are not imported. Source art and tests needed to maintain the current game remain included. Historical design decisions inside the bible are retained for continuity.

Game-engine and map checks passed under native Linux mkxp-z. The native Mac package still needs the corresponding Monterey playtest. See [the current validation report](Development/validation_demo_080.md).

Unofficial fan project. See [CREDITS.md](CREDITS.md) and the runtime’s provenance/license files for attribution. This repository does not grant rights to Pokémon or other third-party assets.
