# Hideout revision — Demo 1 / 0.8.2

25 September 2026. Baseline: GitHub 9ba7d3f, released 0.8.1.

## Verified

- Generated map109 retains its ID, original event IDs and arrival11,14. All
  268 story-map events pass connectivity/arrival/interaction checks; embedded
  Ruby matches all 23 editable scripts. Only map109 geometry changed.
- Removing the two sofa-approach cells disconnects the boss from the entrance:
  the first hideout trainer cannot be bypassed through a gap in the rubbish.
- Ruby WASM with actual Essentials Pokemon/bag/SaveData objects checks guard
  cancellation, victory, minigame cancellation/success, real adapter astral
  loss with a pre-heal snapshot, save roundtrip, no minigame replay after boss
  loss, full-bag collection retry, unique reward, seller continuation and old
  defeated-boss saves. Battle outcomes and graphics are fixtures in this suite.
- Pure minigame tests verify walls, all three reachable nests, no duplicate
  release, preserved progress after contractions, and the three-nest exit gate.
- Native Linux mkxp-z 826929e / Ruby3.1, Mesa software OpenGL: actual player-touch
  guard trigger and trainer win; seated boss; full minigame using injected
  directional/interaction input; second actual trainer battle; cupboard route;
  one necklace; native save. The test uses a level45 Natu to isolate staging.
- After visual refinement, another native minigame run verifies completion
  and disposal of all scene sprites/bitmaps. A focused native route test checks
  the boss and player walking to the cupboard from four possible approach tiles.
- Screenshots and native result markers are in HideoutEvidence_082. The whole-map
  map_109_preview.png is an offline tile render, not an engine screenshot.
- Bible1.29 PDF section31 was rendered and visually inspected. Guide2.27 and
  source instructions match the new quest state and rebuild ownership.

## Compatibility and limits

Map magic26092501 refreshes cached event data. An additive per-quest revision
relocates a saved map109 player to the clear entrance once. Old wins/completed
quests, real companion identities, inventory and save directory are preserved.
The minigame changes no real Pokemon, PP, status or items. Its cancel path has no
penalty; a trainer loss still uses the existing astral system. Existing trainer
rosters, other maps and regional species are unchanged.

Mac package0.8.2/build36 retains the same native runtime and fontHeightReporting1.
No native Mac execution here. Audio used a null output during automated Linux
checks, so audible playback and human difficulty/atmosphere assessment remain
playtest tasks. A completed necklace quest does not replay on Continue; use a
separate new journey to play the entire revised scene. No later Abyss/sabre lore
was implemented or revealed.
