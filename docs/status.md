# Current status

**Playable baseline:** Demo 1, version 0.8.11. Pokémon Essentials 21.1, pinned
mkxp-z runtime; universal Mac, Windows x64 and Linux x86_64 releases.

The demo includes the dream opening, lighthouse family and companion choice,
oil-shop errand, forest/coastal encounters, necklace pursuit, hideout and Mending
minigame, vault/museum visit, docks and southern pond. The captain's Psyduck
Island conversation reaches the demo endpoint.

The dock-city upgrade adds three optional harbour errands, residents with local
histories and a north-eastern outdoor ring. Machop and Hitmonlee spar beside
betting sailors; Harker offers a saved, party-scaled challenger every 15 real
minutes. Names, rewards and the curated opponent roster remain provisional.

Island voyage gameplay, later Team Abyss chapters, shrine progression, Dive,
Koga's settlements, late Suicune/sabre story, cemetery finale and endings remain
planned. Helpers and concept art do not make those chapters playable. Respect
the confirmed/proposed/open labels in [the specification](../specs/game-design.md).

## Maintenance baseline

Game files, Ruby source, tools, tests, specifications and documentation have
separate homes. `uv run play/build/check` is the common entry point, with locked
Python dependencies. The native project restores from a pinned offline Essentials baseline and authored
sources; `game/` and `src/generated/` are ignored outputs. Windows binaries restore
from pinned archives. RPG Maker
XP opens `game/Game.rxproj`; authored maps round-trip through JSON.

The current release includes the Mac Downloads/App Translocation and long-path fixes.
CI covers relocated Unicode paths, saves and rendering on both Mac architectures,
Windows and Ubuntu 22.04/24.04. Mac is ad-hoc signed, not notarized. Smoke tests
do not replace gameplay, audio, hardware-GPU or Intel Monterey 12.7.5 playtesting.

Current authoring uses one rebuild plan, catalog-derived content checks, shared
map-local declarations, named entrances/stable event IDs, feature-owned actor policies
and fixed editable tilesets. Generated content and assets have explicit ownership. `play` refreshes approved assets automatically;
`preview` inspects them without entering a game.
[Declared starting states](development.md#playtest-scenarios) support focused playtesting. Saves use
the normal Essentials serializer without custom versioning. See
[architecture](architecture.md) for ownership and [development](development.md)
for the edit/build/check loop and scoped authoring guides.

## Next work

- Playtest the current demo on the maintainer's target machines.
- Playtest the harbour errands and ring via `play --from docks/harbour` and
  `play --from docks/ring`; check ropes, animation, battle cancellation and astral
  recovery on the target machines before releasing this upgrade.
- Split large gameplay modules by feature when changing that feature; preserve
  current save state and the explicit source manifest order.
- Consider external binary hosting/LFS only with tested automatic restoration.
  Current runtime archives remain available offline.

Keep this page current and brief. Git history preserves retired implementations
and earlier verification evidence.
