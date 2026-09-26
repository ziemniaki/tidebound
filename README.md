# Tidebound — The Keeper’s Light

**Demo 1 · version 0.8.6 · Pokémon Essentials 21.1**

A solitary Pokémon journey through a haunted coastal land. Begin with a bird in a dream, return to a lighthouse home, and follow an ordinary errand toward a working harbour.

## Play

[GitHub Releases](https://github.com/ziemniaki/tidebound/releases) has one ZIP each
for Mac (Intel and Apple Silicon), Windows x64 and Linux x86_64.

## Changes in 0.8.6

The Mac app runs from Downloads, temporary folders and macOS App Translocation;
it no longer requires installation in Applications. Packages support relocation
and paths with spaces or non-ASCII names. Linux launchers also work through
symbolic links. Existing saves remain in `Tidebound_Opening_0_2`, outside the game.

The Mac app remains ad-hoc signed and not notarized. Linux targets Ubuntu
22.04/24.04 and may need the libraries listed in [LINUX_README.txt](LINUX_README.txt).

## Changes in 0.8.4

The southern pond adds three optional fishermen, Psyduck/Aipom/Sunkern grass, the relocated visible Psyduck, an Oran tree and a hidden Mystic Water. A central obelisk is reserved for later Surf. The refined squat and its horror minigame remain included. Psyduck Island remains the demo endpoint, not a newly implemented destination.

## Project navigation

For development, start with [fresh-clone setup and verification](Development/README.md).
The [DX and reliability review](Development/DX_RELIABILITY_REVIEW.md) records
verified findings, the initial tooling fixes, and remaining priorities.
The [build and release guide](Development/RELEASING.md) covers universal Mac
and Windows/Linux packages, native platform smoke checks and automated draft releases. Existing
published downloads remain unchanged until a new version is released.

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

Native Linux rendering, both hideout battles, minigame controls, quest/save and package checks passed. Full Monterey gameplay, controls, audio and save/load remain a manual release check. See [the current validation report](Development/validation_hideout.md).

Unofficial fan project. See [CREDITS.md](CREDITS.md) and the runtime’s provenance/license files for attribution. This repository does not grant rights to Pokémon or other third-party assets.

Windows player ZIPs and native Windows CI are documented with the Mac builds in
[Development/RELEASING.md](Development/RELEASING.md).
