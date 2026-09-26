# Demo 1 / 0.8.0 validation — 23 September 2026

Based on the maintained 0.7.24 project. Mac build34, same native runtime and save directory. No GitHub synchronization configured.

## Completed checks

- Regenerated all 16 authored maps and collision masks. Validator passes 264 events, every arrival/door/interaction reachable, existing coastal camera margin preserved, embedded scripts equal editable numbered sources.
- Native Linux mkxp-z run using a retained pre-update save: party identity and inventory preserved through new dock scenes; regional road Psyduck Water/Psychic; evolution absent at15 and available at16; Whyduck resets to form0; ordinary Psyduck still evolves into Golduck at33.
- Actual native battles: both optional sailor teams defeated with a strong test-only party; wins persisted. Visible Psyduck encountered and defeated through normal battle flow; disappearance flag set. Five engine death messages recorded, all say died and none fainted. This isolates event integration, not difficulty balance.
- Native captain invitation accepted twice: demo-completed state set, no invalid transfer, exploration remains in map112. Full save written successfully with additive demo state. A blocked old-save position on a new sailor relocates to a clear square; repeated recovery is idempotent.
- Engine screenshots inspected for houses/window glow, unchanged lighthouse, visible duck, ships/crews and two-line opening caption. Caption text has no change to routes, goal, timing or steps. A final render-only pass covers the small prop/wood-palette cleanup.
- Bible version1.27 PDF regenerated; revised species and new demo sections visually inspected. Guide2.25, README, status, player instructions and Whyduck species sheet synchronized.
- No disposable test driver embedded in the release. Mac/source archive integrity and matching Scripts hash checked during packaging.

## Scope and limits

This workspace cannot execute macOS. The native Mac app uses the same runtime as the user's working baseline; a Monterey playtest remains needed. Tests use Linux mkxp-z offscreen and automated inputs. They do not replace a fresh human playthrough or assess optional-battle balance. Existing intro, necklace, vault and museum quests were preserved, rather than fully replayed in this targeted pass. No island map or sailing gameplay has been built.

Previous 99 new-game Rare Candies remain by explicit earlier request. The captain endpoint is repeatable and does not force quitting or overwrite the save. Base fainting internals and party UI status labels remain engine terminology; visible battle/field loss messages use died.
