# Tidebound — The Keeper’s Light

**Demo 1 · version 0.8.3 · Pokémon Essentials 21.1**

A solitary Pokémon journey through a haunted coastal land. Begin with a bird in a dream, return to a lighthouse home, and follow an ordinary errand toward a working harbour.

## Play the current demo

The current working build is **0.8.3**. Download **Tidebound_Mac_0.8.3.zip** from the development handoff; GitHub release publication is pending. Unzip it and open Tidebound.app. The native app targets Intel Macs running Monterey 12.7.5. Read [MAC_README.txt](MAC_README.txt) for first-launch help.

For Windows, extract **Tidebound_Project_0.8.3.zip** and run Game.exe. Keep its folders together. The latest published GitHub release remains 0.8.1 until a newer release is explicitly verified.

Arrow keys move; Enter interacts; Esc opens the menu. Save manually. Existing Tidebound saves use the same save folder. The current demo retains 99 starting Rare Candies for testing evolutions.

The eastern-pier captain’s invitation to Psyduck Island marks the demo’s end. You can continue exploring afterward; the voyage and island are future content.

## Changes in 0.8.3

The youngsters' hideout is now a cold, neglected squat: boarded windows, torn pallet mattresses, damaged storage, peeling walls and no household lamps. Its previous sequence remains: a cluttered interior with a small rubbish maze, a guarded sofa, a surprising horror minigame and a revised necklace handoff. Minigame wins survive a lost boss battle. Earlier Aipom and regional Normal/Dark snake changes remain included.

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

Native Linux rendering, both hideout battles, minigame controls, quest/save and package checks passed. The 0.8.3 Mac package still needs its Monterey playtest. See [the current validation report](Development/validation_hideout.md).

Unofficial fan project. See [CREDITS.md](CREDITS.md) and the runtime’s provenance/license files for attribution. This repository does not grant rights to Pokémon or other third-party assets.
